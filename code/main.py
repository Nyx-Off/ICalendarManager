from icalendar import Calendar
import datetime
import requests
import json
import pytz  # Ajouté pour gérer les fuseaux horaires


# Classe pour représenter un événement
class Event:
    def __init__(self, summary, start, end, location=None):  # Ajout de 'location'
        self.summary = summary
        self.start = start
        self.end = end
        self.location = location  # Nouveau champ pour le lieu

    def __eq__(self, other):
        return (self.summary == other.summary and 
                self.start == other.start and 
                self.end == other.end and 
                self.location == other.location)

    def to_json(self):
        return {
            'summary': self.summary,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'location': self.location  # Inclure le lieu dans le JSON
        }

    @staticmethod
    def from_json(data):
        return Event(
            data['summary'],
            datetime.datetime.fromisoformat(data['start']),
            datetime.datetime.fromisoformat(data['end']),
            data.get('location')  # Récupérer le lieu s'il est disponible
        )

# Classe pour gérer le calendrier ICalendar
class CalendarManager:
    def __init__(self, url):
        self.url = url
        self.last_events = []
        
    def save_events_to_json(self, events, filename='events.json'):
        with open(filename, 'w') as file:
            json.dump([event.to_json() for event in events], file, indent=4)

    def load_events_from_json(self, filename='events.json'):
        with open(filename, 'r') as file:
            data = json.load(file)
            return [Event.from_json(event) for event in data]

    def get_calendar_data(self):
        response = requests.get(self.url)
        return Calendar.from_ical(response.content)

    def get_events_next_week(self):
        calendar = self.get_calendar_data()

        now = datetime.datetime.now(pytz.utc)
        start_next_week = now + datetime.timedelta(days=7-now.weekday())
        end_next_week = start_next_week + datetime.timedelta(days=7)

        events_next_week = []
        for component in calendar.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end = component.get('dtend').dt

                if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:
                    start = pytz.utc.localize(start)
                if end.tzinfo is None or end.tzinfo.utcoffset(end) is None:
                    end = pytz.utc.localize(end)

                location = component.get('location')
                if location:
                    location = str(location)

                # Vérifiez si l'événement est dans la semaine suivante
                if start_next_week <= start < end_next_week:
                    location = component.get('location')
                    location = str(location) if location else None
                    events_next_week.append(Event(component.get('summary'), start, end, location))
        return events_next_week

    def check_for_changes(self, filename='events.json'):
        current_events = self.get_events_next_week()
        try:
            last_events = self.load_events_from_json(filename)
        except FileNotFoundError:
            last_events = []

        added = [event for event in current_events if event not in last_events]
        removed = [event for event in last_events if event not in current_events]

        self.save_events_to_json(current_events, filename)  # Sauvegarde des événements actuels
        return added, removed
    
    def has_sent_today(self, filename='last_sent.json'):
        try:
            with open(filename, 'r') as file:
                last_sent = datetime.datetime.fromisoformat(json.load(file)['last_sent'])
                return last_sent.date() == datetime.datetime.now().date()
        except (FileNotFoundError, ValueError, KeyError):
            return False

    def update_last_sent(self, filename='last_sent.json'):
        with open(filename, 'w') as file:
            json.dump({'last_sent': datetime.datetime.now().isoformat()}, file)

# Classe pour gérer le bot Discord
class DiscordBot:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, message):
        data = {
            "content": message,
            "username": "Calendrier Bot"
        }
        requests.post(self.webhook_url, json=data)

    def format_events_message(self, events):
        message = "Emploi du temps pour la semaine prochaine:\n"
        for event in events:
            location_str = f" en {event.location}" if event.location else ""
            message += f"{event.summary} - {event.start.strftime('%Y-%m-%d %H:%M')} à {event.end.strftime('%Y-%m-%d %H:%M')}{location_str}\n"
        return message

    def format_change_alert(self, added, removed):
        message = "Changements dans l'emploi du temps:\n"
        for event in added:
            location_str = f" en {event.location}" if event.location else ""
            message += f"Ajouté: {event.summary} - {event.start.strftime('%Y-%m-%d %H:%M')} à {event.end.strftime('%Y-%m-%d %H:%M')}{location_str}\n"
        for event in removed:
            location_str = f" en {event.location}" if event.location else ""
            message += f"Supprimé: {event.summary} - {event.start.strftime('%Y-%m-%d %H:%M')} à {event.end.strftime('%Y-%m-%d %H:%M')}{location_str}\n"
        return message

# Fonction principale
def main():
    # Utiliser les URL fournies
    calendar_manager = CalendarManager('https://formations.cci-paris-idf.fr/IntNum/index.php/planning/ical/F7C58369-952C-4F85-BEE0-883FC5F3BF10/')
    discord_bot = DiscordBot('https://discord.com/api/webhooks/1106142739579555891/PhrVe8EPN7wweNuUexTjrxgf6wT1MTPySD8FMcmWC0nRZBPpVfeerV_UHpHuMvyl4p0T')

    added, removed = calendar_manager.check_for_changes()
    if added or removed:
        alert_message = discord_bot.format_change_alert(added, removed)
        discord_bot.send_message(alert_message)

    if datetime.datetime.now().weekday() == 3:  # Samedi
        if not calendar_manager.has_sent_today():
            events_next_week = calendar_manager.get_events_next_week()
            schedule_message = discord_bot.format_events_message(events_next_week)
            discord_bot.send_message(schedule_message)
            calendar_manager.update_last_sent()

if __name__ == "__main__":
    main()

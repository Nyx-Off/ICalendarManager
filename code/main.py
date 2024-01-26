from icalendar import Calendar
import datetime
import requests
import json
import pytz
import locale

ICAL_URL = 'Ical URL'
DISCORD_WEBHOOK_URL = 'Discord Webhook URL'


locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# Classe pour représenter un événement
class Event:
    def __init__(self, summary, start, end, location=None):  
        self.summary = summary
        self.start = start
        self.end = end
        self.location = location  

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
            'location': self.location 
        }

    @staticmethod
    def from_json(data):
        return Event(
            data['summary'],
            datetime.datetime.fromisoformat(data['start']),
            datetime.datetime.fromisoformat(data['end']),
            data.get('location') 
        )

# Classe pour gérer le calendrier ICalendar
class CalendarManager:
    def __init__(self):
        self.url = ICAL_URL
        self.last_events = []
        
    def save_events_to_json(self, week_events, filename='events.json'):
        with open(filename, 'w') as file:
            json_data = {date: [event.to_json() for event in events] for date, events in week_events.items()}
            json.dump(json_data, file, indent=4)

    def load_events_from_json(self, filename='events.json'):
        try:
            with open(filename, 'r') as file:
                file_content = file.read().strip()
                if not file_content:
                    return {}  
                data = json.loads(file_content)
                return {date: [Event.from_json(event) for event in events] for date, events in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}  

    def get_week_days(self, start_date):
            return [start_date + datetime.timedelta(days=i) for i in range(7)]

    def get_calendar_data(self):
        response = requests.get(self.url)
        return Calendar.from_ical(response.content)

    def get_events_next_week(self):
        calendar = self.get_calendar_data()

        local_timezone = pytz.timezone('Europe/Paris')

        now = datetime.datetime.now(pytz.utc)
        start_of_this_week = now - datetime.timedelta(days=now.weekday())
        start_of_next_week = start_of_this_week + datetime.timedelta(days=7)
        end_of_next_week = start_of_next_week + datetime.timedelta(days=7)

        week_events = {day.date().isoformat(): [] for day in self.get_week_days(start_of_this_week) + self.get_week_days(start_of_next_week)}

        for component in calendar.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                end = component.get('dtend').dt

                if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:
                    start = pytz.utc.localize(start).astimezone(local_timezone)
                else:
                    start = start.astimezone(local_timezone)

                if end.tzinfo is None or end.tzinfo.utcoffset(end) is None:
                    end = pytz.utc.localize(end).astimezone(local_timezone)
                else:
                    end = end.astimezone(local_timezone)

                location = component.get('location')
                if location:
                    location = str(location)

                if start_of_this_week.date() <= start.date() < end_of_next_week.date():
                    day_key = start.date().isoformat()
                    week_events[day_key].append(Event(component.get('summary'), start, end, location))

        return week_events
    

    def check_for_changes(self, filename='events.json'):
        current_events = self.get_events_next_week()
        try:
            last_events = self.load_events_from_json(filename)
        except FileNotFoundError:
            last_events = {}

        added = {}
        removed = {}

        for date, events in current_events.items():
            last_events_for_date = last_events.get(date, [])
            added[date] = [event for event in events if event not in last_events_for_date]
            removed[date] = [event for event in last_events_for_date if event not in events]

        self.save_events_to_json(current_events, filename)  
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
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL


    def send_message(self, message):
        data = {
            "content": message,
            "username": "Calendrier Bot"
        }
        requests.post(self.webhook_url, json=data)

    def format_events_message(self, week_events):
        message = "Emploi du temps pour la semaine prochaine:\n"
        for date, events in week_events.items():
            if events:  
                message += f"\n{date}:\n"
                for event in events:
                    location_str = f" en {event.location}" if event.location else ""
                    message += f"  {event.summary} - {event.start.strftime('%H:%M')} à {event.end.strftime('%H:%M')}{location_str}\n"
        return message

    def format_change_alert(self, added, removed):
        embeds = []

        # Pour les événements ajoutés (vert)
        for date, events in added.items():
            if events:
                embed = {
                    "title": f"Ajouté le {datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A %d %B %Y')}",
                    "color": 65280,  # Vert
                    "fields": []
                }
                for event in events:
                    field = {
                        "name": event.summary,
                        "value": f"{event.start.strftime('%H:%M')} à {event.end.strftime('%H:%M')}\n" +
                                 (f"en salle : {event.location}" if event.location else ""),
                        "inline": True
                    }
                    embed["fields"].append(field)
                embeds.append(embed)

        # Pour les événements supprimés (rouge)
        for date, events in removed.items():
            if events:
                embed = {
                    "title": f"Supprimé le {datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A %d %B %Y')}",
                    "color": 16711680,  # Rouge
                    "fields": []
                }
                for event in events:
                    field = {
                        "name": event.summary,
                        "value": f"{event.start.strftime('%H:%M')} à {event.end.strftime('%H:%M')}\n" +
                                 (f"en salle : {event.location}" if event.location else ""),
                        "inline": True
                    }
                    embed["fields"].append(field)
                embeds.append(embed)

        data = {
            "content": "@everyone Changements dans l'emploi du temps",
            "embeds": embeds
        }
        requests.post(self.webhook_url, json=data)
    
    def send_embed_message(self, week_events):
        embeds = []
        for date, events in week_events.items():
            if events:
                embed = {
                    "title": f"{datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A %d %B %Y')}",
                    "color": 52479,
                    "fields": []
                }
                for event in events:
                    field = {
                        "name": event.summary,
                        "value": f"{event.start.strftime('%H:%M')} à {event.end.strftime('%H:%M')}\n" +
                                 (f"en salle : {event.location}" if event.location else ""),
                        "inline": True
                    }
                    embed["fields"].append(field)
                embeds.append(embed)

        data = {
            "content": "@everyone voici l'emploi du temps de la semaine",
            "embeds": embeds
        }
        requests.post(self.webhook_url, json=data)

# Fonction principale
def main():
    # Utiliser les URL fournies
    calendar_manager = CalendarManager()
    discord_bot = DiscordBot()
    
    added, removed = calendar_manager.check_for_changes()
    if any(added.values()) or any(removed.values()):
        alert_message = discord_bot.format_change_alert(added, removed)
        discord_bot.send_message(alert_message)

    if datetime.datetime.now().weekday() == 4:  # Samedi
        if not calendar_manager.has_sent_today():
            week_events = calendar_manager.get_events_next_week()
            discord_bot.send_embed_message(week_events)
            calendar_manager.update_last_sent()

if __name__ == "__main__":
    main()

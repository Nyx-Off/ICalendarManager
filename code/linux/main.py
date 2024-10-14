import datetime
import locale
import requests
import pytz
from icalendar import Calendar
import os
import json

ICAL_URL = ''
DISCORD_WEBHOOK_URL = ''
EVENTS_DIR = 'events'
ICAL_FILE_PATH = os.path.join(EVENTS_DIR, 'calendar.ics')
SENT_EVENTS_FILE = os.path.join(EVENTS_DIR, 'sent_events.json')
LOG_FILE = os.path.join(EVENTS_DIR, 'execution.log')

# Fonction pour télécharger les événements du calendrier
def download_calendar():
    if not os.path.exists(EVENTS_DIR):
        os.makedirs(EVENTS_DIR)
    response = requests.get(ICAL_URL)
    if response.status_code == 200:
        with open(ICAL_FILE_PATH, 'wb') as ical_file:
            ical_file.write(response.content)
        with open(ICAL_FILE_PATH, 'rb') as ical_file:
            return Calendar.from_ical(ical_file.read())
    else:
        raise Exception("Erreur lors du téléchargement du calendrier : Statut " + str(response.status_code))

# Fonction pour extraire les événements de la semaine
def get_week_events(calendar, start_date, end_date):
    week_events = {}
    for component in calendar.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt
            end = component.get('dtend').dt
            summary = component.get('summary')
            location = component.get('location')

            # Convertir en timezone locale si nécessaire
            local_timezone = pytz.timezone('Europe/Paris')
            if start.tzinfo is None:
                start = pytz.utc.localize(start).astimezone(local_timezone)
                end = pytz.utc.localize(end).astimezone(local_timezone)
            else:
                start = start.astimezone(local_timezone)
                end = end.astimezone(local_timezone)

            if start_date <= start.date() < end_date:
                day_key = start.date().isoformat()
                if day_key not in week_events:
                    week_events[day_key] = []
                week_events[day_key].append({
                    'summary': summary,
                    'start': start,
                    'end': end,
                    'location': location
                })
    return week_events

# Fonction pour comparer les événements (ajoutés/supprimés)
def compare_events(old_events, new_events):
    if isinstance(old_events, dict) and old_events.get('status') == 'no_events_this_week':
        old_events = {}
    old_set = {frozenset(event.items()) for events in old_events.values() if isinstance(events, list) for event in events}
    new_set = {frozenset(event.items()) for events in new_events.values() if isinstance(events, list) for event in events}

    added = [dict(event) for event in new_set - old_set]
    removed = [dict(event) for event in old_set - new_set]

    return added, removed

# Fonction pour envoyer des messages sur Discord
def send_discord_message(content, embeds=None):
    data = {
        "content": content,
    }
    if embeds:
        data["embeds"] = embeds
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        log_message(f"Erreur lors de l'envoi du message Discord : {response.status_code} - {response.text}")

# Fonction pour créer des embeds pour Discord
def create_embeds_for_events(events):
    embeds = []
    for date, day_events in events.items():
        if day_events:
            embed = {
                "title": f"📅 {datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A %d %B %Y')}",
                "color": 5814783,
                "fields": []
            }
            for event in day_events:
                location_str = f" en {event['location']}" if event['location'] else ""
                field = {
                    "name": event['summary'],
                    "value": f"De {event['start'].strftime('%H:%M')} à {event['end'].strftime('%H:%M')}{location_str}",
                    "inline": False
                }
                embed["fields"].append(field)
            embeds.append(embed)
    return embeds

# Fonction pour charger les événements envoyés
def load_sent_events():
    if os.path.exists(SENT_EVENTS_FILE):
        try:
            with open(SENT_EVENTS_FILE, 'r') as file:
                serialized_events = json.load(file)

            deserialized_events = {}
            for date, day_events in serialized_events.items():
                deserialized_day_events = []
                for event in day_events:
                    deserialized_event = {
                        'summary': event['summary'],
                        'start': datetime.datetime.fromisoformat(event['start']),
                        'end': datetime.datetime.fromisoformat(event['end']),
                        'location': event['location']
                    }
                    deserialized_day_events.append(deserialized_event)
                deserialized_events[date] = deserialized_day_events

            return deserialized_events
        except (json.JSONDecodeError, ValueError):
            # If file is empty or corrupted, return an empty dict and log the error
            log_message("Warning: Could not load sent events, the file might be corrupted.")
            return {}
    return {}


# Fonction pour sauvegarder les événements envoyés
def save_sent_events(events):
    serialized_events = {}
    for date, day_events in events.items():
        serialized_day_events = []
        for event in day_events:
            serialized_event = {
                'summary': event['summary'],
                'start': event['start'].isoformat(),
                'end': event['end'].isoformat(),
                'location': event['location']
            }
            serialized_day_events.append(serialized_event)
        serialized_events[date] = serialized_day_events

    with open(SENT_EVENTS_FILE, 'w') as file:
        json.dump(serialized_events, file, indent=4)

# Fonction pour écrire un message dans le fichier de log
def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

# Fonction principale
def main():
    # Définir la locale en français (Debian)
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        log_message("Locale fr_FR.UTF-8 non disponible, utilisation de la locale par défaut.")
        locale.setlocale(locale.LC_TIME, '')

    try:
        # Télécharger les événements du calendrier
        calendar = download_calendar()
    except Exception as e:
        log_message(str(e))
        return

    # Définir la période de la semaine actuelle ou prochaine
    today = datetime.datetime.now().date()
    if today.weekday() == 6:  # Ne rien envoyer si on est dimanche
        log_message("Aucun envoi le dimanche.")
        return

    if today.weekday() == 5:  # À partir de samedi, envoyer l'emploi du temps de la semaine prochaine
        start_of_week = today + datetime.timedelta(days=(7 - today.weekday()))
    else:
        start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=7)

    # Obtenir les événements de la semaine
    new_events = get_week_events(calendar, start_of_week, end_of_week)

    # Charger les événements précédemment envoyés
    sent_events = load_sent_events()

    # Comparer les événements et éviter les doublons
    added, removed = compare_events(sent_events, new_events)

    # Envoyer les modifications sur Discord
    if added or removed:
        added_embeds = create_embeds_for_events({date: [event for event in new_events.get(date, []) if dict(event) in added] for date in new_events})
        removed_embeds = create_embeds_for_events({date: [event for event in sent_events.get(date, []) if dict(event) in removed] for date in sent_events})
        if added_embeds:
            send_discord_message("🏢 Événements ajoutés :", added_embeds)
            log_message("Événements ajoutés envoyés sur Discord.")
        if removed_embeds:
            send_discord_message("❌ Événements supprimés :", removed_embeds)
            log_message("Événements supprimés envoyés sur Discord.")
        # Sauvegarder les nouveaux événements après envoi
        save_sent_events(new_events)
    elif not new_events and ('status' not in sent_events or sent_events.get('status') != 'no_events_this_week'):
        send_discord_message("ℹ️ Pas de cours cette semaine.")
        save_sent_events({'status': 'no_events_this_week'})
        log_message("Message 'Pas de cours cette semaine' envoyé sur Discord.")
    else:
        log_message("Aucun changement dans les événements de la semaine.")

if __name__ == "__main__":
    main()

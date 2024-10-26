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

# Les fonctions download_calendar, create_embeds_for_events, send_discord_message et log_message restent inchangées...

def get_week_events(calendar, start_date, end_date):
    week_events = {}
    for component in calendar.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt
            end = component.get('dtend').dt
            summary = component.get('summary')
            location = component.get('location')

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
                    'location': location,
                    'week': start_date.isocalendar()[1]
                })
    return week_events

def load_sent_events():
    if os.path.exists(SENT_EVENTS_FILE):
        try:
            with open(SENT_EVENTS_FILE, 'r') as file:
                data = json.load(file)
                
            events_by_week = data.get('events_by_week', {})
            notifications = data.get('notifications', {})
            
            # Désérialisation des dates
            for week_num, week_events in events_by_week.items():
                for date, day_events in week_events.items():
                    for event in day_events:
                        event['start'] = datetime.datetime.fromisoformat(event['start'])
                        event['end'] = datetime.datetime.fromisoformat(event['end'])
            
            return {
                'events_by_week': events_by_week,
                'notifications': notifications
            }
        except Exception as e:
            log_message(f"Erreur lors du chargement des événements : {str(e)}")
            return {'events_by_week': {}, 'notifications': {}}
    return {'events_by_week': {}, 'notifications': {}}

def save_sent_events(events, week_number, notifications):
    data = load_sent_events()
    events_by_week = data['events_by_week']
    
    # Sérialiser les nouveaux événements
    serialized_events = {}
    for date, day_events in events.items():
        serialized_day_events = []
        for event in day_events:
            serialized_event = {
                'summary': event['summary'],
                'start': event['start'].isoformat(),
                'end': event['end'].isoformat(),
                'location': event['location'],
                'week': event.get('week', week_number)
            }
            serialized_day_events.append(serialized_event)
        serialized_events[date] = serialized_day_events
    
    # Mettre à jour les événements et notifications de la semaine
    events_by_week[str(week_number)] = serialized_events
    data['notifications'].update(notifications)
    
    # Nettoyer les anciennes semaines (garder seulement les 3 dernières)
    week_numbers = sorted([int(w) for w in events_by_week.keys()])
    while len(week_numbers) > 3:
        oldest_week = str(week_numbers.pop(0))
        events_by_week.pop(oldest_week)
        
        # Nettoyer aussi les anciennes notifications
        keys_to_remove = [key for key in data['notifications'] if key.startswith(f"week_{oldest_week}_")]
        for key in keys_to_remove:
            data['notifications'].pop(key, None)
    
    # Sauvegarder
    with open(SENT_EVENTS_FILE, 'w') as file:
        json.dump({
            'events_by_week': events_by_week,
            'notifications': data['notifications']
        }, file, indent=4)

def compare_events(old_events, new_events, current_week):
    if not old_events or not old_events.get('events_by_week'):
        return new_events.values(), []

    old_week_events = old_events['events_by_week'].get(str(current_week), {})
    
    # Créer des ensembles d'événements pour la comparaison
    old_set = {
        frozenset((k, str(v)) for k, v in event.items() if k != 'week')
        for events in old_week_events.values()
        for event in events
    }
    new_set = {
        frozenset((k, str(v)) for k, v in event.items() if k != 'week')
        for events in new_events.values()
        for event in events
    }

    # Identifier les changements
    added = [
        dict(event) for events in new_events.values()
        for event in events
        if frozenset((k, str(v)) for k, v in event.items() if k != 'week') not in old_set
    ]
    removed = [
        dict(event) for events in old_week_events.values()
        for event in events
        if frozenset((k, str(v)) for k, v in event.items() if k != 'week') not in new_set
    ]

    return added, removed

def has_been_notified(notifications, week_number, notification_type):
    """Vérifie si une notification a déjà été envoyée"""
    key = f"week_{week_number}_{notification_type}"
    return notifications.get(key, False)

def mark_as_notified(notifications, week_number, notification_type):
    """Marque une notification comme envoyée"""
    key = f"week_{week_number}_{notification_type}"
    notifications[key] = True
    return notifications

def main():
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        log_message("Locale fr_FR.UTF-8 non disponible, utilisation de la locale par défaut.")
        locale.setlocale(locale.LC_TIME, '')

    try:
        calendar = download_calendar()
    except Exception as e:
        log_message(str(e))
        return

    today = datetime.datetime.now().date()
    if today.weekday() == 6:  # Dimanche
        log_message("Aucun envoi le dimanche.")
        return

    # Déterminer la semaine à traiter
    if today.weekday() == 5:  # Samedi
        start_of_week = today + datetime.timedelta(days=2)
    else:
        start_of_week = today - datetime.timedelta(days=today.weekday())
    
    end_of_week = start_of_week + datetime.timedelta(days=7)
    current_week = start_of_week.isocalendar()[1]

    # Charger les données
    stored_data = load_sent_events()
    notifications = stored_data.get('notifications', {})

    # Obtenir les événements actuels
    new_events = get_week_events(calendar, start_of_week, end_of_week)
    
    # Comparer les événements
    added, removed = compare_events(stored_data, new_events, current_week)

    # Gérer les notifications
    should_save = False

    if added or removed:
        # Il y a des changements dans le calendrier
        added_by_date = {}
        removed_by_date = {}
        
        for event in added:
            date = event['start'].date().isoformat()
            if date not in added_by_date:
                added_by_date[date] = []
            added_by_date[date].append(event)
            
        for event in removed:
            date = event['start'].date().isoformat()
            if date not in removed_by_date:
                removed_by_date[date] = []
            removed_by_date[date].append(event)

        if added_by_date:
            added_embeds = create_embeds_for_events(added_by_date)
            send_discord_message("🏢 Événements ajoutés pour la semaine " + str(current_week) + " :", added_embeds)
            log_message(f"Événements ajoutés envoyés pour la semaine {current_week}.")
            
        if removed_by_date:
            removed_embeds = create_embeds_for_events(removed_by_date)
            send_discord_message("❌ Événements supprimés de la semaine " + str(current_week) + " :", removed_embeds)
            log_message(f"Événements supprimés envoyés pour la semaine {current_week}.")
        
        should_save = True
        notifications = mark_as_notified(notifications, current_week, 'changes')
        
    elif not new_events and not has_been_notified(notifications, current_week, 'no_events'):
        # Pas d'événements cette semaine et on ne l'a pas encore notifié
        send_discord_message(f"ℹ️ Pas de cours pour la semaine {current_week}.")
        log_message(f"Message 'Pas de cours cette semaine' envoyé pour la semaine {current_week}.")
        should_save = True
        notifications = mark_as_notified(notifications, current_week, 'no_events')
    else:
        log_message(f"Aucun nouveau changement à notifier pour la semaine {current_week}.")

    if should_save:
        save_sent_events(new_events, current_week, notifications)

if __name__ == "__main__":
    main()

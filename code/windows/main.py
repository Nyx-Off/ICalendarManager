#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import locale
import requests
import pytz
from icalendar import Calendar
import os
import json

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
EVENTS_DIR = os.path.join(BASE_DIR, 'events')
ICAL_FILE_PATH = os.path.join(EVENTS_DIR, 'calendar.ics')
SENT_EVENTS_FILE = os.path.join(EVENTS_DIR, 'sent_events.json')

# Remplir ces constantes avec les URL appropriées
ICAL_URL = ''  # À renseigner
DISCORD_WEBHOOK_URL = ''  # À renseigner

def ensure_events_dir():
    """S'assure que le dossier 'events' existe."""
    if not os.path.exists(EVENTS_DIR):
        os.makedirs(EVENTS_DIR)

def download_calendar():
    """Télécharge le calendrier depuis l'URL ICAL et retourne un objet Calendar."""
    ensure_events_dir()
    response = requests.get(ICAL_URL)
    if response.status_code == 200:
        with open(ICAL_FILE_PATH, 'wb') as ical_file:
            ical_file.write(response.content)
        with open(ICAL_FILE_PATH, 'rb') as ical_file:
            return Calendar.from_ical(ical_file.read())
    else:
        raise Exception("Erreur lors du téléchargement du calendrier : Statut " + str(response.status_code))

def get_week_events(calendar, start_date, end_date):
    """Extrait les événements de la semaine comprise entre start_date et end_date."""
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
                week_events.setdefault(day_key, []).append({
                    'summary': summary,
                    'start': start,
                    'end': end,
                    'location': location
                })
    return week_events

def compare_events(old_events, new_events):
    """
    Compare les événements anciens et nouveaux pour identifier les ajouts et suppressions.
    Si old_events contient un statut indiquant qu'il n'y avait pas d'événements, on le réinitialise.
    """
    if isinstance(old_events, dict) and old_events.get('status') == 'no_events_this_week':
        old_events = {}
    old_set = {frozenset(event.items()) for events in old_events.values() if isinstance(events, list) for event in events}
    new_set = {frozenset(event.items()) for events in new_events.values() if isinstance(events, list) for event in events}

    added = [dict(event) for event in new_set - old_set]
    removed = [dict(event) for event in old_set - new_set]

    return added, removed

def send_discord_message(content, embeds=None):
    """Envoie un message sur Discord via webhook."""
    data = { "content": content }
    if embeds:
        data["embeds"] = embeds
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Erreur lors de l'envoi du message Discord : {response.status_code} - {response.text}")

def create_embeds_for_events(events):
    """Crée des embeds à partir d'un dictionnaire d'événements groupés par date pour Discord."""
    embeds = []
    for date, day_events in events.items():
        if day_events:
            try:
                formatted_date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A %d %B %Y')
            except Exception:
                formatted_date = date
            embed = {
                "title": f"📅 {formatted_date}",
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

def load_sent_events():
    """Charge les événements précédemment envoyés depuis le fichier JSON."""
    ensure_events_dir()
    if os.path.exists(SENT_EVENTS_FILE):
        try:
            with open(SENT_EVENTS_FILE, 'r') as file:
                serialized_events = json.load(file)

            deserialized_events = {}
            for key, value in serialized_events.items():
                if key == 'status':
                    deserialized_events[key] = value
                else:
                    deserialized_day_events = []
                    for event in value:
                        deserialized_day_events.append({
                            'summary': event['summary'],
                            'start': datetime.datetime.fromisoformat(event['start']),
                            'end': datetime.datetime.fromisoformat(event['end']),
                            'location': event['location']
                        })
                    deserialized_events[key] = deserialized_day_events
            return deserialized_events
        except (json.JSONDecodeError, ValueError):
            print("Warning: Impossible de charger les événements envoyés, le fichier est peut-être corrompu.")
            return {}
    return {}

def save_sent_events(events):
    """Sauvegarde les événements dans un fichier JSON."""
    ensure_events_dir()
    serialized_events = {}
    for key, value in events.items():
        if key == 'status':
            serialized_events[key] = value
        else:
            serialized_day_events = []
            for event in value:
                serialized_day_events.append({
                    'summary': event['summary'],
                    'start': event['start'].isoformat(),
                    'end': event['end'].isoformat(),
                    'location': event['location']
                })
            serialized_events[key] = serialized_day_events

    with open(SENT_EVENTS_FILE, 'w') as file:
        json.dump(serialized_events, file, indent=4)

def main():
    ensure_events_dir()
    # Définir la locale en français
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        print("Locale fr_FR.UTF-8 non disponible, utilisation de la locale par défaut.")
        locale.setlocale(locale.LC_TIME, '')

    try:
        calendar = download_calendar()
    except Exception as e:
        print(e)
        return

    today = datetime.datetime.now().date()
    if today.weekday() == 6:  # Aucun envoi le dimanche
        print("Aucun envoi le dimanche.")
        return

    # Si c'est samedi, envoyer l'emploi du temps de la semaine prochaine, sinon celui de la semaine en cours
    if today.weekday() == 5:
        start_of_week = today + datetime.timedelta(days=(7 - today.weekday()))
    else:
        start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=7)

    new_events = get_week_events(calendar, start_of_week, end_of_week)
    sent_events = load_sent_events()

    added, removed = compare_events(sent_events, new_events)

    if added or removed:
        # Préparer les événements ajoutés par date
        added_set = {frozenset(e.items()) for e in added}
        added_by_date = {
            date: [event for event in new_events.get(date, [])
                   if frozenset(event.items()) in added_set]
            for date in new_events
        }
        # Préparer les événements supprimés par date (en ignorant la clé 'status' le cas échéant)
        removed_set = {frozenset(e.items()) for e in removed}
        removed_by_date = {
            date: [event for event in sent_events.get(date, [])
                   if frozenset(event.items()) in removed_set]
            for date in sent_events if date != 'status'
        }
        if added_by_date:
            added_embeds = create_embeds_for_events(added_by_date)
            send_discord_message("🏢 Événements ajoutés :", added_embeds)
        if removed_by_date:
            removed_embeds = create_embeds_for_events(removed_by_date)
            send_discord_message("❌ Événements supprimés :", removed_embeds)
        save_sent_events(new_events)
    elif not new_events and (sent_events.get('status') != 'no_events_this_week'):
        send_discord_message("ℹ️ Pas de cours cette semaine.")
        save_sent_events({'status': 'no_events_this_week'})
    else:
        print("Aucun changement dans les événements de la semaine.")

if __name__ == "__main__":
    main()

<h1 align="center"> ICalendarManager 

![Static Badge](https://img.shields.io/badge/Contributeur-1-brightgreen?style=flat&logo=clubhouse&logoColor=white&logoSize=auto) 
![License](https://img.shields.io/github/license/Nyx-Off/AceVenturaTheGame) 
![Static Badge](https://img.shields.io/badge/Python-black?style=plastic&logo=python&logoColor=white&logoSize=auto&color=yellow)
</h1>

<div align="center">
    <img class="Logo" src="https://raw.githubusercontent.com/Nyx-Off/ICalendarManager/main/logo500x500.png" width="500" />
</div>

## Contexte du Projet

J'ai créé ICalendarManager pour récupérer les cours que j'ai et les partager avec ma classe sur Discord. Il permet également d'être notifié en cas de changement d'emploi du temps, ce qui n'est pas une fonctionnalité native de notre plateforme d'emploi du temps. L'idée est de simplifier la communication et de réduire les surprises liées aux changements de dernière minute.

## Fonctionnalités

- 🚀 **Téléchargement Automatique du Calendrier** : Le script télécharge automatiquement le fichier ICS contenant l'emploi du temps à partir d'une URL spécifiée.
- 📢 **Notifications Discord** : Envoie des notifications Discord contenant l'emploi du temps de la semaine actuelle. À partir de samedi, il envoie l'emploi du temps de la semaine suivante.
- 🔄 **Suivi des Modifications** : Enregistre l'emploi du temps envoyé dans un fichier JSON pour comparer les semaines et éviter les envois redondants. Si des modifications sont détectées (ajouts ou suppressions), seuls les changements sont notifiés.
- 🚫 **Gestion des Semaines Sans Cours** : Si aucune session n'est prévue pour une semaine donnée, le script envoie une notification "Pas de cours cette semaine" et évite de renvoyer le même message.

## Prérequis

- Python 3.x
- Bibliothèques Python : `icalendar`, `requests`, `pytz`

Pour installer les bibliothèques nécessaires, exécutez la commande suivante :
```sh
pip install icalendar requests pytz
```

## Installation

1. Clonez ce dépôt GitHub :
   ```sh
   git clone <url_du_dépôt>
   ```
2. Naviguez jusqu'au répertoire du projet :
   ```sh
   cd ICalendarManager
   ```

## Configuration

Modifiez les valeurs suivantes dans le script pour qu'elles correspondent à votre utilisation :

- `ICAL_URL` : L'URL du fichier iCalendar à télécharger.
- `DISCORD_WEBHOOK_URL` : L'URL du webhook Discord où envoyer les notifications.

## Utilisation

Pour lancer le script, exécutez simplement :
```sh
python main.py
```
Le script est conçu pour être exécuté régulièrement. Pour automatiser l'exécution, vous pouvez l'intégrer dans le Planificateur de Tâches de Windows ou utiliser cron sur Linux.

### Automatisation sous Windows
1. Ouvrez le **Planificateur de Tâches**.
2. Créez une nouvelle tâche de base.
3. Configurez l'exécution du script `main.py` à l'heure souhaitée.

### Automatisation sous Linux (Debian)
Pour automatiser l'exécution du script toutes les heures sur un système Linux, créez une tâche cron :

1. Créez un environnement virtuel pour le projet :
   ```sh
   python3 -m venv venv
   ```
2. Activez l'environnement virtuel :
   ```sh
   source venv/bin/activate
   ```
3. Installez les dépendances :
   ```sh
   pip install icalendar requests pytz
   ```
4. Ajoutez une tâche cron pour exécuter le script toutes les heures :
   ```sh
   crontab -e
   ```
   Puis ajoutez la ligne suivante pour exécuter le script chaque heure :
   ```
   0 * * * * /usr/local/IcalendarManager/venv/bin/python /usr/local/IcalendarManager/main.py >> /usr/local/IcalendarManager/events/execution.log 2>&1
   ```
   Cette ligne exécute le script toutes les heures et enregistre la sortie dans le fichier `execution.log`.

## Structure du Projet

- `main.py` : Script principal qui gère le téléchargement, la comparaison et l'envoi des notifications.
- `events/` : Dossier où sont stockés le fichier `.ics` téléchargé et le fichier JSON contenant les événements envoyés.
- `sent_events.json` : Fichier JSON pour stocker les événements déjà envoyés afin d'éviter les doublons.
- `execution.log` : Fichier de log contenant les informations sur les exécutions du script.

## Améliorations Futures

- **Exécution continue** : Support pour une exécution continue sur un VPS via cron.
- **Interface utilisateur** : Ajout d'une interface graphique pour permettre une configuration plus simple.
- **Améliorations de la version Linux** : Meilleure intégration avec les outils Linux pour une utilisation plus fluide sur serveur.

## Contribuer
Si vous avez des suggestions, des améliorations ou si vous trouvez des bugs, n'hésitez pas à soumettre une pull request ou à ouvrir une issue.

## Licence
Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.

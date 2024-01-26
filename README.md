# ICalendarManager

## Aperçu
`ICalendarManager` est un script Python conçu pour intégrer des calendriers iCalendar avec Discord, permettant l'automatisation de l'envoi d'informations d'événements et de modifications d'événements via un bot Discord. Le script récupère des événements à partir d'une URL iCalendar, les compare avec les données précédemment enregistrées, et informe via Discord les événements ajoutés ou supprimés, ainsi que l'emploi du temps de la semaine à venir.

## Fonctionnalités
- Récupération d'événements depuis une URL iCalendar.
- Détection des modifications dans les événements (ajouts et suppressions).
- Envoi automatique de messages sur Discord pour informer des modifications et de l'emploi du temps hebdomadaire.

## Fonctionnement Détail

### Récupération et Analyse des Événements iCalendar
- **Récupération du Calendrier :** Le script effectue une requête HTTP à l'URL iCalendar spécifiée (`ICAL_URL`) et récupère les données du calendrier au format iCalendar.
- **Analyse des Données :** Les données récupérées sont ensuite analysées à l'aide de la bibliothèque `icalendar`, qui les convertit en une structure de données utilisable en Python.

### Gestion des Événements
- **Modélisation des Événements :** Chaque événement du calendrier est représenté par une instance de la classe `Event`, qui stocke des informations clés comme le résumé, le début, la fin et le lieu de l'événement.
- **Détection des Modifications :** À chaque exécution, le script compare les événements actuels avec ceux stockés dans le fichier `events.json` (enregistré localement). Cette comparaison permet d'identifier les nouveaux événements ajoutés et ceux qui ont été supprimés depuis la dernière vérification.

### Interaction avec Discord
- **Préparation des Messages :** Les informations sur les événements (ajoutés, supprimés, et la liste des événements de la semaine suivante) sont formatées en messages Discord.
- **Messages Embed :** Pour une présentation plus claire et structurée, les messages sont envoyés sous forme d'embeds Discord, qui permettent une meilleure mise en forme et une présentation visuelle améliorée.
- **Envoi via Webhook :** Les messages préparés sont envoyés au serveur Discord via un webhook (identifié par `DISCORD_WEBHOOK_URL`). Ce mécanisme permet une intégration transparente avec le serveur Discord.

### Gestion du Fuseau Horaire
- **Conversion des Heures :** Les heures des événements sont converties en heure locale (fuseau horaire `Europe/Paris`) pour faciliter leur interprétation par les utilisateurs finaux.

## Configuration
- **Configuration Initiale :** Modifiez les constantes `ICAL_URL` et `DISCORD_WEBHOOK_URL` en haut du script pour les adapter à votre calendrier iCalendar et à votre serveur Discord.

## Structure du Code
- **CalendarManager :** Cette classe gère la récupération, l'analyse et le suivi des événements iCalendar.
- **DiscordBot :** Cette classe est responsable de la communication avec le serveur Discord, en formatant et en envoyant les messages.
- **Fonction principale (`main`) :** Point d'entrée du script qui orchestre la récupération des événements, leur comparaison et l'envoi des notifications Discord.

## Utilisation
1. Clonez le dépôt ou téléchargez le script `ICalendarManager`.
2. Modifiez les variables `ICAL_URL` et `DISCORD_WEBHOOK_URL` avec vos propres informations.
3. Exécutez le script pour commencer à surveiller les modifications du calendrier et envoyer des mises à jour via Discord.

## Dépendances
- `icalendar`
- `datetime`
- `requests`
- `json`
- `pytz`
- `locale`

## Licence et Utilisation
- **Licence :** Le logiciel est distribué sous une licence spécifique, interdisant l'utilisation commerciale et exigeant la mention de l'auteur original pour toute redistribution ou modification. Consultez le fichier `LICENSE` pour plus de détails.

## Auteur et Contribution
- **Auteur :** Samy Bensalem - [GitHub](https://github.com/Nyx-Off/ICalendarManager/tree/main).
- **Contribution :** Les contributions au projet sont encouragées. Pour contribuer, vous pouvez soumettre des pull requests, des rapports de bugs, ou des suggestions d'amélioration.

## Contribution
Les contributions, telles que les rapports de bugs, les suggestions ou les pull requests, sont les bienvenues. Veuillez vous assurer de respecter les principes directeurs du projet.

## Remarques
Ce projet est destiné à être utilisé à des fins non commerciales. Toute utilisation commerciale est strictement interdite.

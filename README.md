<h1 align="center"> ICalendarManager </h3>

<div align="center">
    <img class="Logo" src="https://raw.githubusercontent.com/Nyx-Off/ICalendarManager/main/logo500x500.png" width="500" />
</div>

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

## Automatisation avec Cron

### Vue d'ensemble
Pour garantir que le script `ICalendarManager` s'exécute régulièrement et automatiquement, vous pouvez utiliser Cron, un planificateur de tâches sous Unix. Cron permet de configurer des tâches (connues sous le nom de cron jobs) pour s'exécuter à des intervalles de temps spécifiés. Cela est particulièrement utile pour surveiller constamment les modifications de votre calendrier iCalendar et envoyer des mises à jour via Discord sans intervention manuelle.

### Configuration de Cron Job
- **Accédez au Cron :** Ouvrez le cron avec la commande `crontab -e`. Cela ouvrira l'éditeur de cron où vous pouvez ajouter des tâches planifiées.
- **Ajouter un Cron Job :** Ajoutez une ligne suivant le format : 
  ```
  * * * * * /chemin/vers/python3 /chemin/vers/ICalendarManager/script.py
  ```
  Remplacez `/chemin/vers/python3` et `/chemin/vers/ICalendarManager/script.py` par les chemins appropriés sur votre système. La structure de temps `* * * * *` définit la fréquence d'exécution. Par exemple, `0 * * * *` exécutera le script à chaque heure pile.
- **Sauvegardez et Quittez :** Après avoir ajouté la ligne, sauvegardez le fichier et quittez l'éditeur. Le cron job est maintenant configuré et actif.

### Fréquence d'Exécution
- **Personnalisation :** Adaptez la structure de temps selon vos besoins. Par exemple, pour une exécution toutes les 6 heures, utilisez `0 */6 * * *`.
- **Précision :** Assurez-vous que la fréquence d'exécution correspond à vos besoins. Une fréquence trop élevée pourrait surcharger le serveur, tandis qu'une fréquence trop faible pourrait manquer des mises à jour importantes.

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

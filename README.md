# 📅 ICalendar Manager v2.0 - Version Web

![Version](https://img.shields.io/badge/version-2.0-blue)
![PHP](https://img.shields.io/badge/PHP-8.0%2B-purple)

Interface web moderne pour gérer et afficher automatiquement votre emploi du temps à partir d'un fichier ICS avec notifications Discord des changements.

## ✨ Fonctionnalités

- 🖥️ **Interface Web Moderne** : Design responsive, élégant et dark mode
- 📱 **Navigation Intuitive** : Parcourez les semaines précédentes et suivantes
- 🔄 **Mise à Jour Automatique** : Téléchargement et vérification toutes les heures via CRON
- 🔔 **Notifications Discord** : Alertes détaillées des changements (ajouts, modifications, suppressions)
- 📊 **Comparaison Intelligente** : Détection précise des modifications avec détails complets
- 💾 **Historique** : Conservation des 4 dernières semaines
- ⚡ **Actualisation Manuelle** : Bouton pour forcer la mise à jour
- 🎨 **Design Responsive** : Compatible mobile, tablette et desktop
- ⚙️ **Gestions des Erreurs** : Meilleure gestion des erreurs curl avec messages détaillés

## ⚙️ Corrections des Bugs

- Timeout augmenté à 60s (téléchargement)
- Timeout connexion défini à 30s
- Ajout ```CURLOPT_SSL_VERIFYPEER``` pour les certificats SSL 
- Détection du format ICS (avec ou sans Z) - Si pas de Z, les heures sont directement dans le timezone local

## 🚀 Installation

### Prérequis

- PHP 8.0 ou supérieur
- Serveur web (Apache, Nginx)
- Accès CRON
- Extension PHP cURL activée

### Étapes d'installation

1. **Télécharger le projet**
   ```bash
   cd /var/www/html
   # Placer les fichiers du projet ici
   ```

2. **Configurer les permissions**
   ```bash
   chmod 755 cron/check_updates.php
   chmod 775 data logs
   chown -R www-data:www-data data logs
   ```

3. **Configurer l'application**
   
   Éditez le fichier `api/config.php` et renseignez :
   
   ```php
   define('ICAL_URL', 'https://votre-url.com/calendar.ics');
   define('DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/...');
   ```

4. **Configurer le CRON**
   
   Ajoutez cette ligne à votre crontab pour vérifier les mises à jour toutes les heures :
   
   ```bash
   crontab -e
   ```
   
   Ajoutez :
   ```
   0 * * * * /usr/bin/php /var/www/html/icalendar-web/cron/check_updates.php >> /var/www/html/icalendar-web/logs/cron.log 2>&1
   ```

5. **Premier téléchargement**
   
   Pour le premier lancement :
   ```bash
   php cron/check_updates.php
   ```

## 📁 Structure du Projet

```
icalendar-web/
├── index.php                    # Page principale
├── api/
│   ├── config.php              # Configuration (URLs, chemins)
│   ├── calendar_manager.php    # Gestion du calendrier ICS
│   ├── get_events.php          # API : récupérer les événements
│   └── download_calendar.php   # API : télécharger le calendrier
├── cron/
│   └── check_updates.php       # Script CRON (vérification horaire)
├── data/
│   ├── calendar.ics            # Fichier ICS téléchargé
│   ├── events_history.json     # Historique des événements
│   └── .htaccess               # Protection du dossier
├── logs/
│   ├── application.log         # Logs de l'application
│   └── .htaccess               # Protection du dossier
├── assets/
│   ├── css/
│   │   └── style.css           # Styles CSS
│   └── js/
│       └── app.js              # Application JavaScript
└── README.md
```

## 🎯 Utilisation

### Interface Web

1. **Navigation** :
   - Boutons "← Semaine Précédente" / "Semaine Suivante →"
   - Bouton "Aujourd'hui" pour revenir à la semaine actuelle
   - Bouton "🔄 Actualiser" pour forcer le téléchargement

2. **Affichage** :
   - Chaque jour avec cours dans une carte
   - Événements avec : titre, horaires, lieu, description
   - Le jour actuel est mis en évidence

### Notifications Discord

Le système envoie automatiquement des notifications Discord quand il détecte :

**Événements Ajoutés** (vert) :
- Titre, date, horaires, lieu

**Événements Modifiés** (orange) :
- Détails précis des modifications

**Événements Supprimés** (rouge) :
- Informations de l'événement supprimé

## 🔒 Sécurité

- ✅ Dossiers `data/` et `logs/` protégés par `.htaccess`
- ✅ Validation des entrées utilisateur
- ✅ Échappement HTML pour éviter les XSS
- ✅ Headers CORS configurés
- ✅ Logs d'activité

## 🐛 Dépannage

### Le calendrier ne se charge pas

1. Vérifiez `ICAL_URL` dans `api/config.php`
2. Vérifiez les permissions sur `data/`
3. Consultez `logs/application.log`

### Les notifications Discord ne fonctionnent pas

1. Vérifiez `DISCORD_WEBHOOK_URL`
2. Testez le webhook manuellement
3. Consultez les logs

### Le CRON ne s'exécute pas

1. Vérifiez les permissions : `chmod +x cron/check_updates.php`
2. Testez manuellement : `php cron/check_updates.php`
3. Consultez `logs/cron.log`

## 📝 Licence

Ce projet utilise une licence MIT. Voir le fichier [LICENSE](LICENSE).

**Usage non commercial uniquement.**

## 👤 Auteur

**Samy Bensalem**
- GitHub : [@Nyx-Off](https://github.com/Nyx-Off)
- Site : [Samy BENSALEM](https://bensalemdev.fr/)
  
---

<div align="center">
  <b>Créé avec ❤️ par Samy Bensalem</b>
</div>

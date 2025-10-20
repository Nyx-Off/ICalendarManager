<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ICalendar Manager - Emploi du Temps</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <div class="container">
        <div class="header-top">
            <button id="darkModeToggle" class="dark-mode-toggle" title="Activer le mode sombre">🌙</button>
        </div>

        <header>
            <h1>📅 Emploi du Temps</h1>
            <p class="subtitle">Gestion automatique de votre calendrier ICS</p>
        </header>

        <div class="navigation">
            <button id="prevWeek" class="btn btn-nav">← Semaine Précédente</button>
            <div class="week-info">
                <h2 id="currentWeekTitle">Chargement...</h2>
                <p id="weekDates"></p>
            </div>
            <button id="nextWeek" class="btn btn-nav">Semaine Suivante →</button>
        </div>

        <div class="controls">
            <button id="todayBtn" class="btn btn-primary">Aujourd'hui</button>
            <button id="refreshBtn" class="btn btn-secondary">🔄 Actualiser</button>
            <div class="last-update">Dernière mise à jour : <span id="lastUpdate">-</span></div>
        </div>

        <div id="loadingSpinner" class="loading">
            <div class="spinner"></div>
            <p>Chargement des événements...</p>
        </div>

        <div id="errorMessage" class="error-message" style="display: none;"></div>
        <div id="calendarContainer" class="calendar-container"></div>
        <div id="noEvents" class="no-events" style="display: none;">
            <div class="no-events-icon">📭</div>
            <h3>Aucun cours cette semaine</h3>
            <p>Profitez de votre temps libre !</p>
        </div>

        <footer>
            <p>ICalendar Manager v2.0 - <a href="https://github.com/Nyx-Off/ICalendarManager" target="_blank">GitHub</a></p>
            <p class="author">Créé par Samy Bensalem</p>
        </footer>
    </div>
    <script src="assets/js/app.js"></script>
</body>
</html>
#!/usr/bin/env php
<?php
require_once dirname(__DIR__) . '/api/config.php';
require_once dirname(__DIR__) . '/api/calendar_manager.php';
logMessage("=== Début de la vérification automatique ===");
try {
    logMessage("Téléchargement du calendrier...");
    CalendarManager::downloadCalendar();
    $currentWeekData = CalendarManager::getWeekEvents(0);
    $weekNumber = $currentWeekData['weekNumber'];
    $newEvents = $currentWeekData['events'];
    $history = CalendarManager::loadHistory();
    if (isset($history[$weekNumber])) {
        $oldEvents = $history[$weekNumber]['events'];
        $changes = CalendarManager::compareEvents($oldEvents, $newEvents);
        $hasChanges = !empty($changes['added']) || !empty($changes['removed']) || !empty($changes['modified']);
        if ($hasChanges) {
            logMessage("Changements détectés pour la semaine {$weekNumber}");
            logMessage("- Ajoutés: " . count($changes['added']));
            logMessage("- Supprimés: " . count($changes['removed']));
            logMessage("- Modifiés: " . count($changes['modified']));
            CalendarManager::sendDiscordNotification($changes, $weekNumber);
            CalendarManager::saveHistory($weekNumber, $newEvents);
            logMessage("Historique mis à jour avec succès");
        } else {
            logMessage("Aucun changement détecté pour la semaine {$weekNumber}");
        }
    } else {
        logMessage("Première sauvegarde pour la semaine {$weekNumber}");
        CalendarManager::saveHistory($weekNumber, $newEvents);
    }
    $today = new DateTime();
    if ($today->format('N') == 6) {
        logMessage("Samedi détecté, vérification de la semaine prochaine...");
        $nextWeekData = CalendarManager::getWeekEvents(1);
        $nextWeekNumber = $nextWeekData['weekNumber'];
        $nextWeekEvents = $nextWeekData['events'];
        if (isset($history[$nextWeekNumber])) {
            $oldNextWeekEvents = $history[$nextWeekNumber]['events'];
            $nextWeekChanges = CalendarManager::compareEvents($oldNextWeekEvents, $nextWeekEvents);
            $hasNextWeekChanges = !empty($nextWeekChanges['added']) || !empty($nextWeekChanges['removed']) || !empty($nextWeekChanges['modified']);
            if ($hasNextWeekChanges) {
                logMessage("Changements détectés pour la semaine prochaine ({$nextWeekNumber})");
                CalendarManager::sendDiscordNotification($nextWeekChanges, $nextWeekNumber);
                CalendarManager::saveHistory($nextWeekNumber, $nextWeekEvents);
            }
        } else {
            CalendarManager::saveHistory($nextWeekNumber, $nextWeekEvents);
        }
    }
    logMessage("=== Vérification terminée avec succès ===\n");
} catch (Exception $e) {
    logMessage("ERREUR: " . $e->getMessage(), "ERROR");
    logMessage("=== Vérification terminée avec erreur ===\n");
    exit(1);
}
exit(0);
?>

<?php
require_once 'config.php';
require_once 'calendar_manager.php';
setJSONHeaders();
try {
    CalendarManager::downloadCalendar();
    echo json_encode(['success' => true, 'message' => 'Calendrier téléchargé avec succès', 'timestamp' => date('Y-m-d H:i:s')], JSON_UNESCAPED_UNICODE);
    logMessage("Téléchargement manuel du calendrier effectué");
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()], JSON_UNESCAPED_UNICODE);
    logMessage("Erreur download_calendar: " . $e->getMessage(), "ERROR");
}
?>

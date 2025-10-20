<?php
require_once 'config.php';
require_once 'calendar_manager.php';
setJSONHeaders();
try {
    $weekOffset = isset($_GET['week']) ? intval($_GET['week']) : 0;
    $weekOffset = max(-52, min(52, $weekOffset));
    $result = CalendarManager::getWeekEvents($weekOffset);
    echo json_encode(['success' => true, 'data' => $result], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()], JSON_UNESCAPED_UNICODE);
    logMessage("Erreur get_events: " . $e->getMessage(), "ERROR");
}
?>

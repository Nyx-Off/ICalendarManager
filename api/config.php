<?php
define('ICAL_URL', '');
define('DISCORD_WEBHOOK_URL', '');
define('BASE_DIR', dirname(__DIR__));
define('DATA_DIR', BASE_DIR . '/data');
define('LOGS_DIR', BASE_DIR . '/logs');
define('ICAL_FILE', DATA_DIR . '/calendar.ics');
define('HISTORY_FILE', DATA_DIR . '/events_history.json');
define('LOG_FILE', LOGS_DIR . '/application.log');
define('TIMEZONE', 'Europe/Paris');
date_default_timezone_set(TIMEZONE);
setlocale(LC_TIME, 'fr_FR.UTF-8', 'fra_fra', 'french');

function logMessage($message, $level = 'INFO') {
    $timestamp = date('Y-m-d H:i:s');
    $logEntry = "[{$timestamp}] [{$level}] {$message}\n";
    if (!file_exists(LOGS_DIR)) mkdir(LOGS_DIR, 0755, true);
    file_put_contents(LOG_FILE, $logEntry, FILE_APPEND);
}
function ensureDirectories() {
    $dirs = [DATA_DIR, LOGS_DIR];
    foreach ($dirs as $dir) {
        if (!file_exists($dir)) mkdir($dir, 0755, true);
    }
}
function setJSONHeaders() {
    header('Content-Type: application/json; charset=utf-8');
    header('Access-Control-Allow-Origin: *');
}

ensureDirectories();
?>
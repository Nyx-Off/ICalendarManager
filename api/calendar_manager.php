<?php
class CalendarManager {
    public static function downloadCalendar() {
        if (empty(ICAL_URL)) throw new Exception("URL du calendrier non configurée");
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, ICAL_URL);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        $content = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($httpCode !== 200 || $content === false) {
            throw new Exception("Erreur téléchargement calendrier (Code: {$httpCode})");
        }
        file_put_contents(ICAL_FILE, $content);
        logMessage("Calendrier téléchargé avec succès");
        return $content;
    }
    
    public static function parseICS($icsContent) {
        $events = [];
        $lines = explode("\n", str_replace("\r\n", "\n", $icsContent));
        $inEvent = false;
        $currentEvent = [];
        foreach ($lines as $line) {
            $line = trim($line);
            if ($line === 'BEGIN:VEVENT') {
                $inEvent = true;
                $currentEvent = [];
            } elseif ($line === 'END:VEVENT' && $inEvent) {
                if (!empty($currentEvent)) $events[] = $currentEvent;
                $inEvent = false;
            } elseif ($inEvent) {
                $parts = explode(':', $line, 2);
                if (count($parts) === 2) {
                    $key = explode(';', $parts[0])[0];
                    $value = $parts[1];
                    switch ($key) {
                        case 'DTSTART': $currentEvent['start'] = self::parseICSDate($value); break;
                        case 'DTEND': $currentEvent['end'] = self::parseICSDate($value); break;
                        case 'SUMMARY': $currentEvent['summary'] = self::unescapeICSText($value); break;
                        case 'LOCATION': $currentEvent['location'] = self::unescapeICSText($value); break;
                        case 'DESCRIPTION': $currentEvent['description'] = self::unescapeICSText($value); break;
                        case 'UID': $currentEvent['uid'] = $value; break;
                    }
                }
            }
        }
        return $events;
    }
    
    private static function parseICSDate($dateString) {
        $dateString = str_replace(['T', 'Z'], ['', ''], $dateString);
        if (strlen($dateString) >= 14) {
            $year = substr($dateString, 0, 4);
            $month = substr($dateString, 4, 2);
            $day = substr($dateString, 6, 2);
            $hour = substr($dateString, 8, 2);
            $minute = substr($dateString, 10, 2);
            $second = substr($dateString, 12, 2);
            $dt = new DateTime("{$year}-{$month}-{$day} {$hour}:{$minute}:{$second}", new DateTimeZone('UTC'));
            $dt->setTimezone(new DateTimeZone(TIMEZONE));
            return $dt;
        }
        return null;
    }
    
    private static function unescapeICSText($text) {
        return trim(str_replace(['\\\\n', '\\\\,', '\\\\;', '\\\\\\\\'], ["\n", ',', ';', '\\\\'], $text));
    }
    
    public static function getWeekEvents($weekOffset = 0) {
        if (!file_exists(ICAL_FILE)) {
            return ['error' => 'Aucun calendrier disponible', 'events' => []];
        }
        $icsContent = file_get_contents(ICAL_FILE);
        $allEvents = self::parseICS($icsContent);
        $now = new DateTime();
        $now->modify("{$weekOffset} weeks");
        $startOfWeek = clone $now;
        $startOfWeek->modify('monday this week');
        $startOfWeek->setTime(0, 0, 0);
        $endOfWeek = clone $startOfWeek;
        $endOfWeek->modify('+6 days');
        $endOfWeek->setTime(23, 59, 59);
        $weekEvents = [];
        foreach ($allEvents as $event) {
            if ($event['start'] >= $startOfWeek && $event['start'] <= $endOfWeek) {
                $dayKey = $event['start']->format('Y-m-d');
                if (!isset($weekEvents[$dayKey])) $weekEvents[$dayKey] = [];
                $weekEvents[$dayKey][] = [
                    'uid' => $event['uid'] ?? uniqid(),
                    'summary' => $event['summary'] ?? 'Sans titre',
                    'start' => $event['start']->format('c'),
                    'end' => $event['end']->format('c'),
                    'location' => $event['location'] ?? '',
                    'description' => $event['description'] ?? '',
                    'startTime' => $event['start']->format('H:i'),
                    'endTime' => $event['end']->format('H:i'),
                ];
            }
        }
        foreach ($weekEvents as &$dayEvents) {
            usort($dayEvents, function($a, $b) { return strcmp($a['start'], $b['start']); });
        }
        return [
            'events' => $weekEvents,
            'weekStart' => $startOfWeek->format('Y-m-d'),
            'weekEnd' => $endOfWeek->format('Y-m-d'),
            'weekNumber' => $startOfWeek->format('W'),
            'year' => $startOfWeek->format('Y'),
            'lastUpdate' => file_exists(ICAL_FILE) ? date('Y-m-d H:i:s', filemtime(ICAL_FILE)) : null
        ];
    }
    
    public static function compareEvents($oldEvents, $newEvents) {
        $changes = ['added' => [], 'removed' => [], 'modified' => []];
        $oldIndex = [];
        foreach ($oldEvents as $date => $dayEvents) {
            foreach ($dayEvents as $event) $oldIndex[$event['uid']] = $event;
        }
        $newIndex = [];
        foreach ($newEvents as $date => $dayEvents) {
            foreach ($dayEvents as $event) $newIndex[$event['uid']] = $event;
        }
        foreach ($newIndex as $uid => $newEvent) {
            if (!isset($oldIndex[$uid])) {
                $changes['added'][] = $newEvent;
            } else {
                $oldEvent = $oldIndex[$uid];
                $modifications = [];
                if ($oldEvent['summary'] !== $newEvent['summary']) {
                    $modifications['summary'] = ['old' => $oldEvent['summary'], 'new' => $newEvent['summary']];
                }
                if ($oldEvent['start'] !== $newEvent['start']) {
                    $modifications['start'] = ['old' => $oldEvent['start'], 'new' => $newEvent['start']];
                }
                if ($oldEvent['end'] !== $newEvent['end']) {
                    $modifications['end'] = ['old' => $oldEvent['end'], 'new' => $newEvent['end']];
                }
                if ($oldEvent['location'] !== $newEvent['location']) {
                    $modifications['location'] = ['old' => $oldEvent['location'], 'new' => $newEvent['location']];
                }
                if (!empty($modifications)) {
                    $changes['modified'][] = ['event' => $newEvent, 'changes' => $modifications];
                }
            }
        }
        foreach ($oldIndex as $uid => $oldEvent) {
            if (!isset($newIndex[$uid])) $changes['removed'][] = $oldEvent;
        }
        return $changes;
    }
    
    public static function sendDiscordNotification($changes, $weekNumber) {
        if (empty(DISCORD_WEBHOOK_URL)) {
            logMessage("Webhook Discord non configuré", "WARNING");
            return false;
        }
        $embeds = [];
        if (!empty($changes['added'])) {
            $fields = [];
            foreach ($changes['added'] as $event) {
                $date = date('d/m/Y', strtotime($event['start']));
                $location = !empty($event['location']) ? " 📍 {$event['location']}" : "";
                $fields[] = [
                    'name' => "✅ {$event['summary']}",
                    'value' => "📅 {$date} • ⏰ {$event['startTime']} - {$event['endTime']}{$location}",
                    'inline' => false
                ];
            }
            $embeds[] = [
                'title' => '📣 Événements Ajoutés',
                'description' => "Semaine {$weekNumber}",
                'color' => 3066993,
                'fields' => $fields,
                'timestamp' => date('c')
            ];
        }
        if (!empty($changes['modified'])) {
            $fields = [];
            foreach ($changes['modified'] as $modification) {
                $event = $modification['event'];
                $changeDetails = [];
                foreach ($modification['changes'] as $field => $change) {
                    switch ($field) {
                        case 'summary': $changeDetails[] = "Titre: `{$change['old']}` → `{$change['new']}`"; break;
                        case 'start':
                            $oldTime = date('d/m/Y H:i', strtotime($change['old']));
                            $newTime = date('d/m/Y H:i', strtotime($change['new']));
                            $changeDetails[] = "Début: `{$oldTime}` → `{$newTime}`";
                            break;
                        case 'end':
                            $oldTime = date('H:i', strtotime($change['old']));
                            $newTime = date('H:i', strtotime($change['new']));
                            $changeDetails[] = "Fin: `{$oldTime}` → `{$newTime}`";
                            break;
                        case 'location': $changeDetails[] = "Lieu: `{$change['old']}` → `{$change['new']}`"; break;
                    }
                }
                $fields[] = [
                    'name' => "✏️ {$event['summary']}",
                    'value' => implode("\n", $changeDetails),
                    'inline' => false
                ];
            }
            $embeds[] = [
                'title' => '📝 Événements Modifiés',
                'description' => "Semaine {$weekNumber}",
                'color' => 15844367,
                'fields' => $fields,
                'timestamp' => date('c')
            ];
        }
        if (!empty($changes['removed'])) {
            $fields = [];
            foreach ($changes['removed'] as $event) {
                $date = date('d/m/Y', strtotime($event['start']));
                $location = !empty($event['location']) ? " 📍 {$event['location']}" : "";
                $fields[] = [
                    'name' => "❌ {$event['summary']}",
                    'value' => "📅 {$date} • ⏰ {$event['startTime']} - {$event['endTime']}{$location}",
                    'inline' => false
                ];
            }
            $embeds[] = [
                'title' => '🗑️ Événements Supprimés',
                'description' => "Semaine {$weekNumber}",
                'color' => 15158332,
                'fields' => $fields,
                'timestamp' => date('c')
            ];
        }
        if (empty($embeds)) return false;
        $payload = [
            'content' => "🔔 **Changements détectés dans l'emploi du temps**",
            'embeds' => $embeds
        ];
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, DISCORD_WEBHOOK_URL);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $result = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($httpCode === 204 || $httpCode === 200) {
            logMessage("Notification Discord envoyée avec succès");
            return true;
        } else {
            logMessage("Erreur lors de l'envoi de la notification Discord (Code: {$httpCode})", "ERROR");
            return false;
        }
    }
    
    public static function loadHistory() {
        if (file_exists(HISTORY_FILE)) {
            $content = file_get_contents(HISTORY_FILE);
            return json_decode($content, true) ?: [];
        }
        return [];
    }
    
    public static function saveHistory($weekNumber, $events) {
        $history = self::loadHistory();
        $history[$weekNumber] = [
            'events' => $events,
            'timestamp' => time(),
            'date' => date('Y-m-d H:i:s')
        ];
        if (count($history) > 4) {
            $keys = array_keys($history);
            sort($keys);
            $toRemove = array_slice($keys, 0, count($keys) - 4);
            foreach ($toRemove as $key) unset($history[$key]);
        }
        file_put_contents(HISTORY_FILE, json_encode($history, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }
}
?>

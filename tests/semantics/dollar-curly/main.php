<?php
$calls = 0;
class CurlyPrivateHost {
    private static function notice($level, $message, $file, $line) {
        global $calls;
        $calls += 1;
        echo 'H', $calls, ':', $level, ':', $file, ':', $line, ':', error_reporting(), '|';
        published_curly_258();
        CurlyPublished258::token();
        echo '|';
        if ($calls === 1) {
            error_reporting(0);
            ini_set('display_errors', 'stdout');
            return false;
        }
        throw new Exception('stop');
    }
    public static function run() {
        set_error_handler([self::class, 'notice']);
        try {
            include __DIR__ . '/warned.php';
        } catch (Exception $error) {
            echo 'E:', $error->getMessage(), '|';
        }
        restore_error_handler();
    }
}
CurlyPrivateHost::run();
published_curly_258();
CurlyPublished258::token();
echo '|END';

<?php
class CvReviewThrow {
    private static function warning($level, $message, $file, $line) {
        echo 'H:', $message, ':', $line, '|';
        try { throw new Exception('handler'); }
        finally { echo 'F|'; }
    }
    private static function caught(Throwable $e) {
        $old = $e->getPrevious();
        echo $e instanceof ValueError ? 'V:' : 'E:', $e->getMessage(), ':';
        echo $old === null ? '-|' : $old->getMessage() . '|';
    }
    public static function run() {
        set_error_handler([self::class, 'warning'], E_WARNING);
        try { include $missingInclude; } catch (Throwable $e) { self::caught($e); }
        try { require $missingRequire; } catch (Throwable $e) { self::caught($e); }
        try { include_once $missingOnce; } catch (Throwable $e) { self::caught($e); }
        try { require_once $missingRequiredOnce; } catch (Throwable $e) { self::caught($e); }
        restore_error_handler();
        echo 'END';
    }
}
CvReviewThrow::run();

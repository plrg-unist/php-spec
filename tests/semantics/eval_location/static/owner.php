<?php
class StaticEvalOwner {
    public static $value =
        E_STRICT
        + 1;
}
class StaticEvalHandler {
    public static function run() {
        set_error_handler([self::class, 'handle'], E_DEPRECATED);
        echo StaticEvalChild::$value, '|';
    }
    public static function again() { self::handle(0, 'direct', __FILE__, 12); }
    private static function handle($level, $message, $file, $line) {
        echo '[', $file, ':', $line, ']|';
        echo eval('return self::class;'), '|', eval('return __FILE__;'), '|';
        try { eval('?'); } catch (ParseError $e) { echo 'P:', $e->getFile(), ':', $e->getLine(), '|'; }
    }
}

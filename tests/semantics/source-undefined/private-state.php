<?php
class PrivateSourceReader {
    private static function warning($level, $message, $file, $line) {
        echo 'H:', $GLOBALS['phase'], ':', $level, ':', $line, '|';




        set_include_path(__DIR__ . '/unused');
        if ($GLOBALS['phase'] >= 3) {
            throw new Exception('handler');
        }
        return true;
    }
    private static function caught(Throwable $error) {
        $previous = $error->getPrevious();
        echo 'C:', $error instanceof ValueError ? 'V:' : 'E:', $error->getMessage(), ':';
        echo $previous === null ? '-|' : $previous->getMessage() . '|';
    }
    public static function run() {
        set_error_handler([self::class, 'warning']);
        $GLOBALS['phase'] = 1;
        echo 'D|';
        $result = eval(
            $directEval
        );
        echo $result === null ? 'null|' : 'other|';
        $GLOBALS['phase'] = 2;
        echo 'Y|';
        $name = 'dynamicEval';
        $result = eval(
            ${$name}
        );
        echo $result === null ? 'null|' : 'other|';
        $GLOBALS['phase'] = 3;
        echo 'I|';
        try {
            include(
                $directInclude
            );
        } catch (Throwable $error) {
            self::caught($error);
        }
        $GLOBALS['phase'] = 4;
        echo 'R|';
        try {
            require_once(
                $directRequire
            );
        } catch (Throwable $error) {
            self::caught($error);
        }
        $GLOBALS['phase'] = 5;
        echo 'J|';
        $name = 'dynamicInclude';
        try {
            include(
                ${$name}
            );
        } catch (Throwable $error) {
            self::caught($error);
        }
        $GLOBALS['phase'] = 6;
        echo 'E|';
        try {
            eval(
                $throwEval
            );
        } catch (Throwable $error) {
            self::caught($error);
        }
        restore_error_handler();
        echo 'END';
    }
}
PrivateSourceReader::run();

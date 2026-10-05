<?php
class ArrayRequireOwner {
    private static function notice($level, $message, $file, $line) {
        echo 'H:', $message, ':', $line, '|';
        set_include_path('callback-path');
        ini_set('display_errors', '0');
        $GLOBALS['operand'] = 'changed';
        $trace = new Exception('mark');
        echo $trace->getTraceAsString(), '|';
        throw new Exception('stop');
    }
    public static function run() {
        set_error_handler([self::class, 'notice'], E_WARNING);
        $GLOBALS['operand'] = [7];
        try {
            require $GLOBALS['operand'];
            echo 'bad|';
        } catch (Exception $e) {
            echo 'E:', $e->getMessage(), ':', $GLOBALS['operand'], ':', get_include_path(), ':', ini_get('display_errors'), '|';
        }
        restore_error_handler();
    }
}
ArrayRequireOwner::run();
echo 'END';

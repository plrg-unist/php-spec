<?php
class MagicNanParent86 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        echo 'G|';
        return NAN;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicNanChild86 extends MagicNanParent86 {}
function acceptNan86($level, $message, $file, $line): bool {
    global $child;
    echo 'H:', $level, '/', $message, '/', $line, '|';
    $child = null;
    echo 'h|';
    return true;
}
set_error_handler('acceptNan86');
$child = new MagicNanChild86();
echo 'N:', empty($child->value) ? 'T' : 'F', '|';
restore_error_handler();
echo 'E|';

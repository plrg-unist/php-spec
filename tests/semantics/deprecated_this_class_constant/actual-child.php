<?php
namespace Ns237This;
class Base237 {
    #[\Deprecated]
    public const A = 7, B = 8;
    public function read(): void {
        global $member237;
        echo "L|", $this::A, "|";
        echo "P|", $this::{('A' . '')}, "|";
        $member237 = 'A';
        echo "V|", $this::{$member237}, "|";
        echo "R|", $this::{\Ns237This\member237()}, "|";
        echo "S|", self::A, "|";
    }
}
class Child237 extends Base237 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function member237(): string {
    echo "M|";
    return $GLOBALS['member237'];
}
$member237 = 'A';
set_error_handler(function ($level, $message) {
    echo "H|";
    $GLOBALS['member237'] = 'B';
    return true;
});
$object237 = new Child237;
$object237->read();
echo "Z|";

<?php
namespace Ns234Private;
class Vault234 {
    #[\Deprecated]
    private const A = 7, B = 8;
    public static function read(): void {
        global $member234;
        echo "C|", self::{$member234}, "|";
        $GLOBALS['return234'] = 'A';
        echo "R|", self::{\Ns234Private\member234()}, "|";
        echo "F|", self::{\Ns234Private\member234()}, "|";
    }
}
function member234(): string {
    echo "M|";
    $GLOBALS['selected234'] = $GLOBALS['return234'];
    return $GLOBALS['return234'];
}
$GLOBALS['member234'] = 'A';
$GLOBALS['return234'] = 'A';
$GLOBALS['selected234'] = 'A';
set_error_handler(function ($level, $message) {
    echo "H|";
    $denied = $GLOBALS['selected234'];
    try {
        $unused = Vault234::{$denied};
        echo "BAD|";
    } catch (\Error $error) {
        echo "E|";
    }
    $GLOBALS['member234'] = 'B';
    $GLOBALS['return234'] = 'B';
    return true;
});
Vault234::read();
echo "Z|";

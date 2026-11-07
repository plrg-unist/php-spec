<?php
namespace Ns236Order;
class Base236 {
    #[\Deprecated]
    public const A = 7, B = 8;
}
class Child236 extends Base236 {}
class Other236 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function select236(): string {
    echo "C|";
    $GLOBALS['member236'] = 'A';
    return $GLOBALS['class236'];
}
$member236 = 'B';
$class236 = Child236::class;
set_error_handler(function ($level, $message) {
    echo "H|";
    $GLOBALS['member236'] = 'B';
    $GLOBALS['class236'] = Other236::class;
    return true;
});
echo "O|", (\Ns236Order\select236())::{$member236}, "|";
echo "F|", (\Ns236Order\select236())::{$member236}, "|";
echo "Z|";

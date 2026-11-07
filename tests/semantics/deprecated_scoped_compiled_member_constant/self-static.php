<?php
namespace Ns235Scope;
class Base235 {
    #[\Deprecated]
    private const A = 7;
    #[\Deprecated]
    protected const B = 8;
    public static function read(): void {
        echo "S|", self::{('A' . '')}, "|";
        echo "T|", static::{('B' . '')}, "|";
    }
}
class Child235 extends Base235 {
    #[\Deprecated]
    protected const B = 9;
}
set_error_handler(function ($level, $message) {
    echo "H|";
    return true;
});
Base235::read();
Child235::read();
echo "Z|";

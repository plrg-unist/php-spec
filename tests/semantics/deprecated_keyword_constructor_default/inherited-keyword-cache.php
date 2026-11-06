<?php
namespace {
    #[Deprecated] const X = [];
    function notice200() { echo 'H|'; }
}
namespace Ns200 {
    class Root200 {
        function __construct($value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 5;
        }
    }
    class Base200 extends Root200 {
        static function makeSelf() { return new self; }
        static function makeParent() { return new parent; }
        static function makeStatic() { return new static; }
    }
    class Child200 extends Base200 {}
    set_error_handler('notice200');
    $self = Child200::makeSelf();
    $parent = Child200::makeParent();
    $late = Child200::makeStatic();
}

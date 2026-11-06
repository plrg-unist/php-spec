<?php
namespace { const X = 9; }
namespace Ns192 {
class Receiver192 {
    public function method192($value = X) { echo $value === 9 ? 'N|' : 'E|'; }
}
$receiver = new Receiver192(); $receiver->method192();
#[\Deprecated] const X = [];
$fake = $receiver->method192(...);
$fake();
}

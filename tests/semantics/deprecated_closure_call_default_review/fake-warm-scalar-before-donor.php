<?php
namespace { const X = 9; }
namespace Ns191 {
class Receiver191 {
    public function method191($value = X) { echo $value === 9 ? 'N|' : 'E|'; }
}
$receiver = new Receiver191();
$receiver->method191();
#[\Deprecated] const X = [];
$fake = $receiver->method191(...);
$fake->call($receiver);
}

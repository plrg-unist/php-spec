<?php
const X = 9;
class Receiver193 {
    public function run($v = X, $tag = 0) { echo $v, "|"; }
}
$receiver = new Receiver193;
$fn = $receiver->run(...);
$fn();
$fn->__invoke(tag: 1);

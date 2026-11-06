<?php
#[Deprecated] const X = [1];
class Receiver186 { function receive($value = X) { echo $value[0], '|'; } }
$receiver = new Receiver186();
$receiver->receive();

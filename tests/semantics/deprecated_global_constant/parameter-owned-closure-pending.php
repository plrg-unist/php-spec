<?php
#[Deprecated] const X = [1];
$receive = static function($value = X) { echo $value[0], '|'; };
$receive();

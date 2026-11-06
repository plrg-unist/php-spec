<?php
const BASE = static function () { echo __CLASS__ === '' ? 'G|' : 'BAD|'; };
#[Deprecated] const X = BASE;
class Cache194 { const VALUE = X; }
function notice194() { echo 'H|'; return true; }
set_error_handler('notice194');
$first = Cache194::VALUE;
$first();
echo Cache194::VALUE === BASE ? 'same|' : 'BAD|';

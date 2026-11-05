"""Independent carrier-key classification and progress outside the tick original."""

CASES = {
    'review-interned-numeric-and-padded-keys-stay-distinct': (b'''<?php
function numeric_key() { return '7'; }
function padded_key() { return '07'; }
set_error_handler(static function ($n, $m) { echo 'H'; return true; });
$values = [];
$values[numeric_key()] = 'N';
$values[padded_key()] = 'P';
echo $values[7];
echo $values['07'];
''', b'NP'),
    'review-request-carrier-byte-keys-progress-through-write-and-unset': (b'''<?php
function joined_key($prefix, $suffix) { return $prefix . $suffix; }
set_error_handler(static function ($n, $m) { echo 'H'; return true; });
$values = [];
$values[joined_key('0', '7')] = 5;
unset($values[joined_key('0', '7')]);
echo $values['07'] ?? 'Z';
''', b'Z'),
}

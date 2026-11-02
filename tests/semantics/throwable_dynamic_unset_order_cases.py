"""Native-first reinserted-key stability across an unrelated COW write."""

CASES = {'dynamic-reinsert-later-key-stability': br'''<?php
#[AllowDynamicProperties] class Packet161 {}
function outer161($x): Exception { return new Exception('outer', 7); }
$left = new Packet161; $right = new Packet161;
$left->gone = 0; $left->first = 1; $left->tail = 0; unset($left->first); $left->first = 1; $left->later = 9;
$right->gone = 0; $right->tail = 0; $right->first = 2; $right->later = 0;
$a = outer161($left); $b = outer161($right); echo 'B|', $a <=> $b, '|';
$view = (array)$left; $left->tail = 0;
echo 'M|', $a <=> $b, ':', $b <=> $a, '|V|', $view['first'], ':', $view['later'], '|';
'''}
EXPECTED = {'dynamic-reinsert-later-key-stability': b'B|-1|M|-1:1|V|1:9|'}

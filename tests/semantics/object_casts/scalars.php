<?php
foreach ([false, true, -17, 1.5, '', 'text'] as $v) {
    $o = (object)$v;
    echo ($o instanceof stdClass ? 'S' : 'X'), ':', ($o->scalar === $v ? 'same' : 'bad'), ':', $o->scalar, '|';
}
$a = (object)null; $b = (object)[]; echo ($a === $b ? 'same' : 'fresh'), '|';
$c = (object)$a; echo ($a === $c ? 'id' : 'bad'), '|';
$o = (object)INF; echo $o->scalar, '|END';

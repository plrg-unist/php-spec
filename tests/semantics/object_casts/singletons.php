<?php
$v=1; $a=['x'=>&$v]; unset($v); $o=(object)$a; $o->x=2; echo $a['x'], ':', $o->x, '|';
$v=3; $a=[0=>&$v]; unset($v); $o=(object)$a; $o->{'0'}=4; echo $a[0], ':', $o->{'0'}, '|';
$v=5; $a=['x'=>&$v]; unset($v); $o=(object)$a; $r=&$o->x; $r=6; echo $a['x'], ':', $o->x, '|';
$v=7; $a=['x'=>&$v]; unset($v); $o=(object)$a; unset($o->x); $o->x=8; echo $a['x'], ':', $o->x, '|';
$a=['nested'=>[1]]; $o=(object)$a; $o->nested[0]=2; echo $a['nested'][0], ':', $o->nested[0], '|';
$b=(array)$o; $b['nested'][0]=3; echo $o->nested[0], ':', $b['nested'][0], '|END';

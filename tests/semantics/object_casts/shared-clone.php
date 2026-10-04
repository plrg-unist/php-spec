<?php
class SharedCastOwner { public int $v=1; }
$g=new SharedCastOwner; $a=['x'=>&$g->v]; $o=(object)$a; $c=(object)$a; unset($g,$a); $o->x=2; echo $c->x, ':', $o->x, '|';
$g=new SharedCastOwner; $a=['x'=>&$g->v]; $o=(object)$a; $c=clone $o; unset($g,$a); $o->x=3; echo $c->x, ':', $o->x, '|';
$v=4; $o=(object)['x'=>&$v]; $c=clone $o; $o->x=5; echo $v, ':', $c->x, ':', $o->x, '|'; unset($v); $c->x=6; echo $c->x, ':', $o->x, '|END';

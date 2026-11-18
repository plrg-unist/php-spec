<?php
namespace W339A;
interface A {}
interface B {}
interface C {}
class First339 implements \W339A\A,\W339A\B { public $tag = 61; }
class Second339 implements \W339A\C { public $tag = 61; }
class Missing0339 implements \W339A\A { public $tag = 81; }
class Missing1339 implements \W339A\B { public $tag = 81; }
class Missing2339 { public $tag = 81; }
class Box339 {
    public (\W339A\A&\W339A\B)|\W339A\C $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W339AX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as D;
use stdClass as Alpha;
use stdClass as Prefix;
$box339 = new \W339A\Box339();
$box339->v = new \W339A\First339();
$r339 =& $box339->v;
$s339 =& $r339;
echo $r339 === $s339 && $r339->tag === 61 ? 'I|' : 'BAD|';
$copy339 = $box339->v;
$copy339->tag = 67;
echo $copy339 === $r339 && $s339->tag === 67 ? 'C|' : 'BAD|';
$s339 = new \W339A\Second339();
$s339->tag = 71;
echo $r339 === $s339 && $r339->tag === 71 && $copy339->tag === 67 ? 'O|' : 'BAD|';
$kept339 = $r339;
try { $r339 = new \W339A\Missing0339(); } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'M0|' : 'BAD|';
}
unset($error339);
try { $r339 = new \W339A\Missing1339(); } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'M1|' : 'BAD|';
}
unset($error339);
try { $r339 = new \W339A\Missing2339(); } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'M2|' : 'BAD|';
}
unset($error339);
try { $s339 = 17; } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'S|' : 'BAD|';
}
unset($error339);
$r339 = $copy339;
$read339 = $box339->v;
echo $read339 === $copy339 && $r339 === $copy339 && $s339 === $copy339 && $kept339->tag === 71 ? 'P|' : 'BAD|';
unset($read339);
unset($box339);
$s339 = [];
echo $r339 === [] && $copy339->tag === 67 && $kept339->tag === 71 ? 'F|' : 'BAD|';
$r339 = false;
$copy339 = 0;
$kept339 = 0;
unset($r339, $s339, $copy339, $kept339);
echo 'Z|';

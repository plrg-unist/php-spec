<?php
namespace P339;
interface A {}
interface B {}
namespace W339B;
interface C {}
interface D {}
class First339 implements \P339\A,\P339\B { public $tag = 61; }
class Second339 implements \W339B\C,\W339B\D { public $tag = 61; }
class Missing0339 implements \P339\A,\W339B\C { public $tag = 81; }
class Missing1339 implements \P339\B,\W339B\D { public $tag = 81; }
class Missing2339 { public $tag = 81; }
use P339\A as Alpha;
use P339 as Prefix;
class Box339 {
    public (Alpha&Prefix\B)|(namespace\C&D) $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W339BX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as D;
use stdClass as Alpha;
use stdClass as Prefix;
$box339 = new \W339B\Box339();
$box339->v = new \W339B\First339();
$r339 =& $box339->v;
$s339 =& $r339;
echo $r339 === $s339 && $r339->tag === 61 ? 'I|' : 'BAD|';
$copy339 = $box339->v;
$copy339->tag = 67;
echo $copy339 === $r339 && $s339->tag === 67 ? 'C|' : 'BAD|';
$s339 = new \W339B\Second339();
$s339->tag = 71;
echo $r339 === $s339 && $r339->tag === 71 && $copy339->tag === 67 ? 'O|' : 'BAD|';
$kept339 = $r339;
try { $r339 = new \W339B\Missing0339(); } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'M0|' : 'BAD|';
}
unset($error339);
try { $r339 = new \W339B\Missing1339(); } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'M1|' : 'BAD|';
}
unset($error339);
try { $r339 = new \W339B\Missing2339(); } catch (\TypeError $error339) {
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

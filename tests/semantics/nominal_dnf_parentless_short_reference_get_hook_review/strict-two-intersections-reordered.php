<?php
declare(strict_types=1);
namespace D339B;
interface D {}
namespace D339Q;
interface A {}
interface B {}
interface C {}
namespace D339Q;
class First339 implements \D339Q\C,\D339B\D { public $tag = 61; }
class Second339 implements \D339Q\A,\D339Q\B { public $tag = 61; }
class Missing0339 implements \D339Q\C,\D339Q\A { public $tag = 61; }
class Missing1339 implements \D339B\D,\D339Q\B { public $tag = 61; }
namespace D339B;
use D339Q\A as Alpha;
class Box339 {
    public (namespace\D&\D339Q\C)|(\D339Q\B&aLpHa) $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace D339BX;
use stdClass as Alpha;
use stdClass as Gamma;
use stdClass as Tree;
$box339 = new \D339B\Box339();
$box339->v = new \D339Q\First339();
$r339 =& $box339->v;
$s339 =& $r339;
echo $r339 === $s339 && $r339->tag === 61 ? 'I|' : 'BAD|';
$copy339 = $box339->v;
$copy339->tag = 67;
echo $copy339 === $r339 && $s339->tag === 67 ? 'C|' : 'BAD|';
$s339 = new \D339Q\Second339();
$s339->tag = 71;
echo $r339 === $s339 && $r339->tag === 71 && $copy339->tag === 67 ? 'O|' : 'BAD|';
$kept339 = $r339;
try { $r339 = new \D339Q\Missing0339(); } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'M0|' : 'BAD|';
}
unset($error339);
try { $r339 = new \D339Q\Missing1339(); } catch (\TypeError $error339) {
    echo $r339 === $s339 && $r339 === $kept339 && $r339->tag === 71 ? 'M1|' : 'BAD|';
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

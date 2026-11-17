<?php
declare(strict_types=1);
namespace I334P;
class A { public $tag = 61; }
class B { public $tag = 71; }
class C { public $tag = 81; }
class D { public $tag = 91; }
class E { public $tag = 101; }
namespace I334C;
use I334P as Tree;
use I334P\C as Gamma;
use I334P\D as Delta;
class Box334 {
    public gAmMa|tReE\E|dElTa|\I334P\A|tReE\B $v {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
namespace I334CX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as D;
use stdClass as E;
use stdClass as Tree;
use stdClass as Gamma;
use stdClass as Delta;
$box334 = new \I334C\Box334();
$seed334 = new \I334P\E();
$box334->v = $seed334;
unset($seed334);
$r334 =& $box334->v;
$s334 =& $r334;
echo $r334 === $s334 && $r334->tag === 101 ? 'I|' : 'BAD|';
$copy334 = $box334->v;
$copy334->tag = 67;
echo $copy334 === $r334 && $s334 === $r334 && $r334->tag === 67 ? 'C|' : 'BAD|';
$s334 = new \I334P\D();
echo $r334 === $s334 && $r334->tag === 91 && $copy334->tag === 67 ? 'D|' : 'BAD|';
$r334 = new \I334P\B();
echo $r334 === $s334 && $r334->tag === 71 && $copy334->tag === 67 ? 'B|' : 'BAD|';
$s334 = new \I334P\A();
echo $r334 === $s334 && $r334->tag === 61 && $copy334->tag === 67 ? 'A|' : 'BAD|';
$r334 = new \I334P\C();
echo $r334 === $s334 && $r334->tag === 81 && $copy334->tag === 67 ? 'C|' : 'BAD|';
try { $r334 = new \stdClass(); } catch (\TypeError $error334) {
    echo $error334->getMessage(); echo '|';
    echo $r334 === $s334 && $r334->tag === 81 && $copy334->tag === 67 ? 'W|' : 'BAD|';
}
unset($error334);
try { $s334 = 127; } catch (\TypeError $error334) {
    echo $error334->getMessage(); echo '|';
    echo $r334 === $s334 && $r334->tag === 81 && $copy334->tag === 67 ? 'J|' : 'BAD|';
}
unset($error334);
$kept334 = $r334;
$read334 = $box334->v;
echo $read334 === $r334 && $kept334 === $s334 && $copy334->tag === 67 ? 'P|' : 'BAD|';
unset($read334);
unset($box334);
$s334 = 149;
echo $r334 === 149 && $copy334->tag === 67 && $kept334->tag === 81 ? 'F|' : 'BAD|';
$r334 = [];
$copy334 = 0;
$kept334 = 0;
unset($r334, $s334, $copy334, $kept334);
echo 'Z|';

<?php
declare(strict_types=1);
namespace I332P;
class Leaf322 { public $tag = 97; }
namespace I332O;
use I332P\Leaf322 as TU;
class Box322 {
    public float|array|tU|bool|string|int|null $v = null {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
namespace I332C;
use stdClass as TU;
$box322 = new \I332O\Box322();
$first322 = $box322->v;
echo $first322 === null ? 'I|' : 'BAD|';
unset($first322);
$r322 =& $box322->v;
$s322 =& $box322->v;
echo $r322 === null && $s322 === null ? 'N|' : 'BAD|';
$r322 = new \I332P\Leaf322();
$r322->tag = 101;
$copy322 = $box322->v;
$copy322->tag = 107;
echo $copy322 === $r322 && $s322 === $r322 && $r322->tag === 107 ? 'M|' : 'BAD|';
$s322 = new \I332P\Leaf322();
$s322->tag = 113;
echo $r322 === $s322 && $copy322 !== $r322 && $copy322->tag === 107 && $r322->tag === 113 ? 'R|' : 'BAD|';
try { $r322 = new \stdClass(); } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'W|' : 'BAD|';
}
unset($error322);
$r322 = false;
echo $r322 === false && $s322 === false ? 'Vfalse|' : 'BAD|';
$s322 = 37;
echo $r322 === 37 && $s322 === 37 ? 'Vint|' : 'BAD|';
$r322 = 37.0;
echo $r322 === 37.0 && $s322 === 37.0 ? 'Vfloat|' : 'BAD|';
$s322 = '37';
echo $r322 === '37' && $s322 === '37' ? 'Vstr|' : 'BAD|';
$r322 = null;
echo $r322 === null && $s322 === null ? 'Vnull|' : 'BAD|';
$s322 = [193];
$arraycopy322 = $box322->v;
$arraycopy322[0] = 197;
echo $r322[0] === 193 && $s322[0] === 193 && $arraycopy322[0] === 197 && $copy322->tag === 107 ? 'T|' : 'BAD|';
unset($arraycopy322);
$s322 = [];
echo $r322 === [] && $s322 === [] && $copy322->tag === 107 ? 'Q|' : 'BAD|';
$box322->v = new \I332P\Leaf322();
$s322->tag = 127;
$kept322 = $r322;
$read322 = $box322->v;
echo $read322 === $r322 && $kept322 === $s322 && $kept322->tag === 127 ? 'P|' : 'BAD|';
unset($read322);
unset($box322);
$s322 = 211;
echo $r322 === 211 && $copy322->tag === 107 && $kept322->tag === 127 ? 'F|' : 'BAD|';
$r322 = new \stdClass();
$r322->tag = 233;
echo $s322 === $r322 && $s322->tag === 233 ? 'F2|' : 'BAD|';
$r322 = [];
echo $s322 === [] && $copy322->tag === 107 ? 'A2|' : 'BAD|';
$copy322 = 0;
$kept322 = 0;
unset($r322, $s322, $copy322, $kept322);
echo 'Z|';

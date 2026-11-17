<?php
namespace FloatUnionFqOwner;
class Leaf322 { public $tag = 97; }
class Box322 {
    public \stdClass|float $v = 0.0 {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace FloatUnionFqConsumer;
use stdClass as Leaf322;
$box322 = new \FloatUnionFqOwner\Box322();
$first322 = $box322->v;
echo $first322 === 0.0 ? 'I|' : 'BAD|';
unset($first322);
$r322 =& $box322->v;
$s322 =& $box322->v;
echo $r322 === 0.0 && $s322 === 0.0 ? 'N|' : 'BAD|';
$r322 = new \stdClass();
$r322->tag = 101;
$copy322 = $box322->v;
$copy322->tag = 107;
echo $copy322 === $r322 && $s322 === $r322 && $r322->tag === 107 ? 'M|' : 'BAD|';
$s322 = new \stdClass();
$s322->tag = 113;
echo $r322 === $s322 && $copy322 !== $r322 && $copy322->tag === 107 && $r322->tag === 113 ? 'R|' : 'BAD|';
try { $r322 = new \FloatUnionFqOwner\Leaf322(); } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 && $copy322->tag === 107 ? 'W|' : 'BAD|';
}
unset($error322);
try { $r322 = null; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 && $copy322->tag === 107 ? 'A|' : 'BAD|';
}
unset($error322);
try { $r322 = []; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 && $copy322->tag === 107 ? 'J|' : 'BAD|';
}
unset($error322);
$s322 = 0.0;
echo $r322 === 0.0 && $s322 === 0.0 && $copy322->tag === 107 ? 'Q|' : 'BAD|';
$s322 = false;
echo $r322 === 0.0 && $s322 === 0.0 && $copy322->tag === 107 ? 'B0|' : 'BAD|';
$r322 = true;
echo $r322 === 1.0 && $s322 === 1.0 && $copy322->tag === 107 ? 'B1|' : 'BAD|';
$box322->v = new \stdClass();
$s322->tag = 127;
$kept322 = $r322;
$read322 = $box322->v;
echo $read322 === $r322 && $kept322 === $s322 && $kept322->tag === 127 ? 'P|' : 'BAD|';
unset($read322);
unset($box322);
$s322 = 211;
echo $r322 === 211 && $copy322->tag === 107 && $kept322->tag === 127 ? 'F|' : 'BAD|';
$r322 = [];
echo $s322 === [] && $copy322->tag === 107 ? 'A2|' : 'BAD|';
$copy322 = 0;
$kept322 = 0;
unset($r322, $s322, $copy322, $kept322);
echo 'Z|';

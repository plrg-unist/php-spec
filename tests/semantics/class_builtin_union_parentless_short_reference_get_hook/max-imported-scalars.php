<?php
namespace W332P;
class Leaf332 { public $tag = 97; }
namespace W332C;
use W332P\Leaf332 as TU;
class Box322 {
    public array|int|tU|float|string|null|false $v = null {
        &get => $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W332Z;
use stdClass as TU;
$box322 = new \W332C\Box322();
$first322 = $box322->v;
echo $first322 === null ? 'I|' : 'BAD|';
unset($first322);
$r322 =& $box322->v;
$s322 =& $box322->v;
echo $r322 === null && $s322 === null ? 'N|' : 'BAD|';
$r322 = new \W332P\Leaf332();
$r322->tag = 101;
$copy322 = $box322->v;
$copy322->tag = 107;
echo $copy322 === $r322 && $s322 === $r322 && $r322->tag === 107 ? 'M|' : 'BAD|';
$s322 = new \W332P\Leaf332();
$s322->tag = 113;
echo $r322 === $s322 && $copy322 !== $r322 && $copy322->tag === 107 && $r322->tag === 113 ? 'R|' : 'BAD|';
try { $r322 = new \stdClass(); } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'W|' : 'BAD|';
}
unset($error322);
$r322 = false;
echo $r322 === false && $s322 === false ? 'L|' : 'BAD|';
$s322 = true;
echo $r322 === 1 && $s322 === 1 ? 'B|' : 'BAD|';
$r322 = '37.0';
echo $r322 === '37.0' && $s322 === '37.0' ? 'U|' : 'BAD|';
$s322 = 37.0;
echo $r322 === 37.0 && $s322 === 37.0 ? 'V|' : 'BAD|';
$r322 = 37;
echo $r322 === 37 && $s322 === 37 ? 'E|' : 'BAD|';
$s322 = [193];
echo $r322[0] === 193 && $s322[0] === 193 ? 'T|' : 'BAD|';
$r322 = null;
echo $r322 === null && $s322 === null ? 'Q|' : 'BAD|';
$box322->v = new \W332P\Leaf332();
$s322->tag = 127;
$kept322 = $r322;
$read322 = $box322->v;
echo $read322 === $r322 && $kept322 === $s322 && $kept322->tag === 127 ? 'P|' : 'BAD|';
unset($read322);
unset($box322);
$s322 = true;
echo $r322 === true && $s322 === true && $copy322->tag === 107 && $kept322->tag === 127 ? 'F|' : 'BAD|';
$r322 = 0;
$copy322 = 0;
$kept322 = 0;
unset($r322, $s322, $copy322, $kept322);
echo 'Z|';

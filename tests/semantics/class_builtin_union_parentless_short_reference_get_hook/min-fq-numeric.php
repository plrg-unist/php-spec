<?php
namespace W332A;
class Wrong332 { public $tag = 97; }
class Box322 {
    public \stdClass|int|float $v = 0 {
        &get => $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W332X;
use W332A\Wrong332 as stdClass;
$box322 = new \W332A\Box322();
$first322 = $box322->v;
echo $first322 === 0 ? 'I|' : 'BAD|';
unset($first322);
$r322 =& $box322->v;
$s322 =& $box322->v;
echo $r322 === 0 && $s322 === 0 ? 'N|' : 'BAD|';
$r322 = new \stdClass();
$r322->tag = 101;
$copy322 = $box322->v;
$copy322->tag = 107;
echo $copy322 === $r322 && $s322 === $r322 && $r322->tag === 107 ? 'M|' : 'BAD|';
$s322 = new \stdClass();
$s322->tag = 113;
echo $r322 === $s322 && $copy322 !== $r322 && $copy322->tag === 107 && $r322->tag === 113 ? 'R|' : 'BAD|';
try { $r322 = new \W332A\Wrong332(); } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'W|' : 'BAD|';
}
unset($error322);
try { $r322 = null; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'A|' : 'BAD|';
}
unset($error322);
try { $r322 = []; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'J|' : 'BAD|';
}
unset($error322);
$r322 = '37';
echo $r322 === 37 && $s322 === 37 ? 'U|' : 'BAD|';
$s322 = '37.0';
echo $r322 === 37.0 && $s322 === 37.0 ? 'V|' : 'BAD|';
$r322 = true;
echo $r322 === 1 && $s322 === 1 ? 'B|' : 'BAD|';
$s322 = 37.0;
echo $r322 === 37.0 && $s322 === 37.0 ? 'E|' : 'BAD|';
$box322->v = new \stdClass();
$s322->tag = 127;
$kept322 = $r322;
$read322 = $box322->v;
echo $read322 === $r322 && $kept322 === $s322 && $kept322->tag === 127 ? 'P|' : 'BAD|';
unset($read322);
unset($box322);
$s322 = [];
echo $r322 === [] && $s322 === [] && $copy322->tag === 107 && $kept322->tag === 127 ? 'F|' : 'BAD|';
$r322 = 0;
$copy322 = 0;
$kept322 = 0;
unset($r322, $s322, $copy322, $kept322);
echo 'Z|';

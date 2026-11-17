<?php
declare(strict_types=1);
namespace Peer323RelativeOwner;
class Leaf322 { public $tag = 97; }
class Box322 {
    public namespace\Leaf322 $v {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
namespace Peer323RelativeConsumer;
use stdClass as Leaf322;
$box322 = new \Peer323RelativeOwner\Box322();
$seed322 = new \Peer323RelativeOwner\Leaf322();
$seed322->tag = 101;
$box322->v = $seed322;
unset($seed322);
$first322 = $box322->v;
echo $first322 === $box322->v && $first322->tag === 101 ? 'I|' : 'BAD|';
unset($first322);
$r322 =& $box322->v;
$s322 =& $box322->v;
echo $r322 === $s322 && $r322->tag === 101 ? 'N|' : 'BAD|';
$copy322 = $box322->v;
$copy322->tag = 107;
echo $copy322 === $r322 && $s322 === $r322 && $r322->tag === 107 ? 'M|' : 'BAD|';
$s322 = new \Peer323RelativeOwner\Leaf322();
$s322->tag = 113;
echo $r322 === $s322 && $copy322 !== $r322 && $copy322->tag === 107 && $r322->tag === 113 ? 'R|' : 'BAD|';
try { $r322 = new \stdClass(); } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 && $copy322->tag === 107 ? 'W|' : 'BAD|';
}
unset($error322);
try { $r322 = []; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 && $copy322->tag === 107 ? 'A|' : 'BAD|';
}
unset($error322);
try { $r322 = 191; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 && $copy322->tag === 107 ? 'J|' : 'BAD|';
}
unset($error322);
try { $s322 = null; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 && $copy322->tag === 107 ? 'Q|' : 'BAD|';
}
unset($error322);
$kept322 = $r322;
$read322 = $box322->v;
echo $read322 === $r322 && $kept322 === $s322 && $kept322->tag === 113 ? 'P|' : 'BAD|';
unset($read322);
unset($box322);
$s322 = 211;
echo $r322 === 211 && $copy322->tag === 107 && $kept322->tag === 113 ? 'F|' : 'BAD|';
$r322 = [];
echo $s322 === [] && $copy322->tag === 107 ? 'A2|' : 'BAD|';
$copy322 = false;
$kept322 = false;
unset($r322, $s322, $copy322, $kept322);
echo 'Z|';

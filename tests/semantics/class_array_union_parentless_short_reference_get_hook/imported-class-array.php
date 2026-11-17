<?php
namespace ArrayUnionPayload;
class Leaf322 { public $tag = 97; }
namespace ArrayUnionImportedOwner;
use ArrayUnionPayload as PrefixUnion;
class Box322 {
    public pReFiXUnion\lEaF322|array $v = [] {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace ArrayUnionImportedConsumer;
use ArrayUnionShadow as PrefixUnion;
$box322 = new \ArrayUnionImportedOwner\Box322();
$first322 = $box322->v;
echo $first322 === [] ? 'I|' : 'BAD|';
unset($first322);
$r322 =& $box322->v;
$s322 =& $box322->v;
echo $r322 === [] && $s322 === [] ? 'N|' : 'BAD|';
$r322 = new \ArrayUnionPayload\Leaf322();
$r322->tag = 101;
$copy322 = $box322->v;
$copy322->tag = 107;
echo $copy322 === $r322 && $s322 === $r322 && $r322->tag === 107 ? 'M|' : 'BAD|';
$s322 = new \ArrayUnionPayload\Leaf322();
$s322->tag = 113;
echo $r322 === $s322 && $copy322 !== $r322 && $copy322->tag === 107 && $r322->tag === 113 ? 'R|' : 'BAD|';
try { $r322 = new \stdClass(); } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'W|' : 'BAD|';
}
unset($error322);
try { $r322 = null; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'A|' : 'BAD|';
}
unset($error322);
try { $r322 = 1; } catch (\TypeError $error322) {
    echo $error322->getMessage(); echo '|';
    echo $r322 === $s322 && $r322->tag === 113 ? 'J|' : 'BAD|';
}
unset($error322);
$s322 = [];
echo $r322 === [] && $s322 === [] && $copy322->tag === 107 ? 'Q|' : 'BAD|';
$r322 = [137];
$arraycopy322 = $box322->v;
$arraycopy322[0] = 139;
echo $r322[0] === 137 && $s322[0] === 137 && $arraycopy322[0] === 139 && $copy322->tag === 107 ? 'C|' : 'BAD|';
$box322->v = new \ArrayUnionPayload\Leaf322();
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
unset($arraycopy322);
$copy322 = 0;
$kept322 = 0;
unset($r322, $s322, $copy322, $kept322);
echo 'Z|';

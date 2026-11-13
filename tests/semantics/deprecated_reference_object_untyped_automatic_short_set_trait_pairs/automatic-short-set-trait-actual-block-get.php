<?php
namespace Ns284TraitActualAutomaticShortSet;
class Leaf284 {
    public function __destruct() { echo 'L|'; }
}
trait Pair284 {
    public $tag {
        set(
            $incoming284
        ) =>
            ($GLOBALS['sets284execution'] = $GLOBALS['sets284execution'] + 1)
                ? ($incoming284 === false ? true : $incoming284)
                : $incoming284;
        get {
            $GLOBALS['gets284execution'] = $GLOBALS['gets284execution'] + 1;
            return 41;
        }
    }
}
class Box284 { use Pair284; }
$gets284execution = 0;
$sets284execution = 0;
$box284 = new Box284();
echo $box284->tag === 41 && $gets284execution === 1 && $sets284execution === 0 ? 'D|' : 'BAD|';
$result284 = $box284->tag = false;
echo $result284 === false && $box284->tag === 41 && $sets284execution === 1 && $gets284execution === 2 ? 'B|' : 'BAD|';
$box284->tag = new Leaf284();
echo $box284->tag === 41 && $sets284execution === 2 && $gets284execution === 3 ? 'I|' : 'BAD|';
$result284 = $box284->tag = 'plain';
echo $result284 === 'plain' && $box284->tag === 41 && $sets284execution === 3 && $gets284execution === 4 ? 'T|' : 'BAD|';
echo $sets284execution === 3 && $gets284execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';

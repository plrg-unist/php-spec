<?php
namespace Ns286ClassImplicitAutomaticShortSet;
class Leaf286 {
    public function __destruct() { echo 'L|'; }
}
class Box286 {
    public $tag = 17 {
        get =>
            ($GLOBALS['gets286execution'] = $GLOBALS['gets286execution'] + 1)
                ? 41
                : 41;
        set =>
            ($GLOBALS['sets286execution'] = $GLOBALS['sets286execution'] + 1)
                ? ($value === false ? true : $value)
                : $value;
    }
}
$gets286execution = 0;
$sets286execution = 0;
$box286 = new Box286();
echo $box286->tag === 41 && $gets286execution === 1 && $sets286execution === 0 ? 'D|' : 'BAD|';
$result286 = $box286->tag = false;
echo $result286 === false && $box286->tag === 41 && $sets286execution === 1 && $gets286execution === 2 ? 'B|' : 'BAD|';
$box286->tag = new Leaf286();
echo $box286->tag === 41 && $sets286execution === 2 && $gets286execution === 3 ? 'I|' : 'BAD|';
$result286 = $box286->tag = 'plain';
echo $result286 === 'plain' && $box286->tag === 41 && $sets286execution === 3 && $gets286execution === 4 ? 'T|' : 'BAD|';
echo $sets286execution === 3 && $gets286execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';

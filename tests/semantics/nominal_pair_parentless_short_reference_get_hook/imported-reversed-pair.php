<?php
namespace P333;
class First333 { public $tag = 61; }
class Second333 { public $tag = 71; }
namespace W333C;
use P333 as Tree;
use P333\Second333 as Alias;
class Box333 {
    public aLiAs|TrEe\First333 $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W333CX;
use stdClass as First333;
use stdClass as Second333;
use stdClass as Alias;
use stdClass as Tree;
$box333 = new \W333C\Box333();
$seed333 = new \P333\First333();
$box333->v = $seed333;
unset($seed333);
$first333 = $box333->v;
echo $first333->tag === 61 ? 'I|' : 'BAD|';
unset($first333);
$r333 =& $box333->v;
$s333 =& $box333->v;
echo $r333 === $s333 && $r333->tag === 61 ? 'N|' : 'BAD|';
$copy333 = $box333->v;
$copy333->tag = 67;
echo $copy333 === $r333 && $s333 === $r333 && $r333->tag === 67 ? 'M|' : 'BAD|';
$s333 = new \P333\Second333();
$s333->tag = 71;
echo $r333 === $s333 && $copy333 !== $r333 && $copy333->tag === 67 && $r333->tag === 71 ? 'R|' : 'BAD|';
try { $r333 = new \stdClass(); } catch (\TypeError $error333) {
    echo $error333->getMessage(); echo '|';
    echo $r333 === $s333 && $r333->tag === 71 && $copy333->tag === 67 ? 'W|' : 'BAD|';
}
unset($error333);
try { $s333 = 127; } catch (\TypeError $error333) {
    echo $error333->getMessage(); echo '|';
    echo $r333 === $s333 && $r333->tag === 71 && $copy333->tag === 67 ? 'J|' : 'BAD|';
}
unset($error333);
$box333->v = new \P333\First333();
$s333->tag = 79;
$kept333 = $r333;
$read333 = $box333->v;
echo $read333 === $r333 && $kept333 === $s333 && $kept333->tag === 79 && $copy333->tag === 67 ? 'P|' : 'BAD|';
unset($read333);
unset($box333);
$s333 = 149;
echo $r333 === 149 && $copy333->tag === 67 && $kept333->tag === 79 ? 'F|' : 'BAD|';
$r333 = [];
$copy333 = 0;
$kept333 = 0;
unset($r333, $s333, $copy333, $kept333);
echo 'Z|';

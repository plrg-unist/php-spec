<?php
declare(strict_types=1);
namespace I333A;
class First333 { public $tag = 107; }
class Second333 { public $tag = 97; }
class Third333 { public $tag = 151; }
class Box333 {
    public \I333A\Second333|\I333A\First333 $v {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
namespace I333AX;
use stdClass as First333;
use stdClass as Second333;
use stdClass as Lead;
use stdClass as Tree;
$box333 = new \I333A\Box333();
$seed333 = new \I333A\Second333();
$box333->v = $seed333;
unset($seed333);
$first333 = $box333->v;
echo $first333->tag === 97 ? 'I|' : 'BAD|';
unset($first333);
$r333 =& $box333->v;
$s333 =& $box333->v;
echo $r333 === $s333 && $r333->tag === 97 ? 'N|' : 'BAD|';
$copy333 = $box333->v;
$copy333->tag = 103;
echo $copy333 === $r333 && $s333 === $r333 && $r333->tag === 103 ? 'M|' : 'BAD|';
$s333 = new \I333A\First333();
$s333->tag = 107;
echo $r333 === $s333 && $copy333 !== $r333 && $copy333->tag === 103 && $r333->tag === 107 ? 'R|' : 'BAD|';
try { $r333 = new \I333A\Third333(); } catch (\TypeError $error333) {
    echo $error333->getMessage(); echo '|';
    echo $r333 === $s333 && $r333->tag === 107 && $copy333->tag === 103 ? 'W|' : 'BAD|';
}
unset($error333);
try { $s333 = []; } catch (\TypeError $error333) {
    echo $error333->getMessage(); echo '|';
    echo $r333 === $s333 && $r333->tag === 107 && $copy333->tag === 103 ? 'A|' : 'BAD|';
}
unset($error333);
try { $r333 = true; } catch (\TypeError $error333) {
    echo $error333->getMessage(); echo '|';
    echo $r333 === $s333 && $r333->tag === 107 && $copy333->tag === 103 ? 'B|' : 'BAD|';
}
unset($error333);
$box333->v = new \I333A\Second333();
$s333->tag = 113;
$kept333 = $r333;
$read333 = $box333->v;
echo $read333 === $r333 && $kept333 === $s333 && $kept333->tag === 113 && $copy333->tag === 103 ? 'P|' : 'BAD|';
unset($read333);
unset($box333);
$s333 = new \I333A\Third333();
echo $r333 === $s333 && $r333->tag === 151 && $copy333->tag === 103 && $kept333->tag === 113 ? 'F|' : 'BAD|';
$r333 = [];
echo $s333 === [] && $copy333->tag === 103 && $kept333->tag === 113 ? 'Q|' : 'BAD|';
$copy333 = 0;
$kept333 = 0;
unset($r333, $s333, $copy333, $kept333);
echo 'Z|';

<?php
namespace Ns306WeakStringIntShortReference;
class Box306 {
    public string|int $v {
        &get =>
            $this->v;
    }
}
$box306 = new Box306();
echo (array)$box306 === [] ? 'U|' : 'BAD|';
$copy306 = 'saved';
try { $copy306 = $box306->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns306WeakStringIntShortReference\Box306::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy306 === 'saved' && (array)$box306 === [] ? 'P|' : 'BAD|';
unset($e);
$box306->v = 0;
$copy306 = $box306->v;
echo $copy306 === 0 && (array)$box306 === ['v' => 0] ? 'V|' : 'BAD|';
$copy306 = false;
$a306 =& $box306->v;
$b306 =& $box306->v;
echo $a306 === 0 && $b306 === 0 && $copy306 === false ? 'N|' : 'BAD|';
$a306 = '12';
echo $b306 === '12' ? 'S|' : 'BAD|';
$b306 = 17;
echo $a306 === 17 ? 'J|' : 'BAD|';
$a306 = 2.0;
echo $b306 === 2 ? 'D|' : 'BAD|';
$b306 = true;
echo $a306 === 1 ? 'T|' : 'BAD|';
$a306 = false;
echo $b306 === 0 ? 'F|' : 'BAD|';
try { $a306 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns306WeakStringIntShortReference\Box306::$v of type string|int' ? 'L|' : 'BAD|';
}
try { $b306 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns306WeakStringIntShortReference\Box306::$v of type string|int' ? 'A|' : 'BAD|';
}
try { $a306 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns306WeakStringIntShortReference\Box306::$v of type string|int' ? 'O|' : 'BAD|';
}
unset($e);
$b306 = 37;
echo $a306 === 37 && $copy306 === false ? 'K|' : 'BAD|';
unset($box306);
$a306 = false;
echo $b306 === false && $copy306 === false ? 'R|' : 'BAD|';
unset($a306, $b306, $copy306);
echo 'Z|';

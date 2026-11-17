<?php
declare(strict_types=0);
namespace Ns315WeakBoolStringFloatShortReferenceAuthor;
class Box315 {
    public bool|string|float $v {
        &get =>
            $this->v;
    }
}
$box315 = new Box315();
echo (array)$box315 === [] ? 'U|' : 'BAD|';
$copy315 = 'saved';
try { $copy315 = $box315->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns315WeakBoolStringFloatShortReferenceAuthor\Box315::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy315 === 'saved' && (array)$box315 === [] ? 'P|' : 'BAD|';
unset($e);
$box315->v = 0.0;
$copy315 = $box315->v;
echo $copy315 === 0.0 ? 'V|' : 'BAD|';
$copy315 = 17;
$a315 =& $box315->v;
$b315 =& $box315->v;
echo $a315 === 0.0 && $b315 === 0.0 && $copy315 === 17 ? 'N|' : 'BAD|';
$a315 = 23;
echo $a315 === 23.0 && $b315 === 23.0 ? 'J|' : 'BAD|';
$b315 = true;
echo $a315 === true && $b315 === true ? 'T|' : 'BAD|';
$a315 = false;
echo $a315 === false && $b315 === false ? 'F|' : 'BAD|';
$probe_bool315 = $box315->v;
echo $probe_bool315 === false && $a315 === false && $b315 === false && $copy315 === 17 ? 'G|' : 'BAD|';
unset($probe_bool315);
$a315 = 'plain';
echo $a315 === 'plain' && $b315 === 'plain' ? 'P|' : 'BAD|';
$probe_string315 = $box315->v;
echo $probe_string315 === 'plain' && $a315 === 'plain' && $b315 === 'plain' && $copy315 === 17 ? 'H|' : 'BAD|';
unset($probe_string315);
$a315 = '12';
echo $a315 === '12' && $b315 === '12' ? 'S|' : 'BAD|';
$b315 = '12.5';
echo $a315 === '12.5' && $b315 === '12.5' ? 'L|' : 'BAD|';
$a315 = '2e0';
echo $a315 === '2e0' && $b315 === '2e0' ? 'X|' : 'BAD|';
$b315 = '';
echo $a315 === '' && $b315 === '' ? 'E|' : 'BAD|';
$a315 = '0';
echo $a315 === '0' && $b315 === '0' ? 'Q|' : 'BAD|';
$b315 = 2;
echo $a315 === 2.0 && $b315 === 2.0 ? 'D|' : 'BAD|';
try { $a315 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns315WeakBoolStringFloatShortReferenceAuthor\Box315::$v of type string|float|bool' && $a315 === 2.0 && $b315 === 2.0 ? 'U|' : 'BAD|';
}
try { $b315 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns315WeakBoolStringFloatShortReferenceAuthor\Box315::$v of type string|float|bool' && $a315 === 2.0 && $b315 === 2.0 ? 'A|' : 'BAD|';
}
try { $a315 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns315WeakBoolStringFloatShortReferenceAuthor\Box315::$v of type string|float|bool' && $a315 === 2.0 && $b315 === 2.0 ? 'O|' : 'BAD|';
}
unset($e);
$b315 = 37;
echo $a315 === 37.0 && $b315 === 37.0 && $copy315 === 17 ? 'K|' : 'BAD|';
unset($box315);
$a315 = 2;
echo $a315 === 2 && $b315 === 2 && $copy315 === 17 ? 'R|' : 'BAD|';
unset($a315, $b315, $copy315);
echo 'Z|';

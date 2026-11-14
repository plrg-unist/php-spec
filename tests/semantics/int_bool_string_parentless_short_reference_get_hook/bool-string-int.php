<?php
declare(strict_types=0);
namespace Ns314WeakBoolStringIntShortReferenceAuthor;
class Box314 {
    public bool|string|int $v {
        &get =>
            $this->v;
    }
}
$box314 = new Box314();
echo (array)$box314 === [] ? 'U|' : 'BAD|';
$copy314 = 'saved';
try { $copy314 = $box314->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns314WeakBoolStringIntShortReferenceAuthor\Box314::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy314 === 'saved' && (array)$box314 === [] ? 'P|' : 'BAD|';
unset($e);
$box314->v = 0;
$copy314 = $box314->v;
echo $copy314 === 0 ? 'V|' : 'BAD|';
$copy314 = 17;
$a314 =& $box314->v;
$b314 =& $box314->v;
echo $a314 === 0 && $b314 === 0 && $copy314 === 17 ? 'N|' : 'BAD|';
$a314 = 23;
echo $a314 === 23 && $b314 === 23 ? 'J|' : 'BAD|';
$b314 = true;
echo $a314 === true && $b314 === true ? 'T|' : 'BAD|';
$a314 = false;
echo $a314 === false && $b314 === false ? 'F|' : 'BAD|';
$probe_bool314 = $box314->v;
echo $probe_bool314 === false && $a314 === false && $b314 === false && $copy314 === 17 ? 'G|' : 'BAD|';
unset($probe_bool314);
$a314 = 'plain';
echo $a314 === 'plain' && $b314 === 'plain' ? 'P|' : 'BAD|';
$probe_string314 = $box314->v;
echo $probe_string314 === 'plain' && $a314 === 'plain' && $b314 === 'plain' && $copy314 === 17 ? 'H|' : 'BAD|';
unset($probe_string314);
$a314 = '12';
echo $a314 === '12' && $b314 === '12' ? 'S|' : 'BAD|';
$b314 = '12.5';
echo $a314 === '12.5' && $b314 === '12.5' ? 'L|' : 'BAD|';
$a314 = '2e0';
echo $a314 === '2e0' && $b314 === '2e0' ? 'X|' : 'BAD|';
$b314 = '';
echo $a314 === '' && $b314 === '' ? 'E|' : 'BAD|';
$a314 = '0';
echo $a314 === '0' && $b314 === '0' ? 'Q|' : 'BAD|';
$b314 = 2.0;
echo $a314 === 2 && $b314 === 2 ? 'D|' : 'BAD|';
try { $a314 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns314WeakBoolStringIntShortReferenceAuthor\Box314::$v of type string|int|bool' && $a314 === 2 && $b314 === 2 ? 'U|' : 'BAD|';
}
try { $b314 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns314WeakBoolStringIntShortReferenceAuthor\Box314::$v of type string|int|bool' && $a314 === 2 && $b314 === 2 ? 'A|' : 'BAD|';
}
try { $a314 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns314WeakBoolStringIntShortReferenceAuthor\Box314::$v of type string|int|bool' && $a314 === 2 && $b314 === 2 ? 'O|' : 'BAD|';
}
unset($e);
$b314 = 37;
echo $a314 === 37 && $b314 === 37 && $copy314 === 17 ? 'K|' : 'BAD|';
unset($box314);
$a314 = 2.5;
echo $a314 === 2.5 && $b314 === 2.5 && $copy314 === 17 ? 'R|' : 'BAD|';
unset($a314, $b314, $copy314);
echo 'Z|';

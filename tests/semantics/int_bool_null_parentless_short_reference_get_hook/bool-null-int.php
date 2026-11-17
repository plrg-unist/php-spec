<?php
declare(strict_types=0);
namespace Ns318WeakBoolNullIntShortReferenceAuthor;
class Box318 {
    public bool|null|int $v {
        &get =>
            $this->v;
    }
}
$box318 = new Box318();
echo (array)$box318 === [] ? 'U|' : 'BAD|';
$copy318 = 'saved';
$copy318 = $box318->v;
echo $copy318 === null ? 'V|' : 'BAD|';
echo (array)$box318 === ['v' => null] ? 'P|' : 'BAD|';
$copy318 = false;
$a318 =& $box318->v;
$b318 =& $box318->v;
echo $a318 === null && $b318 === null && $copy318 === false ? 'N|' : 'BAD|';
$a318 = 17;
echo $a318 === 17 && $b318 === 17 ? 'J|' : 'BAD|';
$b318 = true;
echo $a318 === true && $b318 === true ? 'T|' : 'BAD|';
$probe_bool318 = $box318->v;
echo $probe_bool318 === true && $a318 === true && $b318 === true && $copy318 === false ? 'G|' : 'BAD|';
unset($probe_bool318);
$a318 = '12';
echo $a318 === 12 && $b318 === 12 ? 'S|' : 'BAD|';
$b318 = '2e0';
echo $a318 === 2 && $b318 === 2 ? 'X|' : 'BAD|';
$a318 = 'plain';
echo $a318 === true && $b318 === true ? 'Q|' : 'BAD|';
$b318 = '';
echo $a318 === false && $b318 === false ? 'E|' : 'BAD|';
$a318 = '0';
echo $a318 === 0 && $b318 === 0 ? 'C|' : 'BAD|';
$b318 = 7.0;
echo $a318 === 7 && $b318 === 7 ? 'F|' : 'BAD|';
$a318 = false;
echo $a318 === false && $b318 === false ? 'B|' : 'BAD|';
$a318 = null;
echo $a318 === null && $b318 === null ? 'L|' : 'BAD|';
$probe_null318 = $box318->v;
echo $probe_null318 === null && $a318 === null && $b318 === null && $copy318 === false ? 'H|' : 'BAD|';
unset($probe_null318);
try { $b318 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns318WeakBoolNullIntShortReferenceAuthor\Box318::$v of type int|bool|null' && $a318 === null && $b318 === null ? 'A|' : 'BAD|';
}
try { $a318 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns318WeakBoolNullIntShortReferenceAuthor\Box318::$v of type int|bool|null' && $a318 === null && $b318 === null ? 'O|' : 'BAD|';
}
unset($e);
$b318 = 37;
echo $a318 === 37 && $b318 === 37 && $copy318 === false ? 'K|' : 'BAD|';
unset($box318);
$a318 = 'free';
echo $a318 === 'free' && $b318 === 'free' && $copy318 === false ? 'R|' : 'BAD|';
unset($a318, $b318, $copy318);
echo 'Z|';

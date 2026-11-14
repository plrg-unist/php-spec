<?php
namespace Ns299UninitializedObjectShortReference;
class Box299 {
    public object $item {
        &get =>
            $this->item;
    }
    public function __destruct() { echo 'D|'; }
}
$box299 = new Box299();
$probe299 = new \stdClass();
$probe299->tag = 47;
$shadow299 =& $probe299;
echo (array)$box299 === [] ? 'U|' : 'BAD|';
try { $read299 = $box299->item; } catch (\Error $e) { echo 'V|'; }
try { $probe299 =& $box299->item; } catch (\Error $e) { echo 'E|'; }
unset($e, $read299);
echo $probe299 === $shadow299 && $probe299->tag === 47 && (array)$box299 === [] ? 'K|' : 'BAD|';
$probe299 = 53;
echo $shadow299 === 53 ? 'A|' : 'BAD|';
$box299->item = new \stdClass();
$alias299 =& $box299->item;
$copy299 = $box299->item;
$copy299->tag = 59;
echo $alias299 === $copy299 && $alias299->tag === 59 ? 'G|' : 'BAD|';
$second299 = new \stdClass();
$second299->tag = 61;
$alias299 = $second299;
echo $alias299 === $second299 && $copy299 !== $second299 && $copy299->tag === 59 ? 'M|' : 'BAD|';
unset($box299);
$alias299 = null;
echo $alias299 === null && $copy299->tag === 59 && $second299->tag === 61 ? 'R|' : 'BAD|';
unset($alias299, $copy299, $second299, $probe299, $shadow299);
echo 'Z|';

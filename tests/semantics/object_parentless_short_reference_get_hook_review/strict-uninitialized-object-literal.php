<?php
declare(strict_types=1);
namespace Ns299UninitializedObjectShortReferencePeer;
class Box299 {
    public object $item {
        &get =>
            $this->{'item'};
    }
    public function __destruct() { echo 'D|'; }
}
$box299peer = new Box299();
$old299peer = new \stdClass();
$old299peer->value = 47;
$probe299peer = $old299peer;
$shadow299peer =& $probe299peer;
echo (array)$box299peer === [] ? 'U|' : 'BAD|';
try { $read299peer = $box299peer->item; } catch (\Error $e) { echo 'V|'; }
try { $probe299peer =& $box299peer->item; } catch (\Error $e) { echo 'E|'; }
unset($e);
echo $probe299peer === $old299peer && $shadow299peer === $old299peer && (array)$box299peer === [] ? 'K|' : 'BAD|';
$probe299peer = 53;
echo $shadow299peer === 53 ? 'A|' : 'BAD|';
unset($old299peer);
$seed299peer = new \stdClass();
$seed299peer->value = 59;
$box299peer->item = $seed299peer;
unset($seed299peer);
$alias299peer =& $box299peer->item;
$copy299peer = $box299peer->item;
$copy299peer->value = 61;
echo $alias299peer === $copy299peer && $alias299peer->value === 61 ? 'C|' : 'BAD|';
unset($box299peer);
$alias299peer = null;
echo $alias299peer === null && $copy299peer->value === 61 ? 'R|' : 'BAD|';
unset($alias299peer, $copy299peer, $probe299peer, $shadow299peer);
echo 'Z|';

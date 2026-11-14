<?php
declare(strict_types=1);
namespace Ns298ArrayNullShortReferencePeer;
class Box298 {
    public array|null $items {
        &get =>
            $this->{'items'};
    }
    public function __destruct() { echo 'D|'; }
}
$box298peer = new Box298();
echo (array)$box298peer === [] ? 'U|' : 'BAD|';
$read298peer = $box298peer->items;
echo $read298peer === null && (array)$box298peer === ['items' => null] ? 'V|' : 'BAD|';
unset($read298peer);
$alias298peer =& $box298peer->items;
$seed298peer = 11;
$alias298peer = ['slot' => &$seed298peer, 'nested' => [13]];
$copy298peer = $box298peer->items;
$alias298peer['nested'][0] = 17;
$seed298peer = 'leaf';
$live298peer = $box298peer->items;
echo $copy298peer === ['slot' => 'leaf', 'nested' => [13]] && $live298peer === ['slot' => 'leaf', 'nested' => [17]] ? 'C|' : 'BAD|';
unset($live298peer);
try { $alias298peer = 29; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns298ArrayNullShortReferencePeer\\Box298::$items of type ?array' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias298peer === ['slot' => 'leaf', 'nested' => [17]] ? 'K|' : 'BAD|';
$alias298peer = null;
echo $box298peer->items === null && $copy298peer === ['slot' => 'leaf', 'nested' => [13]] ? 'Q|' : 'BAD|';
unset($box298peer);
$alias298peer = false;
echo $alias298peer === false && $copy298peer === ['slot' => 'leaf', 'nested' => [13]] ? 'R|' : 'BAD|';
unset($alias298peer, $copy298peer, $seed298peer);
echo 'Z|';

<?php
declare(strict_types=1);
namespace Ns298NullArrayShortReferencePeer;
class Box298 {
    public null|array $items = [31] {
        &get =>
            $this->{'items'};
    }
    public function __destruct() { echo 'D|'; }
}
$box298peer = new Box298();
$alias298peer =& $box298peer->items;
$copy298peer = $box298peer->items;
$alias298peer[] = 37;
echo $copy298peer === [31] && $alias298peer === [31, 37] ? 'C|' : 'BAD|';
$alias298peer = null;
echo $box298peer->items === null && $copy298peer === [31] ? 'N|' : 'BAD|';
$alias298peer = ['nested' => [41]];
$reinit298peer = $box298peer->items;
$alias298peer['nested'][0] = 43;
$live298peer = $box298peer->items;
echo $reinit298peer === ['nested' => [41]] && $live298peer === ['nested' => [43]] ? 'A|' : 'BAD|';
unset($live298peer);
try { $alias298peer = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns298NullArrayShortReferencePeer\\Box298::$items of type ?array' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias298peer === ['nested' => [43]] ? 'K|' : 'BAD|';
unset($box298peer);
$alias298peer = 'released';
echo $alias298peer === 'released' && $copy298peer === [31] && $reinit298peer === ['nested' => [41]] ? 'R|' : 'BAD|';
unset($alias298peer, $copy298peer, $reinit298peer);
echo 'Z|';

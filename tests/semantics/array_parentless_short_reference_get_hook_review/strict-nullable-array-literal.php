<?php
declare(strict_types=1);
namespace Ns297NullableArrayShortReferencePeer;
class Box297 {
    public ?array $items {
        &get =>
            $this->{'items'};
    }
    public function __destruct() { echo 'D|'; }
}
$box297peer = new Box297();
echo (array)$box297peer === [] ? 'U|' : 'BAD|';
$read297peer = $box297peer->items;
echo $read297peer === null && (array)$box297peer === ['items' => null] ? 'V|' : 'BAD|';
unset($read297peer);
$alias297peer =& $box297peer->items;
echo $alias297peer === null ? 'N|' : 'BAD|';
$alias297peer = ['nested' => [31]];
$copy297peer = $box297peer->items;
$alias297peer['nested'][0] = 37;
echo $copy297peer === ['nested' => [31]] && $box297peer->items === ['nested' => [37]] ? 'C|' : 'BAD|';
$alias297peer = null;
echo $box297peer->items === null && $copy297peer === ['nested' => [31]] ? 'Q|' : 'BAD|';
try { $alias297peer = 'bad'; } catch (\TypeError $e) { echo 'T|'; }
echo $alias297peer === null ? 'K|' : 'BAD|';
unset($box297peer);
$alias297peer = 'released';
echo $alias297peer === 'released' && $copy297peer === ['nested' => [31]] ? 'R|' : 'BAD|';
unset($alias297peer, $copy297peer);
echo 'Z|';

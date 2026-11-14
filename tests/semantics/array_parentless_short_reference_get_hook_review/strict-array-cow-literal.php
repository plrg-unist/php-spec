<?php
declare(strict_types=1);
namespace Ns297ArrayShortReferencePeer;
class Box297 {
    public array $items = [7] {
        &get =>
            $this->{'items'};
    }
    public function __destruct() { echo 'D|'; }
}
$box297peer = new Box297();
$seed297peer = 11;
$box297peer->items = ['slot' => &$seed297peer, 'nested' => [13]];
$copy297peer = $box297peer->items;
$alias297peer =& $box297peer->items;
$alias297peer['tail'] = 17;
$seed297peer = 19;
echo $copy297peer === ['slot' => 19, 'nested' => [13]] && $box297peer->items === ['slot' => 19, 'nested' => [13], 'tail' => 17] ? 'C|' : 'BAD|';
$copy297peer['nested'][0] = 23;
$current297peer = $box297peer->items;
echo $current297peer['nested'][0] === 13 && $copy297peer['nested'][0] === 23 ? 'N|' : 'BAD|';
unset($current297peer);
$seed297peer = 'leaf';
$current297peer = $box297peer->items;
echo $copy297peer['slot'] === 'leaf' && $current297peer['slot'] === 'leaf' ? 'L|' : 'BAD|';
unset($current297peer);
try { $alias297peer = null; } catch (\TypeError $e) { echo 'T|'; }
try { $alias297peer = 'bad'; } catch (\TypeError $e) { echo 'S|'; }
echo $box297peer->items === ['slot' => 'leaf', 'nested' => [13], 'tail' => 17] ? 'K|' : 'BAD|';
unset($box297peer);
$alias297peer = 29;
echo $alias297peer === 29 && $copy297peer === ['slot' => 'leaf', 'nested' => [23]] ? 'R|' : 'BAD|';
unset($alias297peer, $copy297peer, $seed297peer);
echo 'Z|';

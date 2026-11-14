<?php
declare(strict_types=1);
namespace Ns297UninitializedArrayShortReferencePeer;
class Box297 {
    public array $items {
        &get =>
            $this->{'items'};
    }
    public function __destruct() { echo 'D|'; }
}
$box297peer = new Box297();
$probe297peer = [41];
$shadow297peer =& $probe297peer;
echo (array)$box297peer === [] ? 'U|' : 'BAD|';
try { $read297peer = $box297peer->items; } catch (\Error $e) { echo 'V|'; }
try { $probe297peer =& $box297peer->items; } catch (\Error $e) { echo 'E|'; }
echo $probe297peer === [41] && $shadow297peer === [41] && (array)$box297peer === [] ? 'K|' : 'BAD|';
$probe297peer[] = 43;
echo $shadow297peer === [41, 43] ? 'A|' : 'BAD|';
$box297peer->items = [47];
$alias297peer =& $box297peer->items;
$copy297peer = $box297peer->items;
$alias297peer[] = 53;
echo $box297peer->items === [47, 53] && $copy297peer === [47] ? 'C|' : 'BAD|';
unset($box297peer);
$alias297peer = null;
echo $alias297peer === null && $copy297peer === [47] ? 'R|' : 'BAD|';
unset($alias297peer, $copy297peer, $probe297peer, $shadow297peer);
echo 'Z|';

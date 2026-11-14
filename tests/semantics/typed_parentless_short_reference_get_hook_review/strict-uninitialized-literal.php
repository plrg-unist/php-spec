<?php
declare(strict_types=1);
namespace Ns296UninitializedShortReferencePeer;
class Box296 {
    public int $tag {
        &get =>
            $this->{'tag'};
    }
    public function __destruct() { echo 'D|'; }
}
$box296peer = new Box296();
$probe296peer = 'stay';
$shadow296peer =& $probe296peer;
echo (array)$box296peer === [] ? 'U|' : 'BAD|';
try { $read296peer = $box296peer->tag; } catch (\Error $e) { echo 'V|'; }
echo (array)$box296peer === [] ? 'Q|' : 'BAD|';
try { $probe296peer =& $box296peer->tag; } catch (\Error $e) { echo 'E|'; }
echo $probe296peer === 'stay' && $shadow296peer === 'stay' && (array)$box296peer === [] ? 'K|' : 'BAD|';
$probe296peer = 'after';
echo $shadow296peer === 'after' ? 'A|' : 'BAD|';
$box296peer->tag = 73;
$tag296peer =& $box296peer->tag;
echo $tag296peer === 73 ? 'G|' : 'BAD|';
try { $tag296peer = null; } catch (\TypeError $e) { echo 'T|'; }
echo $tag296peer === 73 ? 'C|' : 'BAD|';
unset($box296peer);
$tag296peer = [];
echo $tag296peer === [] ? 'R|' : 'BAD|';
unset($tag296peer, $probe296peer, $shadow296peer);
echo 'Z|';

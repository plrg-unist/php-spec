<?php
declare(strict_types=1);
namespace Ns296NullableShortReferencePeer;
class Box296 {
    public ?int $i = null {
        &get =>
            $this->{'i'};
    }
    public ?float $f {
        &get =>
            $this->{'f'};
    }
    public ?bool $b {
        &get =>
            $this->{'b'};
    }
    public ?string $s {
        &get =>
            $this->{'s'};
    }
    public function __destruct() { echo 'D|'; }
}
$box296peer = new Box296();
echo (array)$box296peer === ['i' => null] ? 'U|' : 'BAD|';
$read296peer = $box296peer->s;
echo $read296peer === null && (array)$box296peer === ['i' => null, 's' => null] ? 'V|' : 'BAD|';
unset($read296peer);
$i296peer =& $box296peer->i;
$f296peer =& $box296peer->f;
$b296peer =& $box296peer->b;
$s296peer =& $box296peer->s;
echo $i296peer === null && $f296peer === null && $b296peer === null && $s296peer === null ? 'N|' : 'BAD|';
try { $i296peer = '59'; } catch (\TypeError $e) { echo 'I|'; }
try { $s296peer = 61; } catch (\TypeError $e) { echo 'S|'; }
echo $i296peer === null && $s296peer === null ? 'K|' : 'BAD|';
$i296peer = 67;
$f296peer = 71;
$b296peer = false;
$s296peer = 'bound';
echo $box296peer->i === 67 && $box296peer->f === 71.0 && $box296peer->b === false && $box296peer->s === 'bound' ? 'W|' : 'BAD|';
$i296peer = null;
$f296peer = null;
$b296peer = null;
$s296peer = null;
echo $box296peer->i === null && $box296peer->f === null && $box296peer->b === null && $box296peer->s === null ? 'C|' : 'BAD|';
unset($box296peer);
$i296peer = [];
$f296peer = [];
$b296peer = [];
$s296peer = [];
echo $i296peer === [] && $f296peer === [] && $b296peer === [] && $s296peer === [] ? 'R|' : 'BAD|';
unset($i296peer, $f296peer, $b296peer, $s296peer);
echo 'Z|';

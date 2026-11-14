<?php
declare(strict_types=1);
namespace Ns296ScalarShortReferencePeer;
class Box296 {
    public int $i = 19 {
        &get =>
            $this->{'i'};
    }
    public float $f = 2.5 {
        &get =>
            $this->{'f'};
    }
    public bool $b = true {
        &get =>
            $this->{'b'};
    }
    public string $s = 'peer' {
        &get =>
            $this->{'s'};
    }
    public function __destruct() { echo 'D|'; }
}
$box296peer = new Box296();
$i296peer =& $box296peer->i;
$f296peer =& $box296peer->f;
$b296peer =& $box296peer->b;
$s296peer =& $box296peer->s;
echo $i296peer === 19 && $f296peer === 2.5 && $b296peer === true && $s296peer === 'peer' ? 'G|' : 'BAD|';
try { $i296peer = '23'; } catch (\TypeError $e) { echo 'I|'; }
try { $f296peer = '29'; } catch (\TypeError $e) { echo 'F|'; }
try { $b296peer = 0; } catch (\TypeError $e) { echo 'B|'; }
try { $s296peer = 31; } catch (\TypeError $e) { echo 'S|'; }
echo $i296peer === 19 && $f296peer === 2.5 && $b296peer === true && $s296peer === 'peer' ? 'K|' : 'BAD|';
$i296peer = 47;
$f296peer = 53;
$b296peer = false;
$s296peer = 'kept';
echo $box296peer->i === 47 && $box296peer->f === 53.0 && $box296peer->b === false && $box296peer->s === 'kept' ? 'W|' : 'BAD|';
unset($box296peer);
$i296peer = [];
$f296peer = [];
$b296peer = [];
$s296peer = [];
echo $i296peer === [] && $f296peer === [] && $b296peer === [] && $s296peer === [] ? 'R|' : 'BAD|';
unset($i296peer, $f296peer, $b296peer, $s296peer);
echo 'Z|';

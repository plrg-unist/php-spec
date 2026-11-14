<?php
namespace Ns296NullableShortReference;
class Box296 {
    public ?int $i {
        &get =>
            $this->i;
    }
    public ?float $f {
        &get =>
            $this->f;
    }
    public ?bool $b {
        &get =>
            $this->b;
    }
    public ?string $s {
        &get =>
            $this->s;
    }
    public function __destruct() { echo 'D|'; }
}
class Plain296 { public ?string $s; }
$plain296 = new Plain296();
try { $read296 = $plain296->s; } catch (\Error $e) { echo 'P|'; }
unset($plain296, $read296);
$box296 = new Box296();
echo (array)$box296 === [] ? 'U|' : 'BAD|';
$read296 = $box296->s;
echo $read296 === null && (array)$box296 === ['s' => null] ? 'V|' : 'BAD|';
unset($read296);
$i296 =& $box296->i;
$f296 =& $box296->f;
$b296 =& $box296->b;
$s296 =& $box296->s;
echo $i296 === null && $f296 === null && $b296 === null && $s296 === null ? 'N|' : 'BAD|';
$i296 = 37;
$f296 = 41;
$b296 = true;
$s296 = 'bound';
echo $box296->i === 37 && $box296->f === 41.0 && $box296->b === true && $box296->s === 'bound' ? 'W|' : 'BAD|';
$i296 = null;
$f296 = null;
$b296 = null;
$s296 = null;
echo $box296->i === null && $box296->f === null && $box296->b === null && $box296->s === null ? 'C|' : 'BAD|';
unset($box296);
$i296 = [];
$f296 = [];
$b296 = [];
$s296 = [];
echo $i296 === [] && $f296 === [] && $b296 === [] && $s296 === [] ? 'R|' : 'BAD|';
unset($i296, $f296, $b296, $s296);
echo 'Z|';

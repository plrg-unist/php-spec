<?php
namespace Ns296ScalarShortReference;
class Box296 {
    public int $i = 17 {
        &get =>
            $this->i;
    }
    public float $f = 1.5 {
        &get =>
            $this->f;
    }
    public bool $b = false {
        &get =>
            $this->b;
    }
    public string $s = 'seed' {
        &get =>
            $this->s;
    }
    public function __destruct() { echo 'D|'; }
}
$box296 = new Box296();
$i296 =& $box296->i;
$f296 =& $box296->f;
$b296 =& $box296->b;
$s296 =& $box296->s;
echo $i296 === 17 && $f296 === 1.5 && $b296 === false && $s296 === 'seed' ? 'G|' : 'BAD|';
$i296 = '23';
$f296 = 29;
$b296 = 2;
$s296 = 31;
echo $box296->i === 23 && $box296->f === 29.0 && $box296->b === true && $box296->s === '31' ? 'W|' : 'BAD|';
try { $i296 = []; } catch (\TypeError $e) { echo 'I|'; }
try { $f296 = []; } catch (\TypeError $e) { echo 'F|'; }
try { $b296 = []; } catch (\TypeError $e) { echo 'B|'; }
try { $s296 = []; } catch (\TypeError $e) { echo 'S|'; }
echo $i296 === 23 && $f296 === 29.0 && $b296 === true && $s296 === '31' ? 'K|' : 'BAD|';
unset($box296);
$i296 = 'free';
$f296 = 'free';
$b296 = 'free';
$s296 = [];
echo $i296 === 'free' && $f296 === 'free' && $b296 === 'free' && $s296 === [] ? 'R|' : 'BAD|';
unset($i296, $f296, $b296, $s296);
echo 'Z|';

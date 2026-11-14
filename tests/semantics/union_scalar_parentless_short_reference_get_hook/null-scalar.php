<?php
namespace Ns301WeakNullScalarShortReference;
class Box301 {
    public null|int $i {
        &get =>
            $this->i;
    }
    public null|float $f {
        &get =>
            $this->f;
    }
    public null|bool $b {
        &get =>
            $this->b;
    }
    public null|string $s {
        &get =>
            $this->s;
    }
    public function __destruct() { echo 'D|'; }
}
$box301 = new Box301();
echo (array)$box301 === [] ? 'U|' : 'BAD|';
$i301 =& $box301->i;
$f301 =& $box301->f;
$b301 =& $box301->b;
$s301 =& $box301->s;
echo $i301 === null && $f301 === null && $b301 === null && $s301 === null ? 'N|' : 'BAD|';
$i301 = '157';
$f301 = '1.5';
$b301 = 0;
$s301 = 173;
echo $i301 === 157 && $box301->i === 157 ? 'I|' : 'BAD|';
echo $f301 === 1.5 && $box301->f === 1.5 ? 'F|' : 'BAD|';
echo $b301 === false && $box301->b === false ? 'B|' : 'BAD|';
echo $s301 === '173' && $box301->s === '173' ? 'S|' : 'BAD|';
$copyi301 = $box301->i;
$copyf301 = $box301->f;
$copyb301 = $box301->b;
$copys301 = $box301->s;
$i301 = null;
$f301 = null;
$b301 = null;
$s301 = null;
echo $copyi301 === 157 && $copyf301 === 1.5 && $copyb301 === false && $copys301 === '173' && $i301 === null && $f301 === null && $b301 === null && $s301 === null ? 'Q|' : 'BAD|';
$i301 = 181;
$f301 = 2;
$b301 = true;
$s301 = 'live';
echo $box301->i === 181 && $box301->f === 2.0 && $box301->b === true && $box301->s === 'live' ? 'W|' : 'BAD|';
try { $i301 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns301WeakNullScalarShortReference\Box301::$i of type ?int' ? 'Ti|' : 'BAD|';
}
try { $f301 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns301WeakNullScalarShortReference\Box301::$f of type ?float' ? 'Tf|' : 'BAD|';
}
try { $b301 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns301WeakNullScalarShortReference\Box301::$b of type ?bool' ? 'Tb|' : 'BAD|';
}
try { $s301 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns301WeakNullScalarShortReference\Box301::$s of type ?string' ? 'Ts|' : 'BAD|';
}
unset($e);
echo $i301 === 181 && $f301 === 2.0 && $b301 === true && $s301 === 'live' ? 'K|' : 'BAD|';
unset($box301);
$i301 = [];
$f301 = 'free';
$b301 = 191;
$s301 = false;
echo $i301 === [] && $f301 === 'free' && $b301 === 191 && $s301 === false && $copyi301 === 157 && $copyf301 === 1.5 && $copyb301 === false && $copys301 === '173' ? 'R|' : 'BAD|';
unset($i301, $f301, $b301, $s301, $copyi301, $copyf301, $copyb301, $copys301);
echo 'Z|';

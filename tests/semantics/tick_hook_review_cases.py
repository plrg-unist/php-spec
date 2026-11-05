"""A real getter Tick callback can read a sibling and abort before the return."""

CASES = {
    'review-getter-body-tick-callback-abort-preserves-backing-value': (b'''<?php
$n = 0;
function t() {
    global $n, $object;
    $n = $n + 1;
    echo 'T';
    if ($n === 3) {
        echo $object->other;
        throw new Exception('stop');
    }
}
register_tick_function('t');
declare(ticks=1);
class TickHook43 {
    public $other = 9;
    public int $value = 7 {
        get {
            declare(ticks=1) { echo 'G'; }
            return $this->value;
        }
    }
}
$object = new TickHook43;
try { echo $object->value; echo 'BAD'; }
catch (Exception $e) { echo 'C'; }
echo $object->value;
echo 'Z';
''', b'TTGT9CTGT7TZT'),
    'review-closure-default-enables-first-main-property-tick': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
class TickPropProbe43 {
    public $f=static function(){declare(ticks=1);echo "BAD";};
}
echo "Z";
''', b'TZT'),
    'review-block-getter-enables-first-main-property-tick': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
class TickHookProbe43 {
    public int $value=7 {
        get { declare(ticks=1); return $this->value; }
    }
}
echo "Z";
''', b'TZT'),
    'review-early-property-tick-suppresses-the-following-bare-directive': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
class TickPropTail43 {
    public $f=static function(){declare(ticks=1);echo "BAD";};
}
declare(ticks=1);
echo "Z";
''', b'TZT'),
    'review-property-tick-abort-prevents-non-early-class-activation': (b'''<?php
$n=0;
function t(){
    global $n;
    $n=$n+1;
    echo 'T';
    if($n===1){
        $at=new Exception;
        echo '['.$at->getTrace()[0]['line'].']';
        try{TickPendingGroup43::VALUE;echo 'BAD';}
        catch(Error $absent){echo 'N';}
        throw new Exception('stop');
    }
}
function h($e){
    echo 'C';
    try{TickPendingGroup43::VALUE;echo 'BAD';}
    catch(Error $absent){echo 'N';}
}
register_tick_function('t');
set_exception_handler('h');
interface TickGroupReady43 {}
class TickPendingGroup43 implements TickGroupReady43 {
    public const VALUE=7;
    public $f=static function(){declare(ticks=1);echo 'BAD';};
}
echo 'BAD';
''', b'T[25]NCN'),
}

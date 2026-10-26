"""Frozen original normal mixed declared/dynamic table witnesses."""
CASES = {
    'right-copy-live-declared-slot': br'''<?php
class MixedNumber126 {}
#[AllowDynamicProperties]
class MixedCopyBox126 {
    private $front;
    private $tail;
    function __construct($front, $tail) { $this->front=$front; $this->tail=$tail; }
    function edit() { $this->dynamic=9; $this->tail=0; }
    function changed() { return $this->tail===0 && $this->dynamic===9; }
    function unchanged() { return $this->tail===0 && $this->dynamic===0; }
}
$left=new MixedCopyBox126(new MixedNumber126,0);
$right=new MixedCopyBox126(1,7);
$left->dynamic=0;
$right->dynamic=0;
$calls=0;
function mixed_copy_handler126($level,$message) {
    global $right,$calls;
    $calls=$calls+1;
    echo "H:",(int)($level===8 && $message==="Object of class MixedNumber126 could not be converted to int"),"|";
    $right->edit();
    return true;
}
set_error_handler('mixed_copy_handler126');
$result=41;
echo "B|";
$result=$left <=> $right; // COMPARE
echo "R:",(int)($result===0),":",(int)($calls===1),":",(int)$right->changed(),":",(int)$left->unchanged(),"|";
echo "A|";
''',
    'dynamic-direct-last-owner': br'''<?php
class MixedReleaseNumber126 {}
class MixedDynamicVictim126 { function __destruct() { echo "D|"; } }
#[AllowDynamicProperties]
class MixedReleaseBox126 {
    private $front;
    private $tail;
    function __construct($front,$tail) { $this->front=$front; $this->tail=$tail; }
    function edit() { unset($this->dynamic); $this->tail=0; }
    function changed() { return $this->tail===0 && !isset($this->dynamic); }
}
$left=new MixedReleaseBox126(new MixedReleaseNumber126,0);
$right=new MixedReleaseBox126(1,7);
$left->dynamic=[];
$right->dynamic=new MixedDynamicVictim126;
$calls=0;
function mixed_release_handler126($level,$message) {
    global $right,$calls;
    $calls=$calls+1;
    echo "H:",(int)($level===8 && $message==="Object of class MixedReleaseNumber126 could not be converted to int"),"|";
    $right->edit();
    echo "K|";
    return true;
}
set_error_handler('mixed_release_handler126');
$result=41;
echo "B|";
$result=$left <=> $right; // COMPARE
echo "R:",(int)($result===-1),":",(int)($calls===1),":",(int)$right->changed(),"|";
echo "A|";
''',
}

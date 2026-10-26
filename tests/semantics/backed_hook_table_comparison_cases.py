"""Frozen normal cached backing-hook comparison originals."""
CASES = {
    'cached-backing-skips-get-runs-set': br'''<?php
class HookTableNumber127 {}
#[AllowDynamicProperties]
class HookTableBox127 {
    public $front;
    public int $value = 7 {
        get { global $gets; $gets=$gets+1; return $this->value+100; }
        set { global $sets; $sets=$sets+1; $this->value=$value; }
    }
}
$gets=0; $sets=0;
$left=new HookTableBox127; $right=new HookTableBox127;
$left->front=new HookTableNumber127; $right->front=1;
$left->value=0;
$left->tag=0; $right->tag=0;
$gets=0; $sets=0; $calls=0;
function hook_table_handler127($level,$message) {
    global $right,$calls;
    $calls=$calls+1;
    echo 'H:',(int)($level===8 && $message==='Object of class HookTableNumber127 could not be converted to int'),'|';
    $right->value=0;
    return true;
}
set_error_handler('hook_table_handler127');
$result=41;
echo 'B|';
$result=$left <=> $right; // COMPARE
echo 'R:',(int)($result===0),':',(int)($calls===1),':',(int)($gets===0),':',(int)($sets===1),'|';
$observed=$right->value;
echo 'V:',(int)($observed===100),':',(int)($gets===1),'|A|';
''',
    'backed-set-mutates-selected-cell': br'''<?php
class HookCellNumber127 {}
#[AllowDynamicProperties]
class HookCellBox127 {
    public $front;
    public int $value = 7 {
        get { global $gets; $gets=$gets+1; return $this->value+100; }
        set { global $sets,$opposite; $sets=$sets+1; $opposite=1; $this->value=$value; }
    }
}
$gets=0; $sets=0; $opposite=0;
$left=new HookCellBox127; $right=new HookCellBox127;
$left->front=new HookCellNumber127;
$right->front =& $opposite;
$left->value=0;
$left->tag=0; $right->tag=0;
$gets=0; $sets=0; $opposite=0; $calls=0;
function hook_cell_handler127($level,$message) {
    global $right,$calls;
    $calls=$calls+1;
    echo 'H:',(int)($level===8 && $message==='Object of class HookCellNumber127 could not be converted to int'),'|';
    $right->value=0;
    return true;
}
set_error_handler('hook_cell_handler127');
$result=41;
echo 'B|';
$result=$left <=> $right; // COMPARE
echo 'R:',(int)($result===0),':',(int)($calls===1),':',(int)($gets===0),':',(int)($sets===1),':',(int)($opposite===1),'|A|';
''',
}

"""Independent writable ArrayAccess and affected GLOBALS/Unset originals."""



def review_source(name, body, *, get, set="echo 'WRONGSET;';",
           unset="echo 'WRONGUNSET;';", before=''):
    return ("<?php\nerror_reporting(0);\n" + before +
            f"class {name} implements ArrayAccess {{\n" +
            "    public function offsetExists(mixed $offset): bool { return false; }\n" +
            "    public function offsetGet(mixed $offset): mixed { " + get + " }\n" +
            "    public function offsetSet(mixed $offset, mixed $value): void { " + set + " }\n" +
            "    public function offsetUnset(mixed $offset): void { " + unset + " }\n" +
            "}\n" + body).encode()


CASES = [
    ('compound-live-key-and-borrowed-old-typed-rhs-cell', review_source('CompoundPointers292', """
$held292=&PointerCell292::$value; $rhs292=&$held292; $replacement292=17;
$key292=1; $o292=new CompoundPointers292;
$r292=($o292[$key292]+=$rhs292);
echo 'R:',$r292,':',$stored292,':',$rhs292,':',PointerCell292::$value,':',$key292,':',(int)isset($o292),';';
""", before="class PointerCell292 { public static int $value=13; }\n",
     get="echo 'G:',$offset,';'; $GLOBALS['key292']=7; $GLOBALS['rhs292'] =& $GLOBALS['replacement292']; $GLOBALS['held292']=19; unset($GLOBALS['o292']); return 5;",
     set="echo 'S:',$offset,':',$value,';'; $GLOBALS['stored292']=$value; $GLOBALS['held292']=23;"),
     b'G:1;S:7:22;R:22:22:17:23:7:0;'),

    ('compound-computed-array-rhs-shares-real-cell-after-retirement', review_source('CompoundArray292', """
$held292=&ArrayCell292::$value; $key292=[1,&$held292]; $o292=new CompoundArray292;
$r292=($o292[$key292]+=[2=>&$held292]);
$r292[2]=19;
echo 'R:',$r292[1],':',$saved292[1],':',ArrayCell292::$value,':',(int)isset($held292),':',(int)isset($o292),';';
""", before="class ArrayCell292 { public static int $value=9; }\n",
     get="echo 'G:',$offset[0],':',$offset[1],';'; $GLOBALS['held292']=13; $GLOBALS['key292']=[7]; unset($GLOBALS['held292'],$GLOBALS['o292']); return [1=>&ArrayCell292::$value];",
     set="echo 'S:',$offset[0],':',$value[1],':',$value[2],';'; $value[1]=17; $GLOBALS['saved292']=$value; unset($GLOBALS['key292']);"),
     b'G:1:9;S:7:13:13;R:19:19:19:0:0;'),

    ('nested-write-notice-keeps-returned-real-cell-not-old-key-copy', review_source('NestedCell292', """
$held292=&NestedCellBacking292::$value; $keyCell292=7; $key292=[1,&$keyCell292];
$o292=new NestedCell292;
set_error_handler(function($n,$m) { echo 'N:',$n,':',(int)isset($GLOBALS['keyCell292']),';'; $GLOBALS['held292']=13; return true; },8);
$r292=($o292[$key292][1]=17);
restore_error_handler();
echo 'R:',$r292,':',NestedCellBacking292::$value,':',$held292,':',(int)isset($o292),';';
""", before="class NestedCellBacking292 { public static int $value=9; }\n",
     get="echo 'G;'; $row=[1=>&$GLOBALS['held292']]; unset($GLOBALS['o292'],$GLOBALS['key292'],$GLOBALS['keyCell292']); return $row;"),
     b'G;N:8:0;R:17:17:17:0;'),

    ('nested-write-notice-cow-and-false-fallback-lose-plain-row-write', review_source('NestedCow292', """
$seed292=9; $data292=[1=>$seed292]; $o292=new NestedCow292;
set_error_handler(function($n,$m) { echo 'N;'; $GLOBALS['data292'][1]=13; return false; },8);
$r292=($o292[1][1]=17);
restore_error_handler();
echo 'R:',$r292,':',$data292[1],';';
""", get="echo 'G;'; return $GLOBALS['data292'];"),
     b'G;N;R:17:13;'),

    ('nested-notice-throw-skips-late-rhs-and-typed-destination', review_source('NestedThrow292', """
$seed292=9; $data292=[1=>$seed292]; $o292=new NestedThrow292;
$older292=new Error('older'); $error292=new Error('notice',0,$older292);
$target292=&NoticeTyped292::$value;
set_error_handler(function($n,$m) { if($n===8) { echo 'N;'; $e=$GLOBALS['error292']; unset($GLOBALS['error292'],$GLOBALS['older292']); throw $e; } echo 'U;'; return true; });
try { $target292=($o292[1][1]=$missing292); }
catch(Error $e) { echo 'C:',(int)($e->getMessage()==='notice'),':',NoticeTyped292::$value,':',$data292[1],':',(int)isset($missing292),':',$e->getPrevious()->getMessage(),';'; }
restore_error_handler();
""", before="class NoticeTyped292 { public static int $value=9; }\n",
     get="echo 'G;'; unset($GLOBALS['o292']); return $GLOBALS['data292'];"),
     b'G;N;C:1:9:9:0:older;'),

    ('nested-notice-reentry-keeps-outer-row-and-real-cell', review_source('NestedReentry292', """
$held292=&ReentryCell292::$value; $o292=new NestedReentry292;
set_error_handler(function($n,$m) { global $o292; echo 'N;'; $inner=++$o292[2]; echo 'I:',$inner,';'; $GLOBALS['held292']=13; return true; },8);
$r292=($o292[1][1]=17);
restore_error_handler();
echo 'R:',$r292,':',ReentryCell292::$value,';';
""", before="class ReentryCell292 { public static int $value=9; }\n",
     get="echo 'G:',$offset,';'; if($offset===2) return 5; return [1=>&$GLOBALS['held292']];"),
     b'G:1;N;G:2;I:6;R:17:17;'),

    ('nested-returned-object-survives-both-global-retirements', review_source('OuterObject292', """
$inner292=new InnerObject292; $o292=new OuterObject292;
set_error_handler(function($n,$m) { echo 'WRONGNOTICE;'; return true; },8);
$r292=($o292[1][7]=13);
restore_error_handler();
echo 'R:',$r292,':',$written292,':',(int)isset($inner292),':',(int)isset($o292),';';
""", before="""class InnerObject292 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { return null; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'S:',$offset,':',$value,';'; $GLOBALS['written292']=$value; }
    public function offsetUnset(mixed $offset): void {}
}
""", get="echo 'G;'; $inner=$GLOBALS['inner292']; unset($GLOBALS['inner292'],$GLOBALS['o292']); return $inner;"),
     b'G;S:7:13;R:13:13:0:0;'),

    ('nested-unset-notice-deletes-only-temporary-shared-cell-edge', review_source('NestedUnset292', """
$cell292=&UnsetCell292::$value; $data292=[1=>&$cell292,2=>13]; $o292=new NestedUnset292;
set_error_handler(function($n,$m) { echo 'N;'; $GLOBALS['data292'][1]=17; return true; },8);
unset($o292[1][1]);
restore_error_handler();
echo 'R:',(int)isset($data292[1]),':',$data292[1],':',UnsetCell292::$value,';';
""", before="class UnsetCell292 { public static int $value=9; }\n",
     get="echo 'G;'; return $GLOBALS['data292'];"),
     b'G;N;R:1:17:17;'),

    ('byvalue-get-reference-consumer-owns-detached-temporary', review_source('TemporaryRef292', """
$seed292=9; $data292=[1=>$seed292]; $o292=new TemporaryRef292;
set_error_handler(function($n,$m) { echo 'N;'; $GLOBALS['data292'][1]=13; return true; },8);
$ref292=&$o292[1];
restore_error_handler();
$ref292[1]=17;
echo 'R:',$ref292[1],':',$data292[1],';';
""", get="echo 'G;'; return $GLOBALS['data292'];"),
     b'G;N;R:17:13;'),

    ('compound-late-rhs-warning-precedes-get-throw-with-old-chain', review_source('CompoundThrow292', """
$o292=new CompoundThrow292; $target292=&GetTyped292::$value;
$older292=new Error('older'); $error292=new Error('get',0,$older292);
set_error_handler(function($n,$m) { echo 'U;'; $GLOBALS['rhs292']=17; return true; },2);
try { $target292=($o292[1]+=$rhs292); }
catch(Error $e) { echo 'C:',GetTyped292::$value,':',$rhs292,':',$e->getMessage(),':',$e->getPrevious()->getMessage(),':',(int)isset($error292),';'; }
restore_error_handler();
""", before="class GetTyped292 { public static int $value=9; }\n",
     get="echo 'G:',$offset,';'; $e=$GLOBALS['error292']; unset($GLOBALS['error292'],$GLOBALS['older292'],$GLOBALS['o292']); throw $e;"),
     b'U;G:1;C:9:17:Cannot use object of type CompoundThrow292 as array:get:0;'),
]


CASES += [
    ('compound-get-throw-replacement-keeps-exact-original-older-chain', review_source('ChainRead292', """
$older292=new Error('older'); $original292=new Error('get',0,$older292);
$expected292=$original292; $expectedOlder292=$older292; $o292=new ChainRead292; $target292=&ChainCell292::$value;
try { $target292=($o292[1]+=2); }
catch(Error $e) { echo 'C:',(int)($e===$expected292),':',(int)($e->getPrevious()===$expected292),':',(int)($e->getPrevious()->getPrevious()===$expectedOlder292),':',$e->getLine(),':',$e->getPrevious()->getLine(),':',ChainCell292::$value,':',(int)($e->getFile()===__FILE__),';'; unset($expected292,$expectedOlder292); echo 'L:',$e->getPrevious()->getMessage(),':',$e->getPrevious()->getPrevious()->getMessage(),';'; }
""", before="class ChainCell292 { public static int $value=9; }\n",
     get="echo 'G:',$offset,';'; $e=$GLOBALS['original292']; unset($GLOBALS['original292'],$GLOBALS['older292'],$GLOBALS['o292']); throw $e;"),
     b'G:1;C:0:1:1:13:11:9:1;L:get:older;'),

    ('compound-key-warning-throw-suppresses-get-but-keeps-replacement-chain', review_source('KeyThrow292', """
$o292=new KeyThrow292; $target292=&KeyThrowCell292::$value;
$older292=new Error('older'); $original292=new Error('key',0,$older292);
set_error_handler(function($n,$m) { echo 'U;'; $GLOBALS['key292']=7; $e=$GLOBALS['original292']; unset($GLOBALS['original292'],$GLOBALS['older292']); throw $e; },2);
try { $target292=($o292[$key292]+=2); }
catch(Error $e) { echo 'C:',(int)($e->getMessage()==='Cannot use object of type KeyThrow292 as array'),':',$e->getPrevious()->getMessage(),':',$e->getPrevious()->getPrevious()->getMessage(),':',KeyThrowCell292::$value,':',$key292,':',(int)isset($original292),';'; }
restore_error_handler();
""", before="class KeyThrowCell292 { public static int $value=9; }\n",
     get="echo 'WRONGGET;'; return 5;"),
     b'U;C:1:key:older:9:7:0;'),
]


CASES += [
    ('direct-reference-target-initializes-late-source-before-invalid-target',
     review_source('ReferenceTarget292', """
$o292=new ReferenceTarget292;
set_error_handler(function($n,$m) { echo $n===8?'N;':'WRONGU;'; return true; });
try { $o292[1] =& $missing292; }
catch(Error $e) { echo 'C:',(int)($e->getMessage()==='Cannot assign by reference to an array dimension of an object'),':',(int)($missing292===null),':',(int)isset($missing292),';'; }
restore_error_handler();
""", get="echo 'G;'; return 5;"), b'G;N;C:1:1:0;'),

    ('returned-ordinary-object-and-string-keep-terminal-consumer-kinds',
     review_source('TerminalKinds292', """
$o292=new TerminalKinds292;
set_error_handler(function($n,$m) { echo 'N;'; return true; },8);
try { $o292[1][0]=17; }
catch(Error $e) { echo 'C:',(int)($e->getMessage()==='Cannot use object of type stdClass as array'),';'; }
$r292=($o292[2][0]='Z');
restore_error_handler();
echo 'R:',$r292,';';
""", get="echo 'G:',$offset,';'; if($offset===1) return new stdClass; return 'xy';"),
     b'G:1;C:1;G:2;N;R:Z;'),
]


CHILDREN = """class FirstUnset292 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool {return false;}
 public function offsetGet(mixed $offset): mixed {return null;}
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {echo 'F:',(int)($offset===null),';';}
}
class SecondUnset292 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool {return false;}
 public function offsetGet(mixed $offset): mixed {return null;}
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {echo 'S:',(int)($offset===null),';';}
}
"""

CASES += [
    ('nested-unset-returned-object-keeps-temporary-after-global-rebind',
     review_source('ReturnedUnset292', """
$inner292=new FirstUnset292; $o292=new ReturnedUnset292;
set_error_handler(function($n,$m) {echo 'U;'; $GLOBALS['inner292']=new SecondUnset292; $GLOBALS['missing292']=7; return true;});
unset($o292[1][$missing292]);
restore_error_handler(); echo 'R:',$missing292,';';
""", before=CHILDREN,
            get="echo 'G;'; $inner=$GLOBALS['inner292']; unset($GLOBALS['inner292'],$GLOBALS['o292']); return $inner;"),
     b'G;U;F:1;R:7;'),
    ('nested-unset-alias-keeps-old-reference-after-variable-rebind',
     review_source('AliasUnset292', """
$child292=new FirstUnset292; $held292=&$child292; $replacement292=new SecondUnset292; $o292=new AliasUnset292;
set_error_handler(function($n,$m) {if($n===8) {echo 'N;'; return true;} echo 'U;'; $GLOBALS['child292'] =& $GLOBALS['replacement292']; $GLOBALS['missing292']=7; return true;});
unset($o292[1][1][$missing292]);
restore_error_handler(); echo 'R:',(int)($held292!==$child292),':',(int)($child292===$replacement292),':',$missing292,';';
""", before=CHILDREN,
            get="echo 'G;'; $row=[1=>&$GLOBALS['child292']]; unset($GLOBALS['o292']); return $row;"),
     b'G;N;U;F:1;R:1:1:7;'),
    ('nested-unset-ordinary-array-rereads-borrowed-element-after-warning',
     review_source('UnusedUnset292', """
$row292=[1=>new FirstUnset292];
set_error_handler(function($n,$m) {echo 'U;'; $GLOBALS['row292'][1]=new SecondUnset292; $GLOBALS['missing292']=7; return true;});
unset($row292[1][$missing292]);
restore_error_handler(); echo 'R:',$missing292,';';
""", before=CHILDREN, get="echo 'WRONG;';return null;"),
     b'U;S:1;R:7;'),
]


CASES += [
    ('globals-reference-writer-rebinds-cv-source-with-old-alias-retained', b'''<?php
error_reporting(0);
$target292=3; $held292=&$target292; $rhs292=5;
set_error_handler(function($n,$m) {echo 'UNEXPECTED;'; return true;});
$GLOBALS['target292'] =& $rhs292;
$rhs292=11;
restore_error_handler();
echo 'R:',$target292,':',$held292,':',$rhs292,';';
''', b'R:11:3:11;'),
    ('globals-reference-writer-keeps-function-local-shadow-separate', b'''<?php
error_reporting(0);
$target292=3; $held292=&$target292;
function bindGlobal292($rhs292) {
    $target292=40;
    $GLOBALS['target292'] =& $rhs292;
    $rhs292=9;
    echo 'L:',$target292,':',$rhs292,';';
}
set_error_handler(function($n,$m) {echo 'UNEXPECTED;'; return true;});
bindGlobal292(5);
restore_error_handler();
echo 'R:',$target292,':',$held292,';';
''', b'L:40:9;R:9:3;'),
    ('globals-reference-writer-missing-key-callback-mutates-name', b'''<?php
error_reporting(0);
$rhs292=5;
set_error_handler(function($n,$m) {echo 'U;'; $GLOBALS['missing292']='target292'; return true;});
$GLOBALS[$missing292] =& $rhs292;
$rhs292=11;
restore_error_handler();
echo 'R:',(int)isset($GLOBALS['']),':',(int)isset($target292),':',$missing292,':',($GLOBALS['']??0),':',($GLOBALS['target292']??0),';';
''', b'U;R:0:1:target292:0:11;'),
    ('globals-reference-writer-array-cv-keeps-converted-name-and-live-rhs', b'''<?php
error_reporting(0);
$key292=[1]; $rhs292=5; $old292=&$rhs292; $next292=7;
set_error_handler(function($n,$m) {
    echo 'A;'; $GLOBALS['key292']='changed292';
    $GLOBALS['rhs292'] =& $GLOBALS['next292']; return true;
});
$GLOBALS[$key292] =& $rhs292;
$GLOBALS['Array']=13;
restore_error_handler();
echo 'R:',(int)isset($GLOBALS['Array']),':',(int)isset($GLOBALS['changed292']),':',$GLOBALS['Array'],':',$key292,':',$old292,':',$rhs292,':',$next292,';';
''', b'A;R:1:0:13:changed292:5:13:13;'),
    ('globals-reference-writer-computed-array-keeps-key-and-source-cell-owners', b'''<?php
error_reporting(0);
$cell292=3; $held292=&$cell292; $rhs292=5; $old292=&$rhs292; $next292=7;
function makeGlobalKey292() {return [1=>&$GLOBALS['cell292']];}
set_error_handler(function($n,$m) {
    echo 'A;'; $GLOBALS['rhs292'] =& $GLOBALS['next292'];
    unset($GLOBALS['cell292']); return true;
});
$GLOBALS[makeGlobalKey292()] =& $GLOBALS['rhs292'];
$GLOBALS['Array']=11;
restore_error_handler();
echo 'R:',$old292,':',$rhs292,':',$next292,':',$held292,';';
''', b'A;R:11:7:7:3;'),
]

CASES += [(
    'nested-prefix-get-and-notice-precede-computed-rhs',
    r'''<?php
error_reporting(0);
function rhsPriority292() { echo 'V;'; return 2; }
class PrefixPriority292 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G;'; return [1=>5]; }
    public function offsetSet(mixed $offset, mixed $value): void { echo 'WRONGSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'WRONGUNSET;'; }
}

$o292=new PrefixPriority292;
set_error_handler(function($n,$m) { echo 'N;'; return true; },8);
$a292=($o292[1][1]=rhsPriority292());
$b292=($o292[1][1]+=rhsPriority292());
restore_error_handler();
echo 'R:',$a292,':',$b292,';';
'''.encode(),
    b'V;G;N;V;G;N;R:2:7;',
)]

CASES += [(
    'compound-self-cv-capture-preserves-old-object-type-before-get',
    r'''<?php
error_reporting(0);
class CompoundSelfCaptured292 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G;'; $GLOBALS['o292']=17; return 5; }
    public function offsetSet(mixed $offset, mixed $value): void { echo 'WRONGSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'WRONGUNSET;'; }
}

$o292=new CompoundSelfCaptured292; $r292=9;
try { $r292=($o292[1]+=$o292); }
catch(TypeError $e) { echo 'C:',(int)($e->getMessage()==='Unsupported operand types: int + CompoundSelfCaptured292'),':',$o292,':',$r292,';'; }
'''.encode(),
    b'G;C:1:17:9;',
)]

CASES += [(
    'nested-unset-alias-keeps-old-reference-after-variable-recreation',
    r'''<?php
error_reporting(0);
class FirstUnset292 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool {return false;}
 public function offsetGet(mixed $offset): mixed {return null;}
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {echo 'F:',(int)($offset===null),';';}
}
class SecondUnset292 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool {return false;}
 public function offsetGet(mixed $offset): mixed {return null;}
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {echo 'S:',(int)($offset===null),';';}
}
class AliasUnset292 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G;'; $row=[1=>&$GLOBALS['child292']]; unset($GLOBALS['o292']); return $row; }
    public function offsetSet(mixed $offset, mixed $value): void { echo 'WRONGSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'WRONGUNSET;'; }
}

$child292=new FirstUnset292; $held292=&$child292; $replacement292=new SecondUnset292; $o292=new AliasUnset292;
set_error_handler(function($n,$m) {if($n===8) {echo 'N;'; return true;} echo 'U;'; unset($GLOBALS['child292']); $GLOBALS['child292']=$GLOBALS['replacement292']; $GLOBALS['missing292']=7; return true;});
unset($o292[1][1][$missing292]);
restore_error_handler(); echo 'R:',(int)($held292!==$child292),':',(int)($child292===$replacement292),':',$missing292,';';
'''.encode(),
    b'G;N;U;F:1;R:1:1:7;',
)]

CASES += [(
    'ordinary-array-direct-unset-float-notice-keeps-selected-key-without-count',
    r'''<?php
error_reporting(0);
$row292=[1=>5,3=>7]; $key292=1.5;
set_error_handler(function($n,$m) {echo 'D;'; $GLOBALS['key292']=3; return true;});
unset($row292[$key292]);
restore_error_handler();
echo 'R:',(int)isset($row292[1]),':',$row292[3],':',$key292,';';
'''.encode(),
    b'D;R:0:7:3;',
)]

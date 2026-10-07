"""Original ordinary by-value ArrayAccess writable-consumer discriminators."""


def source(name, body, *, get, set='', before=''):
    return ("<?php\nerror_reporting(0);\n" + before +
            f"class {name} implements ArrayAccess {{\n" +
            " public function offsetExists(mixed $offset): bool { return true; }\n" +
            " public function offsetGet(mixed $offset): mixed { " + get + " }\n" +
            " public function offsetSet(mixed $offset,mixed $value): void { " + set + " }\n" +
            " public function offsetUnset(mixed $offset): void {}\n" +
            "}\n" + body).encode()


CASES = [
    ('direct-compound-get-r-then-set-does-not-emit-indirect-notice',
     source('CompoundPlain292', """
$o292=new CompoundPlain292;
set_error_handler(function($n,$m){echo 'WRONG;';return true;});
$r292=($o292[1.5]+=5);
restore_error_handler();echo 'R:',$r292,';';
""", get="echo 'G:',(int)($offset===1.5),';'; return 13;",
            set="echo 'S:',(int)($offset===1.5),':',$value,';';"),
     b'G:1;S:1:18;R:18;'),
    ('direct-append-compound-passes-null-to-get-and-set',
     source('CompoundAppend292', """
$o292=new CompoundAppend292;
set_error_handler(function($n,$m){echo 'WRONG;';return true;});
$r292=($o292[]+=3);
restore_error_handler();echo 'R:',$r292,';';
""", get="echo 'G:',(int)($offset===null),';'; return 9;",
            set="echo 'S:',(int)($offset===null),':',$value,';';"),
     b'G:1;S:1:12;R:12;'),
    ('pre-and-post-updates-use-get-temporary-without-set',
     source('UpdateTemporary292', """
$o292=new UpdateTemporary292;
set_error_handler(function($n,$m){echo 'N:',(int)($n===8),';';return true;});
$x292=++$o292[1];$y292=$o292[1]--;
restore_error_handler();echo 'R:',$x292,':',$y292,';';
""", get="echo 'G;';return 7;",set="echo 'WRONG;';"),
     b'G;N:1;G;N:1;R:8:7;'),
    ('nested-null-get-temp-autoinits-before-final-float-key',
     source('NullTemporary292', """
$o292=new NullTemporary292;
set_error_handler(function($n,$m){echo $n===8?'N;':'D;';return true;});
$r292=($o292[1][2.5]=17);
restore_error_handler();echo 'R:',$r292,':',(int)isset($o292),';';
""", get="echo 'G;';return null;",set="echo 'WRONG;';"),
     b'G;N;D;R:17:1;'),
    ('returned-array-depth-three-writes-only-owned-temporary',
     source('DeepTemporary292', """
$o292=new DeepTemporary292;
set_error_handler(function($n,$m){echo 'N;';return true;});
$r292=($o292[1][2][3]=17);
restore_error_handler();echo 'R:',$r292,':',$a292[2][3],';';
""", before="$seed292=5;$a292=[2=>[3=>$seed292]];\n",
            get="echo 'G;';return $GLOBALS['a292'];",set="echo 'WRONG;';"),
     b'G;N;R:17:5;'),
    ('returned-inner-arrayaccess-object-skips-indirect-notice',
     source('OuterObject292', """
$inner292=new InnerObject292;$o292=new OuterObject292;
set_error_handler(function($n,$m){echo 'WRONG;';return true;});
$r292=($o292[1][2]=17);
restore_error_handler();echo 'R:',$r292,':',$stored292,';';
""", before="""class InnerObject292 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool {return true;}
 public function offsetGet(mixed $offset): mixed {return null;}
 public function offsetSet(mixed $offset,mixed $value): void {echo 'S:',$offset,':',$value,';';$GLOBALS['stored292']=$value;}
 public function offsetUnset(mixed $offset): void {}
}
""", get="echo 'G;';return $GLOBALS['inner292'];",set="echo 'WRONG;';"),
     b'G;S:2:17;R:17:17;'),
    ('nested-unset-null-get-still-demands-final-missing-key',
     source('UnsetNullTemporary292', """
$o292=new UnsetNullTemporary292;
set_error_handler(function($n,$m){if($n===8){echo 'N;';}else{echo 'U;';$GLOBALS['last292']=7;}return true;});
unset($o292[1][$last292]);
restore_error_handler();echo 'R:',$last292,';';
""", get="echo 'G;';return null;"),
     b'G;N;U;R:7;'),
    ('compound-missing-key-and-rhs-demand-before-get-latch-null',
     source('MissingCompound292', """
$o292=new MissingCompound292;
set_error_handler(function($n,$m){if($m==='Undefined variable $key292'){echo 'K;';$GLOBALS['key292']=99;}else{echo 'V;';$GLOBALS['rhs292']=17;}return true;});
$r292=($o292[$key292]+=$rhs292);
restore_error_handler();echo 'R:',$r292,':',$key292,':',$rhs292,';';
""", get="echo 'G:',(int)($offset===null),';';return 13;",
            set="echo 'S:',(int)($offset===null),':',$value,';';"),
     b'K;V;G:1;S:1:13;R:13:99:17;'),
]

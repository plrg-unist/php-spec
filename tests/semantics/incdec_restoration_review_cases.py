"""Independent old-cell, wrapper and destructor-mutation originals."""

SHOW = """function show($v) {
    if ($v===true) echo 'T'; elseif ($v===false) echo 'F';
    elseif ($v===null) echo 'N'; else echo $v;
}"""


def kept(initial, expression, handler_throw=False):
    handler_end = "throw $GLOBALS['first'];" if handler_throw else 'return true;'
    return f"""<?php
class D {{function __destruct() {{
    echo 'D:',$GLOBALS['keep']===$this,':',$GLOBALS['x']===41,';';
    $GLOBALS['keep']=99;
}}}}
{SHOW}
$first=new Exception('first');
function h($n,$m,$f,$l) {{
    echo 'H:',$n,';';$GLOBALS['x']=&$GLOBALS['peer'];$GLOBALS['keep']=new D;
    {handler_end}
}}
set_error_handler('h');$x={initial};$keep=&$x;$peer=41;$v=100;
try {{$v={expression};echo 'R:';show($v);echo ';';}}
catch(Throwable $e) {{echo 'C:',$e===$first,':',$v,';';}}
echo 'X:';show($x);echo ';K:';show($keep);echo ';P:';show($peer);echo ';E;';
""".encode()


def shared(initial, expression, wrapper):
    install = "$GLOBALS['peer']=new D;$GLOBALS['x']=&$GLOBALS['peer'];" if wrapper else "$GLOBALS['x']=new D;$GLOBALS['peer']=$GLOBALS['x'];"
    return f"""<?php
class D {{function __destruct() {{
    echo 'D:',$GLOBALS['x']===true,':',$GLOBALS['x']==='Ba0',';';
}}}}
{SHOW}
function h($n,$m,$f,$l) {{echo 'H:',$n,';';{install}return true;}}
set_error_handler('h');$x={initial};$peer=41;$v={expression};
echo 'R:';show($v);echo ';X:';show($x);echo ';P:',$peer instanceof D,';A;';
unset($peer);echo 'E;';
""".encode()


CASES = {
    'review-old-cell-caller-rebind-pre': kept('true', '++$x'),
    'review-old-cell-caller-rebind-post': kept('false', '$x--'),
    'review-old-cell-caller-rebind-string': kept("'Az9'", '++$x'),
    'review-old-cell-caller-rebind-throw': kept('true', '$x++', True),
    'review-shared-object-pre': shared('true', '++$x', False),
    'review-shared-object-post-string': shared("'Az9'", '$x++', False),
    'review-surviving-wrapper-pre': shared('true', '++$x', True),
    'review-surviving-wrapper-post-string': shared("'Az9'", '$x++', True),
    'review-destructor-resurrection': b"""<?php
class D {function __destruct() {
    echo 'D:',$GLOBALS['x']===$this,';';$GLOBALS['calls']++;
    $GLOBALS['escaped']=$this;
}}
function h($n,$m,$f,$l) {echo 'H;';$GLOBALS['x']=new D;return true;}
set_error_handler('h');$calls=0;$x=true;$v=++$x;
echo 'R:',$v===true,':',$x===true,':',$escaped instanceof D,':',$calls,';';
unset($escaped);echo 'E:',$calls,';';
""",
    'review-array-destructor-write': b"""<?php
class D {function __destruct() {
    if(isset($GLOBALS['x'])) echo 'D:',$GLOBALS['x']===true,';';
    else echo 'D:absent;';
    $GLOBALS['x']=99;
}}
function h($n,$m,$f,$l) {echo 'H;';$GLOBALS['x']=[new D];return true;}
set_error_handler('h');$x=true;$keep=&$x;$v=++$x;
echo 'R:',$v===true,':',$x===true,':',$keep===true,';E;';
""",
    'review-destructor-late-property-source': b"""<?php
class C {public int $p=0;}
class D {function __destruct() {
    echo 'D:',$GLOBALS['keep']===$this,';';$GLOBALS['keep']=7;
    $GLOBALS['c']->p=&$GLOBALS['keep'];
}}
function h($n,$m,$f,$l) {$GLOBALS['x']=new D;return true;}
$c=new C;$x=true;$keep=&$x;set_error_handler('h');$v=++$x;
echo 'R:',$v===true,':',$x===true,':',$keep===true,':',$c->p===true,';E;';
""",
    'review-destructor-rebind-caller': b"""<?php
class D {function __destruct() {
    echo 'D:',$GLOBALS['x']===$this,';';$GLOBALS['x']=&$GLOBALS['peer'];
}}
function h($n,$m,$f,$l) {$GLOBALS['x']=new D;return true;}
$x=true;$peer=41;set_error_handler('h');$v=++$x;
echo 'R:',$v===true,':',$x===true,':',$peer===41,';E;';
""",
    'review-destructor-new-object-write': b"""<?php
class E {function __destruct() {echo 'Z;';}}
class D {function __destruct() {
    echo 'D:',$GLOBALS['x']===$this,';';$GLOBALS['x']=new E;
}}
function h($n,$m,$f,$l) {$GLOBALS['x']=new D;return true;}
$x=true;set_error_handler('h');$v=++$x;
echo 'R:',$v===true,':',$x===true,';E;';
""",
}

for name, initial, expression in (
        ('review-destructor-exit-bool', 'true', '++$x'),
        ('review-destructor-exit-string', "'Az9'", '$x++')):
    CASES[name] = f"""<?php
class D {{function __destruct() {{echo 'D:',$GLOBALS['x']===$this,';';exit('Q;');}}}}
function h($n,$m,$f,$l) {{$GLOBALS['x']=new D;return true;}}
function s() {{echo 'S:',$GLOBALS['x']===true,':',$GLOBALS['x']==='Ba0',';';}}
register_shutdown_function('s');set_error_handler('h');$x={initial};$v={expression};
echo 'WRONG;';
""".encode()

for name, probe in (
        ('review-array-reverse-identical', "true===$GLOBALS['x']"),
        ('review-array-notidentical', "$GLOBALS['x']!==41"),
        ('review-array-effectful-left', "probe_touch()===$GLOBALS['x']")):
    CASES[name] = f"""<?php
function probe_touch() {{echo 'F;';$GLOBALS['x']=99;return true;}}
class D {{function __destruct() {{echo 'D:',{probe},';';$GLOBALS['x']=99;}}}}
function h($n,$m,$f,$l) {{echo 'H;';$GLOBALS['x']=[new D];return true;}}
set_error_handler('h');$x=true;$v=++$x;
echo 'R:',$v===true,':',$x===true,';E;';
""".encode()

CASES['review-array-destructor-cv-isset-write'] = b"""<?php
class D {function __destruct() {
    global $x;
    if(isset($x)) echo 'D-cv:',$x===true,';';
    else echo 'D-cv:absent;';
    $x=99;
}}
function h($n,$m,$f,$l) {echo 'H;';$GLOBALS['x']=[new D];return true;}
set_error_handler('h');$x=true;$keep=&$x;$v=++$x;
echo 'R:',$v===true,':',$x===true,':',$keep===true,';E;';
"""

BOUNDARIES = {
    'review-destructor-late-property-source': 'increment/decrement restoration target is expired or constrained',
    'review-destructor-rebind-caller': 'increment/decrement destructor changed restored target ownership',
    'review-destructor-new-object-write': 'increment/decrement destructor changed restored target ownership',
    'review-destructor-exit-bool': 'increment/decrement warning exit continuation',
    'review-destructor-exit-string': 'increment/decrement warning exit continuation',
}

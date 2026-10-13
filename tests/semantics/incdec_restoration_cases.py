"""Next native-first obligations: destructor work before scalar restoration."""

SHOW = '''function show($v) {
    if ($v===true) echo 'T'; elseif ($v===false) echo 'F';
    elseif ($v===null) echo 'N'; elseif ($v instanceof D) echo 'O';
    else echo $v;
}
'''
CASES = {}


def original(initial, expression, handler_throw=False, destructor='observe', reference=False):
    action = "throw $GLOBALS['second'];" if destructor == 'throw' else (
        "$GLOBALS['x']=99;" if destructor == 'write' else '')
    after_handler = "throw $GLOBALS['first'];" if handler_throw else 'return true;'
    alias = '$keep=&$x;' if reference else ''
    return ('''<?php
class D { public function __destruct() {
    if (isset($GLOBALS['x'])) echo 'D:',$GLOBALS['x'] instanceof D,':',$GLOBALS['x']===true,';';
    else echo 'D:absent;';
    ''' + action + '''
} }
''' + SHOW + f'''$first=new Exception('first');$second=new Exception('second');
function h($n,$m,$f,$l) {{ echo 'H:',$n,';';$GLOBALS['x']=new D;{after_handler} }}
set_error_handler('h');$x={initial};{alias}$v=100;
try {{$v={expression};echo 'R:';show($v);echo ';';}}
catch(Throwable $e) {{echo 'C:',$e===$first,':',$e===$second,':',$e->getPrevious()===$first,':',$v,';';}}
echo 'X:';show($x);echo ';';
try {{unset($x);}} catch(Throwable $e) {{echo 'U:',$e===$second,';';}}
echo 'E;';
''').encode()


for mode, expression in {'pre-inc': '++$x', 'post-inc': '$x++',
                         'pre-dec': '--$x', 'post-dec': '$x--'}.items():
    CASES[mode + '-object-string'] = original("'Az9'", expression)
    CASES[mode + '-object-write-bool'] = original('true', expression, destructor='write')
    CASES[mode + '-object-throw-bool'] = original('true', expression, destructor='throw')

for mode, expression in (('pre-dec', '--$x'), ('post-dec', '$x--')):
    CASES[mode + '-object-null-handler-throw'] = original('null', expression, handler_throw=True)
    CASES[mode + '-object-throw-empty'] = original("''", expression, destructor='throw')

for mode, expression in (('pre-inc', '++$x'), ('post-dec', '$x--')):
    CASES[mode + '-object-both-throw-bool'] = original('true', expression, handler_throw=True, destructor='throw')
    CASES[mode + '-object-string-handler-throw'] = original("'Az9'", expression, handler_throw=True, destructor='throw')
    CASES[mode + '-object-retained-reference'] = original('true', expression, reference=True)

for name, initial, expression, action in (
        ('pre-inc-unique-wrapper-string', "'Az9'", '++$x', ''),
        ('post-dec-unique-wrapper-bool', 'true', '$x--', "$GLOBALS['x']=99;")):
    CASES[name] = f'''<?php
class D {{function __destruct() {{
    echo 'D:',$GLOBALS['x']===$this,';';{action}
}}}}
{SHOW}
function h($n,$m,$f,$l) {{
    echo 'H:',$n,';';$GLOBALS['peer']=new D;
    $GLOBALS['x']=&$GLOBALS['peer'];unset($GLOBALS['peer']);return true;
}}
set_error_handler('h');$x={initial};$v={expression};
echo 'R:';show($v);echo ';X:';show($x);echo ';E;';
'''.encode()

CASES['pre-inc-array-ordered-throw'] = b'''<?php
class D {function __construct(public int $n) {}
function __destruct() {
    echo 'D:',$this->n,':',$GLOBALS['x']===true,';';
    if($this->n===1) throw $GLOBALS['second'];$GLOBALS['x']=99;
}}
function h($n,$m,$f,$l) {echo 'H;';$GLOBALS['x']=[new D(1),new D(2)];return true;}
$second=new Exception('second');$x=true;$v=100;set_error_handler('h');
try {$v=++$x;echo 'WRONG;';}
catch(Throwable $e) {echo 'C:',$e===$second,':',$v,';';}
echo 'X:',$x===true,';E;';
'''

CASES['pre-inc-plain-object-handler-throw'] = b'''<?php
class Plain {}
function h($n,$m,$f,$l) {
    echo 'H:',$n,';';$GLOBALS['x']=new Plain;throw $GLOBALS['first'];
}
$first=new Exception('first');$x=true;$v=100;set_error_handler('h');
try {$v=++$x;echo 'WRONG;';}
catch(Throwable $e) {echo 'C:',$e===$first,':',$v,':',$x===true,';';}
echo 'E;';
'''

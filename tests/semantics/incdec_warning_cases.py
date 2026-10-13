"""Original direct-CV updates across scalar warning handlers."""

MODES = {'pre-inc': '++$x', 'post-inc': '$x++',
         'pre-dec': '--$x', 'post-dec': '$x--'}
SHOW = '''function show($v) {
    if ($v===true) { echo 'T'; }
    elseif ($v===false) { echo 'F'; }
    elseif ($v===null) { echo 'N'; }
    else { echo $v; }
}
'''
CASES = {}

for mode, expression in MODES.items():
    values = {'bool-true': 'true', 'bool-false': 'false', 'string': "'Az9'", 'empty': "''"}
    if mode.endswith('dec'):
        values['null'] = 'null'
    for name, initial in values.items():
        for action in ('return', 'throw'):
            callback = "throw $GLOBALS['failure'];" if action == 'throw' else 'return true;'
            CASES[mode + '-' + name + '-' + action] = ('''<?php
''' + SHOW + f'''$failure=new Exception('original');
function h($n,$m,$f,$l) {{ echo 'H:',$n,':',$m,':',$l,';'; $GLOBALS['x']=41; {callback} }}
set_error_handler('h'); $x={initial}; $v=100;
try {{ $v={expression}; echo 'V:'; show($v); echo ';'; }}
catch (Exception $e) {{ echo 'C:',$e===$failure,':',$v,';'; }}
echo 'X:'; show($x); echo ';';
''').encode()

    CASES[mode + '-reference-rebind'] = ('''<?php
''' + SHOW + f'''function h($n,$m,$f,$l) {{ echo 'H:',$n,';'; $GLOBALS['x']=&$GLOBALS['peer']; $GLOBALS['keep']=41; return true; }}
set_error_handler('h'); $x='Az9'; $keep=&$x; $peer='peer';
$v={expression}; echo 'V:'; show($v); echo ';X:'; show($x); echo ';K:'; show($keep); echo ';P:'; show($peer);
''').encode()

for mode, expression in (('pre-inc', '++$x'), ('post-dec', '$x--')):
    CASES[mode + '-new-reference'] = ('''<?php
''' + SHOW + f'''function h($n,$m,$f,$l) {{ echo 'H:',$n,';'; $GLOBALS['x']=&$GLOBALS['peer']; return true; }}
set_error_handler('h'); $x='Az9'; $peer='peer';
$v={expression}; echo 'V:'; show($v); echo ';X:'; show($x); echo ';P:'; show($peer);
$x='after'; echo ';P2:'; show($peer);
''').encode()
    CASES[mode + '-array-replacement'] = ('''<?php
''' + SHOW + f'''function h($n,$m,$f,$l) {{ echo 'H:',$n,';'; $GLOBALS['x']=[21,22]; return true; }}
set_error_handler('h'); $x='Az9'; $v={expression}; echo 'V:'; show($v); echo ';X:'; show($x);
''').encode()

for initial, expression in (('true', '++$x'), ("'Az9'", '$x--')):
    for action in ('return', 'throw'):
        name = 'bool' if initial == 'true' else 'string'
        callback = "throw $GLOBALS['failure'];" if action == 'throw' else 'return true;'
        CASES['destructor-' + name + '-' + action] = f'''<?php
class D {{ public function __destruct() {{ echo 'D;'; }} }}
$failure=new Exception('original');
function h($n,$m,$f,$l) {{ echo 'H:',$n,';'; $GLOBALS['x']=new D; echo 'R;'; {callback} }}
set_error_handler('h'); $x={initial}; $v=100;
try {{ $v={expression}; echo 'V:',$v,';'; }} catch (Exception $e) {{ echo 'C:',$e===$failure,':',$v,';'; }}
echo 'X:',$x instanceof D,';'; unset($x); echo 'END;';
'''.encode()

for name, expression in (('fallback', '++$x'), ('suppressed', '@(++$x)')):
    CASES[name] = ('''<?php
''' + SHOW + f'''function h($n,$m,$f,$l) {{ echo 'H:',$n,';'; $GLOBALS['x']=41; return false; }}
set_error_handler('h'); $x='Az9'; $v={expression}; echo 'V:'; show($v); echo ';X:'; show($x);
''').encode()

for name, initial in (('null', 'null'), ('integer', '7'), ('numeric-string', "'7'")):
    CASES['quiet-' + name] = ('''<?php
''' + SHOW + f'''function h($n,$m,$f,$l) {{ echo 'WRONG;'; return true; }}
set_error_handler('h'); $x={initial}; $v=++$x; echo 'V:'; show($v); echo ';X:'; show($x);
''').encode()

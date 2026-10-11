"""Original sources distinguishing CV reads, copied values and owned references."""
OPERATORS = ('%', '<<', '>>', '&', '|', '^')
CASES = {}

for index, operator in enumerate(OPERATORS):
    CASES['copy-right-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H:",$n,";"; $GLOBALS['b']=3; return true; }}
set_error_handler('h'); $a=5.75; $b=2;
$v=$a {operator} (+$b); echo "V:",$v,":",$b;
'''.encode()
    CASES['copy-left-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H:",$n,";"; $GLOBALS['a']=true; return true; }}
set_error_handler('h'); $a=5.75; $b=[];
try {{ $v=(+$a) {operator} $b; echo "wrong"; }} catch (TypeError $e) {{ echo $e->getMessage(),";"; }}
echo $a===true;
'''.encode()
    CASES['literal-left-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H:",$n,";"; $GLOBALS['b']=3; return true; }}
set_error_handler('h'); $b=2;
$v=5.75 {operator} $b; echo "V:",$v,":",$b;
'''.encode()
    CASES['refassign-right-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H:",$n,";"; $GLOBALS['b']=&$GLOBALS['c']; return true; }}
set_error_handler('h'); $a=5.75; $old=2; $b=9; $c=3;
$v=$a {operator} ($b=&$old); echo "V:",$v,":",$b,":",$old;
'''.encode()
    CASES['refcall-right-' + str(index)] = f'''<?php
function &rhs() {{ return $GLOBALS['b']; }}
function h($n,$m,$f,$l) {{ echo "H:",$n,";"; $GLOBALS['b']=&$GLOBALS['c']; return true; }}
set_error_handler('h'); $a=5.75; $b=2; $c=3;
$v=$a {operator} rhs(); echo "V:",$v,":",$b,":",$c;
'''.encode()

CASES.update({
    'both-copy-leading': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,":",$m,";"; $GLOBALS['a']='99.75tail'; $GLOBALS['b']=5; return true; }
set_error_handler('h'); $a='12.5tail'; $b=7;
$v=(true?$a:0) % (+$b); echo "V:",$v,":",$a,":",$b;
''',
    'copy-array-right': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,";"; $GLOBALS['a']=true; $GLOBALS['b']=0; return true; }
set_error_handler('h'); $a=5.75; $b=[1];
try { $v=$a % (true?$b:[]); echo "wrong"; } catch (TypeError $e) { echo $e->getMessage(),";"; }
echo $a===true,":",$b;
''',
    'refcall-left-failure': b'''<?php
function &lhs() { return $GLOBALS['a']; }
function h($n,$m,$f,$l) { echo "H:",$n,";"; $GLOBALS['a']=&$GLOBALS['c']; return true; }
set_error_handler('h'); $a=5.75; $c=true; $b=[];
try { $v=lhs() % $b; echo "wrong"; } catch (TypeError $e) { echo $e->getMessage(),";"; }
echo $a===true;
''',
    'refcall-right-throw': b'''<?php
$failure=new Exception('stop');
function &rhs() { return $GLOBALS['b']; }
function h($n,$m,$f,$l) { echo "H:",$n,";"; $GLOBALS['b']=&$GLOBALS['c']; throw $GLOBALS['failure']; }
set_error_handler('h'); $a=5.75; $b=2; $c=3;
try { $v=$a % rhs(); echo "wrong"; } catch (Exception $e) { echo $e===$failure,":",$b; }
''',
    'literal-string-left': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,":",$m,";"; $GLOBALS['b']=5; return true; }
set_error_handler('h'); $b=7; $v='12.5tail' % $b; echo "V:",$v,":",$b;
''',
})

for index in (0, 3):
    operator = OPERATORS[index]
    CASES['refassign-live-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H:",$n,";"; $GLOBALS['b']=&$GLOBALS['c']; $GLOBALS['old']=7; return true; }}
set_error_handler('h'); $a='12.5tail'; $old=2; $b=9; $c=3;
$v=$a {operator} ($b=&$old); echo "V:",$v,":",$b,":",$old;
'''.encode()

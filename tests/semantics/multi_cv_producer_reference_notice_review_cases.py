"""Independent duplicate-CV COW and compiled Notice-line witnesses."""
import hashlib


def source(namespace='', qualified=False, forward=False):
    prefix = '<?php\n'
    if namespace:
        prefix += 'namespace ' + namespace + ';\n'
    handler = (namespace + '\\' if namespace else '') + 'h'
    producer = ('\\' + namespace + '\\' if qualified else '') + 'make'
    make = "function make($saved,&$changed){$changed[0]=13;echo 'M:',$saved[0],':',$changed[0],';';return $saved;}\n"
    definitions = (
        "function h($n,$m,$file,$line){global $x;echo 'H:',$line,':',$x[0],';';$x[0]=17;return true;}\n"
        + ('' if forward else make)
        + "function &take(&$value){echo 'F:',$value[0],';';$value[0]=19;return $value;}\n"
    )
    execution = (
        "$x=[5];$copy=$x;set_error_handler('" + handler.replace('\\', '\\\\') + "',8);echo 'J;';\n"
        '$r=&take(' + producer + '(\n'
        '    $x,\n'
        '    $x\n'
        "));\n$r[0]=23;echo 'R:',$r[0],':',$x[0],':',$copy[0],';';unset($r,$x,$copy);\n"
    )
    return (prefix + definitions + execution + (make if forward else '')).encode()


NAMED_ID = 'named-prior-reference-duplicate-cv-runtime-namespace'
NAMED_SOURCE = b"""<?php
namespace ReviewNotice49\\Named;
function h($n,$m,$file,$line){global $x,$prefix;echo 'H:',$line,':',$x[0],':',$prefix,';';$x[0]=17;$prefix=29;return true;}
function make($saved,&$changed){$changed[0]=13;echo 'M:',$saved[0],':',$changed[0],';';return $saved;}
function &take(&$prefix,&$value){echo 'F:',$prefix,':',$value[0],';';$value[0]=19;$prefix=31;return $value;}
$x=[5];$copy=$x;$prefix=2;$prefixAlias=&$prefix;set_error_handler('ReviewNotice49\\\\Named\\\\h',8);echo 'N;';
$r=&take(prefix:$prefix,value:make(
    $x,
    $x
));
$r[0]=23;echo 'R:',$r[0],':',$x[0],':',$copy[0],':',$prefixAlias,';';unset($r,$x,$copy,$prefix,$prefixAlias);
"""

CASES = {
    'duplicate-cv-known-global': source(),
    'duplicate-cv-known-qualified-namespace': source('ReviewNotice49\\Known', qualified=True),
    'duplicate-cv-runtime-namespace-primary': source('ReviewNotice49\\Fallback'),
    'duplicate-cv-forward-global': source(forward=True),
    NAMED_ID: NAMED_SOURCE,
}

HASHES = {name: hashlib.sha256(value).hexdigest() for name, value in CASES.items()}
NATIVE_STDOUT_PATTERN = r'J;M:5:13;H:([0-9]+):13;F:5;R:23:17:5;'
NATIVE_NAMED_STDOUT_PATTERN = r'N;M:5:13;H:([0-9]+):13:2;F:29:5;R:23:17:5:31;'

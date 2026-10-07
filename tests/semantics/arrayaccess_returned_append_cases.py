"""Original returned-child simple append witnesses and pinned native observations."""


def access(name, getter, setter):
    return f'''class {name} implements ArrayAccess {{
    public function offsetExists(mixed $key): bool {{ echo 'WRONGEXISTS;'; return false; }}
    public function offsetGet(mixed $key): mixed {{ {getter} }}
    public function offsetSet(mixed $key, mixed $value): void {{ {setter} }}
    public function offsetUnset(mixed $key): void {{ echo 'WRONGUNSET;'; }}
}}
'''


GET_CHILD = '''echo 'G:', $key, ';';
        $held309 = $GLOBALS['child309'];
        $GLOBALS['rhs309'] = 17;
        unset($GLOBALS['outer309'], $GLOBALS['child309']);
        return $held309;'''

START = '''$rhs309 = 11;
$child309 = new Child309;
$outer309 = new Outer309;
'''

CASES = [{
    'id': 'returned-child-simple-append-live-cv-and-post-set-readback',
    'source': '<?php\n' + access('Child309', "echo 'WRONGGET;'; return 5;", '''
        echo 'S:', ($key === null ? 'N' : 'K'), ':', $value, ';';
        $GLOBALS['saved309'] = $value;
        $GLOBALS['rhs309'] = 21;''') + access('Outer309', GET_CHILD, "echo 'WRONGOUTERSET;';") + START + '''$r309 = ($outer309['root'][] = $rhs309);
echo 'R:', $r309, ':', $saved309, ':', $rhs309, ':', (isset($outer309) ? 1 : 0), ':', (isset($child309) ? 1 : 0), ';';
''',
}, {
    'id': 'returned-child-simple-append-keeps-old-rhs-reference-cell',
    'source': '<?php\n' + access('Child309', "echo 'WRONGGET;'; return 5;", '''
        echo 'S:', ($key === null ? 'N' : 'K'), ':', $value, ';';
        $GLOBALS['saved309'] = $value;
        $GLOBALS['rhs309'] =& $GLOBALS['new309'];
        $GLOBALS['alias309'] = 25;''') + access('Outer309', GET_CHILD, "echo 'WRONGOUTERSET;';") + START + '''$alias309 =& $rhs309;
$new309 = 31;
$r309 = ($outer309['root'][] = $rhs309);
echo 'R:', $r309, ':', $saved309, ':', $rhs309, ':', $alias309, ':', $new309, ':', (isset($outer309) ? 1 : 0), ':', (isset($child309) ? 1 : 0), ';';
''',
}, {
    'id': 'returned-child-simple-append-eager-object-rhs-survives-root-retirement',
    'source': '''<?php
class Payload309 { public $number = 13; }
function make309() {
    echo 'RHS;';
    $value309 = new Payload309;
    $GLOBALS['payload309'] = $value309;
    return $value309;
}
''' + access('Child309', "echo 'WRONGGET;'; return 5;", '''
        echo 'S:', ($key === null ? 'N' : 'K'), ':', $value->number, ';';
        $value->number = 29;
        $GLOBALS['saved309'] = $value;''') + access('Outer309', '''
        echo 'G:', $key, ';';
        $held309 = $GLOBALS['child309'];
        unset($GLOBALS['outer309'], $GLOBALS['child309'], $GLOBALS['payload309']);
        return $held309;''', "echo 'WRONGOUTERSET;';") + '''$child309 = new Child309;
$outer309 = new Outer309;
$r309 = ($outer309['root'][] = make309());
echo 'R:', $r309->number, ':', ($r309 === $saved309 ? 1 : 0), ':', (isset($payload309) ? 1 : 0), ':', (isset($outer309) ? 1 : 0), ':', (isset($child309) ? 1 : 0), ';';
''',
}, {
    'id': 'returned-child-simple-append-set-throw-keeps-chain-and-source-lines',
    'source': '<?php\n' + access('Child309', "echo 'WRONGGET;'; return 5;", '''
        echo 'S:', ($key === null ? 'N' : 'K'), ':', $value, ';';
        $GLOBALS['saved309'] = $value;
        throw new Exception('set309', 0, new Exception('previous309'));''') + access('Outer309', GET_CHILD, "echo 'WRONGOUTERSET;';") + START + '''try {
    $r309 = (
        $outer309['root'][] =
            $rhs309
    );
} catch (Throwable $e309) {
    echo 'C:', ($e309 instanceof Exception ? 'Exception' : 'Other'), ':', $e309->getMessage(), ':', $e309->getLine(), ':', ($e309->getFile() === __FILE__ ? 1 : 0), ';';
    $p309 = $e309->getPrevious();
    if ($p309 !== null) {
        echo 'P:', $p309->getMessage(), ':', $p309->getLine(), ':', ($p309->getFile() === __FILE__ ? 1 : 0), ':', ($p309->getPrevious() === null ? 0 : 1), ';';
    }
}
echo 'R:', $saved309, ':', $rhs309, ':', (isset($r309) ? 1 : 0), ':', (isset($outer309) ? 1 : 0), ':', (isset($child309) ? 1 : 0), ';';
''',
}]

OBSERVED_STDOUT = {
    'returned-child-simple-append-live-cv-and-post-set-readback': b'G:root;S:N:17;R:21:17:21:0:0;',
    'returned-child-simple-append-keeps-old-rhs-reference-cell': b'G:root;S:N:17;R:25:17:31:25:31:0:0;',
    'returned-child-simple-append-eager-object-rhs-survives-root-retirement': b'RHS;G:root;S:N:13;R:29:1:0:0:0;',
    'returned-child-simple-append-set-throw-keeps-chain-and-source-lines': b'G:root;S:N:17;C:Exception:set309:8:1;P:previous309:8:1:0;R:17:17:0:0:0;',
}

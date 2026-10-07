"""Independent returned-child append controls and pinned native observations."""

from arrayaccess_returned_append_cases import CASES as AUTHOR_CASES, access


GET_CHILD = """echo 'G:', $key, ';';
        $held309 = $GLOBALS['child309'];
        unset($GLOBALS['outer309'], $GLOBALS['child309']);
        return $held309;"""

START = """$child309 = new Child309;
$outer309 = new Outer309;
"""

CASES = [{
    'id': 'returned-child-simple-append-missing-rhs-latches-null-and-selected-child',
    'source': '<?php\n' + access('Child309', "echo 'WRONGGET;'; return 5;", """
        echo 'S:', ($key === null ? 'N' : 'K'), ':', ($value === null ? 'N' : 'V'), ';';
        $GLOBALS['saved309'] = $value;
        $GLOBALS['rhs309'] = 41;""") + access('Replacement309', "echo 'WRONGREPLACEMENTGET;'; return 5;", "echo 'WRONGREPLACEMENTSET;';") + access('Outer309', GET_CHILD, "echo 'WRONGOUTERSET;';") + START + """set_error_handler(function ($level309, $message309, $file309, $line309) {
    echo 'H:', ($level309 === E_WARNING ? 1 : 0), ':', ($message309 === 'Undefined variable $rhs309' ? 1 : 0), ':', ($file309 === __FILE__ ? 1 : 0), ':', $line309, ';';
    $GLOBALS['rhs309'] = 23;
    $GLOBALS['child309'] = new Replacement309;
    return true;
});
$r309 = ($outer309['root'][] = $rhs309);
echo 'R:', ($r309 === null ? 'N' : 'V'), ':', ($saved309 === null ? 'N' : 'V'), ':', $rhs309, ':', (isset($outer309) ? 1 : 0), ':', ($child309 instanceof Replacement309 ? 1 : 0), ';';
""",
}, {
    'id': 'returned-child-simple-append-missing-rhs-throw-skips-set',
    'source': '<?php\n' + access('Child309', "echo 'WRONGGET;'; return 5;", "echo 'WRONGSET;';") + access('Outer309', GET_CHILD, "echo 'WRONGOUTERSET;';") + START + """set_error_handler(function ($level309, $message309, $file309, $line309) {
    echo 'H:', ($level309 === E_WARNING ? 1 : 0), ':', ($message309 === 'Undefined variable $rhs309' ? 1 : 0), ':', ($file309 === __FILE__ ? 1 : 0), ':', $line309, ';';
    $GLOBALS['rhs309'] = 23;
    throw new Exception('rhs309', 0, new Exception('previous309'));
});
try {
    $r309 = (
        $outer309['root'][] =
            $rhs309
    );
} catch (Throwable $e309) {
    echo 'C:', ($e309 instanceof Exception ? 'Exception' : 'Other'), ':', $e309->getMessage(), ':', $e309->getLine(), ':', ($e309->getFile() === __FILE__ ? 1 : 0), ';';
    $p309 = $e309->getPrevious();
    echo 'P:', $p309->getMessage(), ':', $p309->getLine(), ':', ($p309->getPrevious() === null ? 0 : 1), ';';
}
echo 'R:', $rhs309, ':', (isset($r309) ? 1 : 0), ':', (isset($outer309) ? 1 : 0), ':', (isset($child309) ? 1 : 0), ';';
""",
}, {
    'id': 'returned-array-simple-append-keeps-real-row-and-late-rhs',
    'source': '<?php\n' + access('Outer309', """
        echo 'G:', $key, ';';
        return ['ref' => &$GLOBALS['target309']];""", "echo 'WRONGOUTERSET;';") + """$target309 = [];
$rhs309 = 11;
$outer309 = new Outer309;
set_error_handler(function ($level309, $message309) {
    echo 'N:', $level309, ';';
    $GLOBALS['rhs309'] = 17;
    unset($GLOBALS['outer309']);
    return true;
}, E_NOTICE);
$r309 = ($outer309['root']['ref'][] = $rhs309);
restore_error_handler();
echo 'R:', $r309, ':', $target309[0], ':', $rhs309, ':', (isset($outer309) ? 1 : 0), ';';
""",
}]

# Separate source counterpart: the original empty append dimension is preserved.
CASES.append({
    'id': 'returned-child-final-explicit-null-keeps-dimension-source-form',
    'source': AUTHOR_CASES[0]['source'].replace("$outer309['root'][]", "$outer309['root'][null]", 1),
})

OBSERVED_STDOUT = {
    'returned-child-simple-append-missing-rhs-latches-null-and-selected-child': b'G:root;H:1:1:1:34;S:N:N;R:N:N:41:0:1;',
    'returned-child-simple-append-missing-rhs-throw-skips-set': b'G:root;H:1:1:1:26;C:Exception:rhs309:22:1;P:previous309:22:0;R:23:0:0:0;',
    'returned-child-final-explicit-null-keeps-dimension-source-form': b'G:root;S:N:17;R:21:17:21:0:0;',
    'returned-array-simple-append-keeps-real-row-and-late-rhs': b'G:root;N:8;R:17:17:17:0;',
}

"""Default RIGHT handlers are independent of ordinary field/table layouts."""
OPS = {'mod': '%', 'shl': '<<', 'shr': '>>', 'and': '&', 'or': '|', 'xor': '^'}
SEVEN = {'mod': 5, 'shl': 1536, 'shr': 0, 'and': 4, 'or': 15, 'xor': 11}


def ones(label, count):
    return label.encode() + b':' + b':'.join([b'1'] * count) + b';'


def source(op, mode):
    assert op in OPS and mode in ('repair', 'retain', 'late-left', 'cell', 'table', 'throw')
    cell = mode == 'cell'
    table = mode == 'table'
    throws = mode == 'throw'
    fails = mode in ('retain', 'late-left') or (cell and op == 'xor')
    result = 100 if fails or throws else (SEVEN[op] if mode == 'repair' else 2)
    drop_value = result if cell or table else 100
    right_test = '$rightAlias instanceof RightBox' if cell else ('$right instanceof RightBox' if fails else '$right === ' + ('5' if table else '7'))
    left_test = '$left instanceof stdClass' if mode == 'late-left' else '$left === 99'
    target = "$GLOBALS['rightAlias']" if cell else "$GLOBALS['right']"
    lines = [
        '<?php',
        "class Token { public function __destruct() { $GLOBALS['tokenDrops']++; echo 'T:', $GLOBALS['v'] === $GLOBALS['dropValue'], ':', $GLOBALS['strings'] === 0, ';'; } }",
        'class RightBase extends stdClass { public $payload; }',
        'class RightBox extends RightBase {',
        "    public function __toString(): string { $GLOBALS['strings']++; echo 'BAD-S;'; return '5'; }",
        '    public function __destruct() {',
        "        $GLOBALS['drops']++; echo 'D:', $GLOBALS['v'] === $GLOBALS['dropValue'], ':', $this->payload instanceof Token, ':', $GLOBALS['weakChild']->get() === $this->payload, ':', $GLOBALS['strings'] === 0, ';';",
        "        if ($GLOBALS['rewrite']) { echo 'WRITE:', $GLOBALS['right'] === 5, ';'; $GLOBALS['right'] = 7; }",
        '    }',
        '}',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls']++;",
        "    echo 'H:', $level === E_DEPRECATED, ':', $line === 40, ':', $message === 'Implicit conversion from float 12.5 to int loses precision', ':', $file === __FILE__, ':', $GLOBALS['left'] === 12.5, ':', $GLOBALS['weakRight']->get() === " + target + ", ':', $GLOBALS['weakChild']->get() === " + target + "->payload, ':', $GLOBALS['strings'] === 0, ';';",
        "    $GLOBALS['left'] = " + ('new stdClass()' if mode == 'late-left' else '99') + ';',
        ("    $GLOBALS['right'] =& $GLOBALS['newRight'];" if cell else ("    $GLOBALS['right'] = 5;" if mode in ('repair', 'table', 'throw') else '    // Retain the standard-handler object.')),
        ("    throw $GLOBALS['failure'];" if throws else
         "    echo 'W:', " + ("$GLOBALS['left'] instanceof stdClass" if mode == 'late-left' else "$GLOBALS['left'] === 99") + ", ':', " + ("$GLOBALS['right'] === 5" if cell or table else ("$GLOBALS['right'] instanceof RightBox" if fails else "$GLOBALS['right'] === 7")) + ", ':', $GLOBALS['weakRight']->get() " + ('=== null' if mode in ('repair', 'table') else '=== ' + target) + ", ':', $GLOBALS['weakChild']->get() " + ('=== null' if mode == 'repair' else '!== null') + ", ':', $GLOBALS['strings'] === 0, ':', $GLOBALS['drops'] === " + ('1' if mode == 'repair' else '0') + ", ':', $GLOBALS['tokenDrops'] === " + ('1' if mode == 'repair' else '0') + ", ';';"),
        ('    // Supplied throw does not return.' if throws else '    return false;'),
        '}',
        '$left = 12.5; $right = ' + ('new stdClass()' if table else 'new RightBox()') + '; $right->payload = new Token(); ' + ('$rightAlias =& $right; ' if cell else '') + '$newRight = 5;',
        ('$right->label = 7; $snapshot = (array)$right;' if table else '// Use inline declared storage.'),
        '$weakRight = WeakReference::create($right); $weakChild = WeakReference::create($right->payload);',
        '$calls = 0; $strings = 0; $drops = 0; $tokenDrops = 0; $v = 100; $dropValue = ' + str(drop_value) + '; $rewrite = ' + ('true' if mode in ('repair', 'throw') else 'false') + ';',
    ]
    lines += [''] * (35 - len(lines))
    lines += [
        "$failure = new Exception('standard-right');",
        "set_error_handler('h');",
        'try {',
        '    $v =',
        f'        $left {OPS[op]} $right;',
    ]
    if throws:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $failure, ':', $e->getLine() === 36, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === 99, ':', $right === 7, ':', $weakRight->get() === null, ':', $weakChild->get() === null, ':', $strings === 0, ';';",
        ]
    elif fails:
        message = ('stdClass' if mode == 'late-left' else 'int') + ' ' + OPS[op] + ' RightBox'
        lines += [
            "    echo 'BAD-R;';",
            '} catch (TypeError $e) {',
            "    echo 'C:', $e->getMessage() === 'Unsupported operand types: " + message + "', ':', $e->getLine() === 40, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', " + left_test + ", ':', " + right_test + ", ':', $weakChild->get() !== null, ':', $strings === 0, ':', $drops === 0, ';';",
        ]
    else:
        lines += [
            "    echo 'R:', $v === " + str(result) + ", ':', $calls === 1, ':', $left === 99, ':', " + ('$right === 5' if cell or table else '$right === 7') + ", ':', $strings === 0, ':', " + ('$weakChild->get() !== null' if cell or table else '$weakChild->get() === null') + ", ';';",
            "} catch (Throwable $e) { echo 'BAD-E;';",
        ]
    lines += ['}', "finally { echo 'F;'; }", 'restore_error_handler();']
    if cell:
        lines += ['$rightAlias = null;']
    elif table:
        lines += ['$snapshot = null;']
    elif fails:
        lines += ['$right = null;']
    lines += [
        "echo 'A:', $weakRight->get() === null, ':', $weakChild->get() === null, ':', $drops === " + ('0' if table else '1') + ", ':', $tokenDrops === 1, ':', $strings === 0, ':', $calls === 1, ';';",
        "echo 'END:', $v === " + str(result) + ", ':', " + left_test + ";",
    ]
    assert lines[35] == "$failure = new Exception('standard-right');" and lines[39] == f'        $left {OPS[op]} $right;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {**{op + '-repair-destructor': source(op, 'repair') for op in OPS},
         'mod-retain-class': source('mod', 'retain'), 'and-late-left-class': source('and', 'late-left'),
         'mod-cell-rebind': source('mod', 'cell'), 'xor-cell-rebind': source('xor', 'cell'),
         'mod-materialized-stdclass': source('mod', 'table'), 'shl-supplied-throw': source('shl', 'throw')}
EXPECTED_STDOUT = {}
for name in CASES:
    repair = name.endswith('repair-destructor')
    throws = name.endswith('supplied-throw')
    cell = '-cell-' in name
    table = name.endswith('materialized-stdclass')
    fails = name in ('mod-retain-class', 'and-late-left-class', 'xor-cell-rebind')
    release = ones('D', 4) + (b'WRITE:1;' if repair or throws else b'') + ones('T', 2)
    EXPECTED_STDOUT[name] = (ones('H', 8) + (release if repair or throws else b'') +
        (b'' if throws else ones('W', 7)) + (ones('C', 10) if fails or throws else ones('R', 6)) + b'F;' +
        (ones('T', 2) if table else release if cell or fails else b'') + ones('A', 6) + b'END:1:1')


def control():
    lines = ['<?php', 'function h($level, $message, $file, $line) {',
             "    $GLOBALS['calls']++; echo 'H:', $level === E_DEPRECATED, ':', $line === 40, ':', $file === __FILE__, ':', $message === 'Implicit conversion from float 12.5 to int loses precision', ';';",
             "    $GLOBALS['left'] = 99; $GLOBALS['right'] = 5; return true;", '}',
             '$left = 12.5; $right = new stdClass(); $calls = 0; $v = 100;']
    lines += [''] * (39 - len(lines))
    lines += ["$v = $left % $right; echo 'R:', $v === 2, ':', $calls === 1, ':', $left === 99, ':', $right === 5;", 'restore_error_handler();']
    lines[37] = "set_error_handler('h');"
    assert lines[39].startswith('$v =')
    return ('\n'.join(lines) + '\n').encode()


CASES['empty-stdclass-control'] = control()
EXPECTED_STDOUT['empty-stdclass-control'] = ones('H', 4) + b'R:1:1:1:1'
CONTROLS = {'empty-stdclass-control'}


def expected_stderr(name, path):
    return b'' if name in CONTROLS or name.endswith('supplied-throw') else b'Deprecated: Implicit conversion from float 12.5 to int loses precision in ' + bytes(path) + b' on line 40\n'

# Representative unchanged gates; candidate execution still selects every source.
BASELINE_SELECTION = (
    'mod-repair-destructor', 'xor-cell-rebind',
    'mod-materialized-stdclass', 'empty-stdclass-control',
)

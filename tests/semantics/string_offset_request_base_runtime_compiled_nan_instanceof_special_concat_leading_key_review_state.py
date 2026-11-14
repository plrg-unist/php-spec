#!/usr/bin/env python3
"""Independent consumer-only NaN authority and unchanged truth boundaries."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_compiled_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_compiled_nan_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    if tree[0] in ('NAN', 'FLOAT', 'STRING', 'COMPILED'):
        return
    children = tree[2:3] if tree[0] == 'CAST' else tree[1:3] if tree[0] in ('IDENTICAL', 'ADD') else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_nan = S_after.CODE[0]', 'ppool_peer_nan = S_after.POOLS[0]',
              'pcunit_peer_nan = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[0] != 'INSTANCEOF':
            continue
        origin, child = 'porigin_' + tag, 'porigin_' + tag + '_0'
        target, child_path = 'pcpath_peer_nan_root', 'pcpath_peer_nan_child'
        value = 'PFLOAT n_compiled_nan_' + tag + '_0'
        requested = '$ptascii(' + json.dumps(tree[-1]) + ')'
        guards += [origin + ' = PORIGIN 0 ' + target, child + ' = PORIGIN 0 ' + child_path,
                   '$string_read_runtime_instanceof_operand(S_after, ' + child + ') = (' + value + ')',
                   '$number_bool(NFLOAT n_compiled_nan_' + tag + '_0) = (true, true)',
                   '$truth_value(S_after, ' + value + ', 5) =/= S_after[.RESULT = KNOWN (PBOOL true)]',
                   '$string_read_runtime_value(S_after, ' + child + ') = eps',
                   '$string_read_runtime_bytes(S_after, ' + child + ') = eps']

        def refused(state):
            return ['$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                    '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                    '$string_read_request_base_saved(' + state + ', pstringread) = eps']

        mutations = [
            ('root_drop', 'S_after[.CODE[0] = pcode_peer_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nan.EXPRESSIONS, ' + target + ', eps)]]'),
            ('root_flip', 'S_after[.CODE[0] = pcode_peer_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nan.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_nan[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_nan.EXPRESSIONS]]'),
            ('names', 'S_after[.CODE[0] = pcode_peer_nan[.NAMES = eps]]'),
            ('fallback', 'S_after[.CODE[0] = pcode_peer_nan[.NAMES = (CODENAME ' + target + ' (' + requested + ') ($ptascii("Other"))) :: pcode_peer_nan.NAMES]]'),
            ('parent_precision', 'S_after[.POOLS[0] = ppool_peer_nan[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_nan.CONSTANTS]]'),
            ('child_precision', 'S_after[.POOLS[0] = ppool_peer_nan[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_nan.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_nan[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NScalarInt (INTEGER 0) eps)) :: pcunit_peer_nan.OCCURRENCES]]'),
            ('context', 'S_after[.CONSTCONTEXT = ({ORIGIN ' + origin + ', LINE 5, FACTS eps})]'),
        ]
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('throw', 'THROWN "Error" ($ptascii("peer_nan")) 5')):
            mutations.append((label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PBOOL false)]'))
        for label, replacement in mutations:
            state = 'S_peer_nan_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
        for label, flag in (('drop', 'eps'), ('flip', '(false)')):
            state = 'S_peer_nan_child_' + label
            expected, outcome = 'eps', refused(state)
            if index in (1, 2, 3) and label == 'flip':
                expected = '(' + value + ')'
                outcome = ['$string_read_runtime_value(' + state + ', ' + origin + ') = (PBOOL false)',
                           '$string_read_runtime_bytes(' + state + ', porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)',
                           '$string_read_request_base_saved(' + state + ', pstringread) = $string_read_request_base_saved(S_after, pstringread)']
            guards += [state + ' = S_after[.CODE[0] = pcode_peer_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nan.EXPRESSIONS, ' + child_path + ', ' + flag + ')]]',
                       '$compiled_read(' + state + ', ' + child + ') = eps',
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + child + ') = ' + expected,
                       *outcome]
        if index == 0:
            for bits in (18444492273895866368, 9221120237041090561, 9218868437227405313, 18446744073709551616):
                state, raw = 'S_peer_nan_bits_' + str(bits), 'PFLOAT ' + str(bits)
                expected = '(' + raw + ')' if bits < 2**64 else 'eps'
                guards += [state + ' = S_after[.POOLS[0] = ppool_peer_nan[.CONSTANTS = (PCONSTANT ' + child_path + ' (' + raw + ')) :: ppool_peer_nan.CONSTANTS]]',
                           '$string_read_runtime_instanceof_operand(' + state + ', ' + child + ') = ' + expected,
                           '$string_read_runtime_value(' + state + ', ' + child + ') = eps',
                           '$string_read_runtime_bytes(' + state + ', ' + child + ') = eps',
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = ' + ('(PBOOL false)' if bits < 2**64 else 'eps')]
            guards += ['S_peer_nan_raw_name = S_after[.SOURCES[0] = pcunit_peer_nan[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprConstFetch (NName (BYTES "T3RoZXI=") eps) eps)) :: pcunit_peer_nan.OCCURRENCES]]',
                       '$string_read_runtime_instanceof_operand(S_peer_nan_raw_name, ' + child + ') = (' + value + ')',
                       *refused('S_peer_nan_raw_name')]
            name = '(NName (BYTES "U2VMZg==") eps)'
            guards += ['porigin_' + tag + '_name = PORIGIN 0 pcpath_peer_nan_name',
                       'S_peer_nan_keyword = S_after[.SOURCES[0] = pcunit_peer_nan[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprInstanceof expression_' + tag + '_0 ' + name + ' eps)) :: (PCOCCURRENCE pcpath_peer_nan_name ' + name + ') :: pcunit_peer_nan.OCCURRENCES]][.CODE[0] = pcode_peer_nan[.NAMES = (CODENAME ' + target + ' ($ptascii("SeLf")) eps) :: pcode_peer_nan.NAMES]]',
                       *refused('S_peer_nan_keyword')]
    if index == 0:
        for number, (name, fixture, original, target, node, accepted, nan) in enumerate(CONTROLS):
            state, origin = 'S_peer_nan_control_' + str(number), 'porigin_peer_nan_control_' + str(number)
            normal = state + '_normal'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + ('(PBOOL false)' if accepted else 'eps'),
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + ('(eps)' if accepted else 'eps')]
            if nan:
                child = 'porigin_peer_nan_control_child_' + str(number)
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                           '$string_read_runtime_value(' + normal + ', ' + child + ') = eps',
                           '$string_read_runtime_bytes(' + normal + ', ' + child + ') = eps']
                if name == 'late_namespace_inf':
                    guards += ['$compiled_read(' + normal + ', ' + child + ') = eps',
                               '$compiled_identity_value(' + normal + ', ' + child + ') = eps',
                               '$string_read_runtime_instanceof_operand(' + normal + ', ' + child + ') = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    raw = [
        ('nan', '', 'NAN', 'Missing', True, True),
        ('negative_nan', '', '-NAN', '\\stdClass', True, True),
        ('late_namespace_inf', 'namespace Ns;', 'INF-INF', 'namespace\\Missing', False, True),
        ('arithmetic_nan', 'namespace Ns;', '\\INF-\\INF', 'namespace\\Missing', True, True),
        ('power_nan', 'use stdClass as Alias;', 'NAN**2', 'Alias', True, True),
        ('scalar_nan', '', 'NAN+false', 'stdClass', True, True),
        ('int_fallback', '', '1', 'stdClass', True, False),
        ('float_fallback', '', 'INF', 'stdClass', True, False),
        ('bool_fallback', '', 'false', 'stdClass', True, False),
        ('null_fallback', '', 'null', 'stdClass', True, False),
        ('string_fallback', '', '"x"', 'stdClass', True, False),
        ('emitted_nan', '', '((float)(!INF))*INF', 'stdClass', True, True),
        ('array', '', '[1]', 'stdClass', False, False),
        ('object', '', 'new stdClass', 'stdClass', False, False),
        ('dynamic', '$left=NAN;', '$left', '$target', False, True),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, prefix, operand, target, accepted, nan in raw:
        paths[name].write_bytes(('<?php ' + prefix + '$x=(' + operand + ') instanceof ' + target + ';\n').encode())
    root = runner.ROOT
    profile = json.loads((root / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = runner.Worker([str(root / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(root / '.tools/php-file.so'), str(root / 'frontend/worker.php')], prep / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()}) for name, path in paths.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = runner.Worker([str(root / '_build/default/adapter/main.exe'), str(root)], prep / 'adapter')
    try:
        checked = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for name, row in parsed.items()}
        assert all(row['ok'] for row in checked.values())
    finally:
        adapter.close()
    for name, prefix, operand, target_name, accepted, nan in raw:
        target, node = next((path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                            for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_Instanceof')
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, accepted, nan))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += helpers.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Current four histories add independent consumer-only NaN bit/identity, missing/flipped child and root CODE, exact target/fallback/line/source/precision, NORMAL/CONSTCONTEXT, keyword and saved-receipt controls. Fifteen checked-source source0 controls cover genuine NaN unary/arithmetic/POWER/scalar children, ordinary fallback types, namespace/alias targets and owning/dynamic refusal. The later arithmetic/unary/completed-POWER operand certificates promote the emitted-NaN control and coherent false-CODE INF-INF, +NAN and NAN**2 children; missing CODE and other flips retain refusal. Namespaced late-fallback INF operands lack compiled NaN facts and remain refused; fully qualified INF operands supply the genuine positive namespace case. Negative/payload/signaling NaN compiler outputs preserve instanceof=false while general VALUE/BYTE and quiet truth stay refused; invalid64 bits refuse. Existing raw ConstFetch compiler-output trust is explicit. Native originals reused once; no general truth/formatter/compiler/owner or held-boundary widening.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

#!/usr/bin/env python3
"""Independent quiet string-unary authority, malformed guards and continuations."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_numeric_string_unary_special_concat_leading_key_cases as cases
import string_offset_request_base_nested_unary_numeric_special_concat_leading_key_review_state as prior

runner = prior.runner
QUIET_CONTROL = 'mixed-quiet-numeric-string-unary-special'
CONST_CONTROL = 'mixed-constfetch-unary-special'
CONCAT_CONTROL = 'mixed-nonliteral-string-unary-special'


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    text = ('  +1 ', '1', '1.00000000000001', '4.00000000000001e0')[index]
    bits = (4607182418800017453, 4616189618054758411)[max(0, index - 2)]
    numeric = 'PINT 1' if index < 2 else 'PFLOAT ' + str(bits)
    number = 'NINT 1' if index < 2 else 'NFLOAT ' + str(bits)
    literal = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
    node = 'NScalarInt (INTEGER 1)' if index < 2 else 'NScalarFloat (FLOAT text_terminal)'
    replacements = {
        'expression_terminal = ' + node + ' metadata_terminal':
            'expression_terminal = NScalarString (BYTES text_terminal) metadata_terminal',
        '$parser_literal_at(expression_terminal, 14) = (' + numeric + ')':
            '$parser_literal_at(expression_terminal, 14) = (' + literal + ')',
        '$compiled_read(S, porigin_terminal) = (' + numeric + ')':
            '$compiled_read(S, porigin_terminal) = (' + literal + ')'}
    unary = 'POSITIVE' if index == 3 else 'NEGATIVE'
    result = 'pvalue_child_unary' if index < 2 else '(PFLOAT ' + str(13830554455654793261 if index == 2 else bits) + ')'
    replacements['$unary_apply(S, ' + unary + ', ' + numeric + ', 0) = S[.RESULT = KNOWN ' + result + ']'] = (
        '$unary_apply(S, ' + unary + ', ' + literal + ', 0) = S[.RESULT = KNOWN ' + result + ']')
    for old, new in replacements.items():
        assert checks.count(old) == 1, old
        checks[checks.index(old)] = new
    checks += [
        '$base64(text_terminal) = $ptascii(' + json.dumps(text) + ')',
        '$numeric_string($base64(text_terminal)) = FULLNUM (' + number + ')',
        '$coerce_number(' + literal + ') = COERCED (' + number + ') false']

    # Keep the real compiler fact, but replace its actual unary source node.
    # An already Unsupported state makes the line-zero warning observationally
    # inert, so unary_apply equality alone would incorrectly accept this case.
    origin = 'porigin_child_unary' if index < 2 else 'porigin_inner_unary'
    ast = 'NExprUnaryPlus' if index == 3 else 'NExprUnaryMinus'
    leading = text + 'x'
    encoded = base64.b64encode(leading.encode()).decode()
    output = '4' if index == 3 else '-1'
    guards = runner.lines(r'''
S_hostile = S_after[.COMPLETION = UNSUPPORTED "missing source line"]
''') + [
        'porigin_string_unary = ' + origin,
        'porigin_string_unary = PORIGIN n_string_unit pcpath_string_unary',
        '$compiled_read(S_hostile, porigin_string_unary) = (pvalue_string_unary)',
        '$compiled_precision(S_hostile, (porigin_string_unary)) = (14)',
        '$compiled_special_concat_bytes(S_hostile, porigin_string_unary) = ($ptascii("' + output + '"))',
        '$coerce_number(PSTRING ($ptascii(' + json.dumps(leading) + '))) = COERCED (' + number + ') true',
        '$unary_apply(S_hostile, ' + unary + ', PSTRING ($ptascii(' + json.dumps(leading) + ')), 0) = S_hostile[.RESULT = KNOWN pvalue_string_unary]',
        'expression_leading = ' + ast + ' (NScalarString (BYTES ' + json.dumps(encoded) + ') metadata_terminal) metadata_string_unary',
        'S_leading = S_hostile[.SOURCES = [{ID n_string_unit, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_string_unary expression_leading)])}]]',
        '$origin_node(S_leading.SOURCES, porigin_string_unary) = (expression_leading)',
        '$compiled_read(S_leading, porigin_string_unary) = (pvalue_string_unary)',
        '$compiled_precision(S_leading, (porigin_string_unary)) = (14)',
        '$unary_apply(S_leading, ' + unary + ', PSTRING ($ptascii(' + json.dumps(leading) + ')), 0) = S_leading[.RESULT = KNOWN pvalue_string_unary]',
        '$compiled_special_concat_bytes(S_leading, porigin_string_unary) = eps']
    # Bind the real unary node before reusing its source metadata above.
    at = next(i for i, check in enumerate(guards) if check.startswith('expression_leading = '))
    guards[at:at] = [
        '$origin_node(S_hostile.SOURCES, porigin_string_unary) = (' + ast + ' expression_terminal metadata_string_unary)']
    checks += guards
    return checks, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = prior.compiler_conditions({name: checked[name] for name in (prior.STRING_CONTROL, prior.BINARY_CONTROL) if name in checked}, paths)
    for index, name in enumerate((QUIET_CONTROL, CONST_CONTROL, CONCAT_CONTROL)):
        if name not in checked:
            continue
        state, origin = 'S_fresh_' + str(index), 'porigin_fresh_' + str(index)
        path, unary = 'pcpath_fresh_' + str(index), 'porigin_fresh_unary_' + str(index)
        child, expression = 'porigin_fresh_child_' + str(index), 'expression_fresh_child_' + str(index)
        checks += [
            state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
            state + '.COMPLETION = BUDGET',
            '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (' + path + ')',
            origin + ' = PORIGIN 0 ' + path,
            '$compiled_read(' + state + ', ' + origin + ') = (PSTRING ($ptascii("1x")))',
            '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + unary + ')',
            '$origin_node(' + state + '.SOURCES, ' + unary + ') = (NExprUnaryPlus ' + expression + ' metadata_fresh_' + str(index) + ')',
            '$compiled_read(' + state + ', ' + unary + ') = (' + ('PFLOAT 4607182418800017408' if index == 0 else 'PINT 1') + ')',
            '$origin_child((' + unary + '), [PCFIELD 0]) = (' + child + ')',
            '$origin_node(' + state + '.SOURCES, ' + child + ') = (' + expression + ')',
            '$parser_literal_at(' + expression + ', 14) = ' + ('(PSTRING ($ptascii("1")))' if index == 2 else 'eps')]
        if index == 0:
            checks += [
                expression + ' = NExprUnaryPlus expression_quiet_string metadata_quiet_unary',
                '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                '$origin_child((' + child + '), [PCFIELD 0]) = (porigin_quiet_string)',
                '$origin_node(' + state + '.SOURCES, porigin_quiet_string) = (expression_quiet_string)',
                'expression_quiet_string = NScalarString (BYTES text_quiet_string) metadata_quiet_string',
                '$base64(text_quiet_string) = $ptascii("1.0")',
                '$coerce_number(PSTRING ($base64(text_quiet_string))) = COERCED (NFLOAT 4607182418800017408) false',
                '$compiled_special_concat_bytes(' + state + ', ' + unary + ') = ($ptascii("1"))',
                '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("1x"))',
                '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))']
        else:
            ast = ('NExprConstFetch name_fresh metadata_child_fresh_1' if index == 1 else
                   'NExprBinaryOpConcat expression_left_fresh expression_right_fresh metadata_child_fresh_2')
            checks += [
                expression + ' = ' + ast,
                '$compiled_read(' + state + ', ' + child + ') = (' + ('PBOOL true' if index == 1 else 'PSTRING ($ptascii("1"))') + ')',
                '$compiled_special_concat_bytes(' + state + ', ' + unary + ') = ' + ('($ptascii("1"))' if index == 1 else 'eps'),
                '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ' + ('($ptascii("1x"))' if index == 1 else 'eps'),
                '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = ' + ('PSTRING_CARRIER INTERNED_STRING' if index == 1 else 'PSTRING') + ' ($ptascii("1x"))']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.floating.__file__), Path(prior.prior.floating.prior.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = {
        prior.STRING_CONTROL: runner.CONTROLS[prior.STRING_CONTROL],
        prior.BINARY_CONTROL: b"<?php $x = (+(1+0.0) . false) . 'x';\n",
        QUIET_CONTROL: b'<?php $x = (+(+"1.0") . false) . \'x\';\n',
        CONST_CONTROL: b"<?php $x = (+true . false) . 'x';\n",
        CONCAT_CONTROL: b"<?php $x = (+('1'.'') . false) . 'x';\n"}
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual quiet full-numeric string-leaf unary source-state fixtures retain exact bytes, typing/bits, own facts/precision, terminal-pool omission, borrowed owners, supplied throw, later bounds and budgets. Malformed warningful leaves retain plausible unary facts and a line-zero state-equality trap. Current compiler controls admit quiet numeric-string unary, certified unary arithmetic and Boolean ConstFetch while refusing warningful strings and nonliteral numeric CONCAT. Older cuts retain their identities without source/native replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

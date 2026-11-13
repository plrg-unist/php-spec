#!/usr/bin/env python3
"""Independent numeric CONCAT unary byte, warning and borrowed-owner checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_numeric_string_concat_unary_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_string_concat_unary_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
LITERAL_CONTROL = 'literal-numeric-concat'
WARNING_CONTROL = 'leading-numeric-concat'
CONTROLS = {
    prior.STRING_CONTROL: prior.CONTROLS[prior.STRING_CONTROL],
    LITERAL_CONTROL: prior.prior.CONTROLS['unary-numeric-concat'],
    WARNING_CONTROL: b"<?php $x = (+('1tail'.false) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tags = ['string_unary'] if index < 3 else ['string_unary', 'string_unary_child_l']
    guards = prior.unary_guards(tags, ('1x', '-1x', '0x', '-4x')[index])
    if index == 0:
        guards += runner.lines(r'''
porigin_string_unary = PORIGIN n_warning_unit pcpath_warning_unary
porigin_string_unary_child = PORIGIN n_warning_unit pcpath_warning_concat
$origin_child((porigin_string_unary_child), [PCFIELD 0]) = (PORIGIN n_warning_unit pcpath_warning_literal)
$origin_child((porigin_string_unary_child), [PCFIELD 1]) = (PORIGIN n_warning_unit pcpath_warning_special)
$compiled_read(S_after, porigin_string_unary) = (PINT 1)
S_warning_host = S_after[.COMPLETION = UNSUPPORTED "missing source line"][.RESULT = KNOWN (PINT 1)]
expression_warning_literal = NScalarString (BYTES "MXRhaWw=") metadata_string_unary_child_l
expression_warning_concat = NExprBinaryOpConcat expression_warning_literal expression_string_unary_child_r metadata_string_unary_child
expression_warning_unary = NExprUnaryPlus expression_warning_concat metadata_string_unary
S_warning = S_warning_host[.POOLS = $special_review_pools(S_warning_host.POOLS, porigin_string_unary_child, (PSTRING ($ptascii("1tail1"))))][.SOURCES = [{ID n_warning_unit, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_warning_unary expression_warning_unary), (PCOCCURRENCE pcpath_warning_concat expression_warning_concat), (PCOCCURRENCE pcpath_warning_literal expression_warning_literal), (PCOCCURRENCE pcpath_warning_special expression_string_unary_child_r)])}]]
$origin_node(S_warning.SOURCES, porigin_string_unary) = (expression_warning_unary)
$origin_node(S_warning.SOURCES, porigin_string_unary_child) = (expression_warning_concat)
$compiled_precision(S_warning, (porigin_string_unary)) = (14)
$compiled_precision(S_warning, (porigin_string_unary_child)) = (14)
$parser_literal_at(expression_warning_concat, 14) = eps
$compiled_read(S_warning, porigin_string_unary_child) = (PSTRING ($ptascii("1tail1")))
$compiled_read(S_warning, porigin_string_unary) = (PINT 1)
$compiled_special_concat_bytes(S_warning, porigin_string_unary_child) = ($ptascii("1tail1"))
$coerce_number(PSTRING ($ptascii("1tail1"))) = COERCED (NINT 1) true
$unary_apply(S_warning, POSITIVE, PSTRING ($ptascii("1tail1")), 0) = S_warning
$compiled_special_concat_bytes(S_warning, porigin_string_unary) = eps
''')
    checks += guards
    return checks, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = prior.compiler_conditions({prior.STRING_CONTROL: checked[prior.STRING_CONTROL]}, paths) if prior.STRING_CONTROL in checked else []
    if LITERAL_CONTROL in checked:
        checks += prior.prior.compiler_conditions({'unary-numeric-concat': checked[LITERAL_CONTROL]}, {'unary-numeric-concat': paths[LITERAL_CONTROL]})
    if WARNING_CONTROL not in checked:
        return checks
    checks += ['S_warning_control = $php_run(' + checked[WARNING_CONTROL]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[WARNING_CONTROL])).decode()) + ')']
    return checks + runner.lines(r'''
S_warning_control.COMPLETION = BUDGET
$special_review_concat_path(S_warning_control.SOURCES[0].OCCURRENCES) = (pcpath_warning_control)
porigin_warning_control = PORIGIN 0 pcpath_warning_control
$compiled_read(S_warning_control, porigin_warning_control) = eps
$compiled_special_concat_bytes(S_warning_control, porigin_warning_control) = eps
$origin_child((porigin_warning_control), [PCFIELD 0, PCFIELD 0]) = (porigin_warning_control_unary)
$compiled_read(S_warning_control, porigin_warning_control_unary) = eps
$compiled_special_concat_bytes(S_warning_control, porigin_warning_control_unary) = eps
$origin_child((porigin_warning_control_unary), [PCFIELD 0]) = (porigin_warning_control_child)
$origin_node(S_warning_control.SOURCES, porigin_warning_control_child) = (expression_warning_control_child)
$parser_literal_at(expression_warning_control_child, 14) = eps
$compiled_read(S_warning_control, porigin_warning_control_child) = (PSTRING ($ptascii("1tail")))
$compiled_special_concat_bytes(S_warning_control, porigin_warning_control_child) = ($ptascii("1tail"))
$coerce_number(PSTRING ($ptascii("1tail"))) = COERCED (NINT 1) true
''')


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.arithmetic, source.runner, prior, prior.source, prior.source.arithmetic, prior.source.runner, prior.prior, prior.prior.arithmetic, prior.prior.constants, prior.prior.nested, prior.prior.prior, prior.prior.arithmetic.floating, prior.strings)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh numeric mixed-CONCAT unary source-state fixtures retain independent source/kind, missing/wrong fact, both precision-direction and equal-byte distinct-header owner controls. Leading-zero/space bytes, signed/zero indices, supplied throw, nested arithmetic, negative bounds and budgets retain their actual source histories. A malformed certified leading-number CONCAT keeps the actual unary fact and an already abrupt state makes pure unary application unchanged, but explicit quiet coercion still refuses the certificate. Fresh compiler controls directly promote only the quiet PSTRING case while retaining parser-literal CONCAT and warningful string refusals. Historical campaigns are not replayed or aggregated.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

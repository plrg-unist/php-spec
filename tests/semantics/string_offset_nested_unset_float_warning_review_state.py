#!/usr/bin/env python3
"""Independent raw FLOAT bits, compiler facts and Warning continuation checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_review_state as review
import string_offset_nested_unset_float_warning_cases as cases

INDEX = 2


def base(value):
    return ('BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base* z_base)) (KNOWN '
        + value + ') z) (KNOWN (PINT 7)) z_outer')


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    bits = cases.KEY_BITS[name]
    wrong = bits + 1 if INDEX == 2 else bits - 1
    checks = review.assertions(program, path, cases.OUTPUTS[name], INDEX % 2 == 1)
    old = 'S_review_E.BASE = ' + base('PNULL')
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S_review_E.BASE = ' + base('(PFLOAT ' + str(bits) + ')')
    checks += [
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_float_key)',
        'porigin_float_key = PORIGIN 0 pcpath_float_key',
        '$origin_node(S_review_E.SOURCES, porigin_float_key) = (NScalarFloat (FLOAT text_float_key) metadata_float_key)',
        '$hex_bits(text_float_key, 0) = ' + str(bits),
        '$compiled_read(S_review_E, porigin_float_key) = (PFLOAT ' + str(bits) + ')',
        '$compiled_identity_value(S_review_E, porigin_float_key) = (PFLOAT ' + str(bits) + ')',
        'S_review_E.POOLS = ppool_float :: ppool_float_tail*',
        'ppool_float.UNIT = 0',
        'S_review_E.CODE = pcode_float :: pcode_float_tail*',
        'pcode_float.UNIT = 0',
    ]
    controls = [
        *('$string_unset_warning_plan(S_review_E[.BASE = ' + base(value) + ']) = eps'
          for value in ('(PFLOAT ' + str(wrong) + ')', 'PNULL', '(PBOOL true)', '(PINT 0)', '(PINT 1)')),
        'S_float_pool = S_review_E[.POOLS = (ppool_float[.CONSTANTS = (PCONSTANT pcpath_float_key (PFLOAT ' + str(wrong) + ')) :: ppool_float.CONSTANTS]) :: ppool_float_tail*]',
        '$compiled_read(S_float_pool, porigin_float_key) = (PFLOAT ' + str(wrong) + ')',
        '$compiled_identity_value(S_float_pool, porigin_float_key) = (PFLOAT ' + str(wrong) + ')',
        '$string_unset_warning_source(S_float_pool, porigin_site, z) = eps',
        '$string_unset_warning_plan(S_float_pool) = eps',
        '~$call_task_valid(S_float_pool, STRING_UNSET_WARNING_RESULT porigin_site z)',
        'S_float_phase = S_review_E[.CODE = (pcode_float[.EXPRESSIONS = (CODEEXPR pcpath_float_key z false) :: pcode_float.EXPRESSIONS]) :: pcode_float_tail*]',
        '$compiled_read(S_float_phase, porigin_float_key) = eps',
        '$string_unset_warning_source(S_float_phase, porigin_site, z) = eps',
        '$string_unset_warning_plan(S_float_phase) = eps',
        '~$call_task_valid(S_float_phase, STRING_UNSET_WARNING_RESULT porigin_site z)',
    ]
    if INDEX == 2:
        for bits_positive in (0x000fffffffffffff, 0x0010000000000000,
                              0xfff0000000000000, 0x8000000000000000):
            controls.append('$string_unset_warning_literal(NScalarFloat (FLOAT "'
                + format(bits_positive, '016x') + '") eps, PFLOAT ' + str(bits_positive) + ')')
        for raw, value in (('fff8000000000000', 0xfff8000000000000),
                           ('7ff0000000000001', 0x7ff0000000000001),
                           ('10000000000000000', 1 << 64),
                           ('3ff8000000000000', bits + 1)):
            controls.append('~$string_unset_warning_literal(NScalarFloat (FLOAT "'
                + raw + '") eps, PFLOAT ' + str(value) + ')')
        controls += [
            '~$string_unset_warning_literal(NScalarFloat (FLOAT "3ff0000000000000") eps, PINT 1)',
            '~$string_unset_warning_literal(NExprUnaryPlus (NScalarFloat (FLOAT "0000000000000000") eps) eps, PFLOAT 0)',
        ]
        assert program.count('"3ff8000000000000"') == 1
        subnormal = program.replace('"3ff8000000000000"', '"0000000000000001"')
        encoded = json.dumps(base64.b64encode(bytes(path)).decode())
        controls += [
            'S_subnormal_I = $php_run(' + subnormal + ', 0, ' + encoded + ')',
            'S_subnormal_found = $review_null_seek(S_subnormal_I, "entry", 1000)',
            '$review_null_at(S_subnormal_found, "entry")',
            'S_subnormal_E = $review_null_running(S_subnormal_found)',
            'S_subnormal_E.BASE = ' + base('(PFLOAT 1)'),
            '$string_unset_warning_plan(S_subnormal_E) = ((porigin_subnormal, z))',
            '$origin_child((porigin_subnormal), [PCFIELD 0, PCFIELD 1]) = (porigin_subnormal_key)',
            '$compiled_read(S_subnormal_E, porigin_subnormal_key) = (PFLOAT 1)',
            '$compiled_identity_value(S_subnormal_E, porigin_subnormal_key) = (PFLOAT 1)',
            '$string_unset_warning_plan(S_subnormal_E[.BASE = ' + base('(PFLOAT 2)') + ']) = eps',
            '$call_task_valid(S_subnormal_E, STRING_UNSET_WARNING_RESULT porigin_subnormal z)',
            *review.public('S_subnormal_E'),
        ]
    return checks + controls, (30 if INDEX == 2 else 16) + len(controls)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(review.__file__), Path(cases.__file__), Path(cases.null.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (2, 5)
    prior = review.prior
    prior.NAME = tuple(cases.CASES)[INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.PREFIX = cases, conditions, review.PREFIX
    passed = prior.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'AL', 1
    report['derived_subnormal_full_authentication'] = INDEX == 2
    report['scope'] = ('Independent fractional-return/infinity-throw raw nonNaN FLOAT keys: '
        'exact bits, other nonNaN FLOAT/tag and pool/raw mismatches, disabled key CODE phase, '
        'source-only base mutation resume, same-Exception discard and whole/split equality. '
        'Return-only derived leaf boundaries and subnormal-AST full authentication are '
        'source0/native0, without subnormal or zero source agreement. Only fresh selected '
        'originals reuse saved native observations; accepted NULL/BOOL cuts are not renewed.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

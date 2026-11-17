#!/usr/bin/env python3
"""Independent unary-minus FLOAT key, source and Warning continuation checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_review_state as review
import string_offset_nested_unset_negative_float_warning_cases as cases

INDEX = 2


def base(value):
    return ('BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base* z_base)) (KNOWN '
        + value + ') z) (KNOWN (PINT 7)) z_outer')


def literal(bits):
    return 'NExprUnaryMinus (NScalarFloat (FLOAT "' + format(bits, '016x') + '") eps) eps'


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    bits, child = cases.KEY_BITS[name], cases.CHILD_BITS[name]
    checks = review.assertions(program, path, cases.OUTPUTS[name], INDEX % 2 == 1)
    old = 'S_review_E.BASE = ' + base('PNULL')
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S_review_E.BASE = ' + base('(PFLOAT ' + str(bits) + ')')
    checks += [
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_minus_key)',
        'porigin_minus_key = PORIGIN 0 pcpath_minus_key',
        '$origin_node(S_review_E.SOURCES, porigin_minus_key) = (NExprUnaryMinus (NScalarFloat (FLOAT text_minus_child) metadata_minus_child) metadata_minus_key)',
        '$origin_child((porigin_minus_key), [PCFIELD 0]) = (porigin_minus_child)',
        '$origin_node(S_review_E.SOURCES, porigin_minus_child) = (NScalarFloat (FLOAT text_minus_child) metadata_minus_child)',
        '$hex_bits(text_minus_child, 0) = ' + str(child),
        '$compiled_read(S_review_E, porigin_minus_key) = (PFLOAT ' + str(bits) + ')',
        '$compiled_identity_value(S_review_E, porigin_minus_key) = (PFLOAT ' + str(bits) + ')',
        'S_review_E.POOLS = ppool_minus :: ppool_minus_tail*',
        'ppool_minus.UNIT = 0',
        'S_review_E.CODE = pcode_minus :: pcode_minus_tail*',
        'pcode_minus.UNIT = 0',
        'S_review_E.SOURCES = pcunit_minus :: pcunit_minus_tail*',
        'pcunit_minus.ID = 0',
    ]
    controls = [
        *('$string_unset_warning_plan(S_review_E[.BASE = ' + base(value) + ']) = eps'
          for value in ('(PFLOAT ' + str(child) + ')', '(PFLOAT ' + str(bits - 1) + ')',
                        'PNULL', '(PBOOL true)', '(PINT (-1))')),
        'S_minus_pool = S_review_E[.POOLS = (ppool_minus[.CONSTANTS = (PCONSTANT pcpath_minus_key (PFLOAT ' + str(child) + ')) :: ppool_minus.CONSTANTS]) :: ppool_minus_tail*]',
        '$compiled_read(S_minus_pool, porigin_minus_key) = (PFLOAT ' + str(child) + ')',
        '$compiled_identity_value(S_minus_pool, porigin_minus_key) = eps',
        '$string_unset_warning_source(S_minus_pool, porigin_site, z) = eps',
        '$string_unset_warning_plan(S_minus_pool) = eps',
        '~$call_task_valid(S_minus_pool, STRING_UNSET_WARNING_RESULT porigin_site z)',
        'S_minus_phase = S_review_E[.CODE = (pcode_minus[.EXPRESSIONS = (CODEEXPR pcpath_minus_key z false) :: pcode_minus.EXPRESSIONS]) :: pcode_minus_tail*]',
        '$compiled_read(S_minus_phase, porigin_minus_key) = eps',
        '$string_unset_warning_source(S_minus_phase, porigin_site, z) = eps',
        '$string_unset_warning_plan(S_minus_phase) = eps',
        '~$call_task_valid(S_minus_phase, STRING_UNSET_WARNING_RESULT porigin_site z)',
        'S_minus_source = S_review_E[.SOURCES = (pcunit_minus[.OCCURRENCES = (PCOCCURRENCE pcpath_minus_key (NExprUnaryMinus (NScalarFloat (FLOAT "' + format(child + 1, '016x') + '") metadata_minus_child) metadata_minus_key)) :: pcunit_minus.OCCURRENCES]) :: pcunit_minus_tail*]',
        '$string_unset_warning_source(S_minus_source, porigin_site, z) = eps',
        '$string_unset_warning_plan(S_minus_source) = eps',
        '~$call_task_valid(S_minus_source, STRING_UNSET_WARNING_RESULT porigin_site z)',
    ]
    if INDEX == 2:
        for raw in (0, 1 << 63, 1, 0x000fffffffffffff, 0x0010000000000000,
                    0x7ff0000000000000, 0xfff0000000000000):
            controls.append('$string_unset_warning_literal(' + literal(raw)
                + ', PFLOAT ' + str(raw ^ (1 << 63)) + ')')
        for raw, value in ((child, child), (child + 1, bits),
                           (0, 0), (1 << 64, bits),
                           (0x7ff8000000000000, 0xfff8000000000000),
                           (0xfff0000000000001, 0x7ff0000000000001)):
            controls.append('~$string_unset_warning_literal(' + literal(raw)
                + ', PFLOAT ' + str(value) + ')')
        controls += [
            '~$string_unset_warning_literal(' + literal(child) + ', PINT (-1))',
            '~$string_unset_warning_literal(NExprUnaryPlus (NScalarFloat (FLOAT "3ff8000000000000") eps) eps, PFLOAT ' + str(child) + ')',
            '~$string_unset_warning_literal(NExprUnaryMinus (' + literal(child) + ') eps, PFLOAT ' + str(child) + ')',
        ]
        assert program.count('"3ff8000000000000"') == 1
        subnormal = program.replace('"3ff8000000000000"', '"0000000000000001"')
        encoded = json.dumps(base64.b64encode(bytes(path)).decode())
        controls += [
            'S_minus_subnormal_I = $php_run(' + subnormal + ', 0, ' + encoded + ')',
            'S_minus_subnormal_found = $review_null_seek(S_minus_subnormal_I, "entry", 1000)',
            '$review_null_at(S_minus_subnormal_found, "entry")',
            'S_minus_subnormal_E = $review_null_running(S_minus_subnormal_found)',
            'S_minus_subnormal_E.BASE = ' + base('(PFLOAT 9223372036854775809)'),
            '$string_unset_warning_plan(S_minus_subnormal_E) = ((porigin_minus_subnormal, z))',
            '$origin_child((porigin_minus_subnormal), [PCFIELD 0, PCFIELD 1]) = (porigin_minus_subnormal_key)',
            '$origin_child((porigin_minus_subnormal_key), [PCFIELD 0]) = (porigin_minus_subnormal_child)',
            '$origin_node(S_minus_subnormal_E.SOURCES, porigin_minus_subnormal_child) = (NScalarFloat (FLOAT "0000000000000001") metadata_minus_subnormal_child)',
            '$compiled_read(S_minus_subnormal_E, porigin_minus_subnormal_key) = (PFLOAT 9223372036854775809)',
            '$compiled_identity_value(S_minus_subnormal_E, porigin_minus_subnormal_key) = (PFLOAT 9223372036854775809)',
            '$string_unset_warning_plan(S_minus_subnormal_E[.BASE = ' + base('(PFLOAT 1)') + ']) = eps',
            '$call_task_valid(S_minus_subnormal_E, STRING_UNSET_WARNING_RESULT porigin_minus_subnormal z)',
            *review.public('S_minus_subnormal_E'),
        ]
    return checks + controls, (30 if INDEX == 2 else 16) + len(controls)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(review.__file__), Path(cases.__file__), Path(cases.raw.__file__)]
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
    report['derived_negative_subnormal_full_authentication'] = INDEX == 2
    report['scope'] = ('Independent fractional-return/infinity-throw unary-minus FLOAT keys: '
        'raw child and signed root bits, wrong sign/tag/child/pool, disabled key CODE and source '
        'occurrence refusals, source-only base mutation resume, same-Exception discard and whole/split. '
        'Return-only leaf boundaries and negative-subnormal AST authentication are source0/native0, '
        'without zero/subnormal source agreement. Fresh originals reuse saved native observations; '
        'accepted raw FLOAT/NULL/BOOL cuts are not renewed.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

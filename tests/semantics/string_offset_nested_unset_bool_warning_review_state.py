#!/usr/bin/env python3
"""Independent Boolean key tags, compiler facts and Warning continuation checks."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_review_state as review
import string_offset_nested_unset_bool_warning_cases as cases

INDEX = 2


def base(value):
    return ('BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base* z_base)) (KNOWN '
        + value + ') z) (KNOWN (PINT 7)) z_outer')


def conditions(program, path):
    literal = 'true' if INDEX < 2 else 'false'
    opposite = 'false' if INDEX < 2 else 'true'
    name = tuple(cases.CASES)[INDEX]
    checks = review.assertions(program, path, cases.OUTPUTS[name], INDEX % 2 == 1)
    old = 'S_review_E.BASE = ' + base('PNULL')
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S_review_E.BASE = ' + base('(PBOOL ' + literal + ')')
    wrong = '$string_unset_warning_plan(S_review_E[.BASE = ' + base('(PBOOL false)') + ']) = eps'
    assert checks.count(wrong) == 1
    checks[checks.index(wrong)] = '$string_unset_warning_plan(S_review_E[.BASE = ' + base('(PBOOL ' + opposite + ')') + ']) = eps'
    checks += [
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_bool_key)',
        'porigin_bool_key = PORIGIN 0 pcpath_bool_key',
        '$origin_node(S_review_E.SOURCES, porigin_bool_key) = (NExprConstFetch (NName (BYTES text_bool_key) metadata_bool_name) metadata_bool_key)',
        '$ptlc($base64(text_bool_key)) = $ptascii("' + literal + '")',
        '$compiled_read(S_review_E, porigin_bool_key) = (PBOOL ' + literal + ')',
        '$compiled_identity_value(S_review_E, porigin_bool_key) = (PBOOL ' + literal + ')',
        *('$string_unset_warning_plan(S_review_E[.BASE = ' + base(value) + ']) = eps'
          for value in ('PNULL', '(PINT 0)', '(PINT 1)')),
        'S_review_E.POOLS = ppool_bool :: ppool_bool_tail*',
        'ppool_bool.UNIT = 0',
        'S_bool_pool = S_review_E[.POOLS = (ppool_bool[.CONSTANTS = (PCONSTANT pcpath_bool_key (PBOOL ' + opposite + ')) :: ppool_bool.CONSTANTS]) :: ppool_bool_tail*]',
        '$compiled_read(S_bool_pool, porigin_bool_key) = (PBOOL ' + opposite + ')',
        '$string_unset_warning_source(S_bool_pool, porigin_site, z) = eps',
        '$string_unset_warning_plan(S_bool_pool) = eps',
        '~$call_task_valid(S_bool_pool, STRING_UNSET_WARNING_RESULT porigin_site z)',
        'S_review_E.CODE = pcode_bool :: pcode_bool_tail*',
        'pcode_bool.UNIT = 0',
        'S_bool_phase = S_review_E[.CODE = (pcode_bool[.EXPRESSIONS = (CODEEXPR pcpath_bool_key z false) :: pcode_bool.EXPRESSIONS]) :: pcode_bool_tail*]',
        '$compiled_read(S_bool_phase, porigin_bool_key) = eps',
        '$string_unset_warning_source(S_bool_phase, porigin_site, z) = eps',
        '$string_unset_warning_plan(S_bool_phase) = eps',
        '~$call_task_valid(S_bool_phase, STRING_UNSET_WARNING_RESULT porigin_site z)',
    ]
    return checks, (30 if INDEX % 2 == 0 else 16) + 13


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(review.__file__), Path(cases.__file__),
        Path(cases.null.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 2)
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
    report['scope'] = ('Independent literal Boolean entry and source-only Warning continuation: '
        'exact/opposite BOOL, NULL and INT0/1 captured keys; forged pool value against raw keyword '
        'and disabled compiled-key phase; normal Error after base rebind/removal or same-Exception '
        'discard, handler restoration and whole/split equality. Fixture source0/native0. '
        'Only fresh false-return/true-throw originals reuse their saved observations; '
        'other source agreements and accepted NULL cuts retain their own identities.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

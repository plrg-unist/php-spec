#!/usr/bin/env python3
"""Raw initialized NULL-CV entry and the existing saved-cell Warning protocol."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from encoding_declare_protocol import public
import string_offset_nested_unset_bool_cv_float_post_protocol as floating
import string_offset_nested_unset_null_cv_warning_cases as cases

INDEX = 0
FRONT_ONLY = False
PREFIX = floating.prior.seek.PREFIX + r'''
dec $null_cv_raw_front(pstate) : bool
def $null_cv_raw_front(S) = true -- if S.TODO = UNSET_ARRAY :: ptask_tail*
def $null_cv_raw_front(S) = false -- otherwise
dec $null_cv_raw_seek(pstate, nat) : pstate
def $null_cv_raw_seek(S, 0) = S
def $null_cv_raw_seek(S, n) = S
  -- if $(n > 0)
  -- if $null_cv_raw_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $null_cv_raw_seek(S, n) = $null_cv_raw_seek($drive_steps($review_cv_running(S), 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$null_cv_raw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def raw_front(program, path):
    return [
        'S_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_I.COMPLETION = BUDGET',
        'S_found = $null_cv_raw_seek(S_I, 1000)',
        '$null_cv_raw_front(S_found)',
        'S_E = $review_cv_running(S_found)',
        'S_E.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base_name* z_base)) (VARIABLE n_key_name* z_key) z) (KNOWN (PINT 7)) z_outer',
        'S_E.ORIGIN = (porigin_site)',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_E.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_E.STORE|)',
        'S_E.STORE[n_key] = DEFINED PNULL',
        '~$environment_blocked(S_E, n_key_name*)',
        '~(n_key <- S_E.REFCELLS)',
        '~$foreach_released_cell(S_E, n_key)',
        '~$typed_cv_string_released_cell(S_E, n_key)',
        '~$update_released_cell(S_E, n_key)',
        '$resolve_at(S_E, VARIABLE n_key_name* z_key, z_key) = S_E[.RESULT = KNOWN PNULL]',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        '$compiled_read(S_E, porigin_key) = eps',
        '$error_handler_eligible(S_E, 2)',
        r'S_E.REQUEST = eps /\ S_E.CURRENT = eps /\ S_E.FRAMES = eps /\ S_E.HELD = eps',
        *public('S_E'),
        '$string_unset_bool_cv_plan(S_E[.STORE[n_key] = DEFINED (PBOOL false)]) = ((porigin_site, z, n_key))',
    ]


def conditions(program, path):
    if FRONT_ONLY:
        return raw_front(program, path) + [
            '~$string_unset_bool_cv_cell(S_E, n_key_name*, z_key, n_key)',
            '$string_unset_bool_cv_plan(S_E) = eps',
        ], 1
    floating.INDEX, floating.cases = INDEX, cases
    checks, derived = floating.conditions(program, path)
    old = 'S_E.STORE[n_key] = DEFINED (PBOOL ' + str(INDEX == 0).lower() + ')'
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S_E.STORE[n_key] = DEFINED PNULL'
    if INDEX == 0:
        for check in floating.finite_checks():
            assert checks.count(check) == 1
            checks.remove(check)
    checks += ['$string_unset_bool_cv_cell(S_E, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))']
    return checks, derived


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(floating.__file__), Path(floating.prior.__file__),
               Path(floating.prior.seek.__file__), Path(floating.prior.sl.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 3)
    FRONT_ONLY = '--front-only' in sys.argv
    if FRONT_ONLY:
        sys.argv.remove('--front-only')
    runner = floating.prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, floating.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Genuine raw initialized NULL-CV source/STORE/read/ordinary cell before entry admission; '
        'BOOL-only helper/plan refusal and counterfactual BOOL plan. Source0/native0.' if FRONT_ONLY else
        'Initialized NULL-CV reuses the exact saved-cell task and corrected post predicates, preserving '
        'Error or authenticated pending Throwable, callback/mask priority and whole/split. Source0/native0.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

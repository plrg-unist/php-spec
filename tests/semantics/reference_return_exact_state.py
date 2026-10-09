#!/usr/bin/env python3
"""Generate focused SL assertions from recorded, source-checked return packets.

This producer starts no PHP, compiler, or model process. Pass the ignored raw
source-run directories and an ignored output directory; run the emitted fixtures
with the pinned numeric runner and the current modules.json in explicit --sl mode.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from request_environment_state import request_fixture

PREFIX = r'''dec $exact_function(pstate, preqbytes) : bool
def $exact_function(S, n_name*) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = n_name*
def $exact_function(S, n_name*) = false -- otherwise
dec $exact_value_head(ptask) : bool
def $exact_value_head(RETURN_REF_VALUE z) = true
def $exact_value_head(ptask) = false -- otherwise
dec $exact_value_tasks(ptask*) : bool
def $exact_value_tasks((RETURN_REF_VALUE z) :: ptask*) = true
def $exact_value_tasks(ptask_head :: ptask_tail*) = $exact_value_tasks(ptask_tail*)
  -- if ~$exact_value_head(ptask_head)
def $exact_value_tasks(eps) = false
dec $exact_finally_head(ptask) : bool
def $exact_finally_head(FINALLY_REF_RETURN porigin porigin_source poperand z) = true
def $exact_finally_head(ptask) = false -- otherwise
dec $exact_finally_tasks(ptask*) : bool
def $exact_finally_tasks((FINALLY_REF_RETURN porigin porigin_source poperand z) :: ptask*) = true
def $exact_finally_tasks(ptask_head :: ptask_tail*) = $exact_finally_tasks(ptask_tail*)
  -- if ~$exact_finally_head(ptask_head)
def $exact_finally_tasks(eps) = false
dec $exact_stage(pstate, nat) : bool
def $exact_stage(S, 1) = true
  -- if $exact_function(S, [103])
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*
def $exact_stage(S, 2) = true
  -- if $exact_function(S, [103])
  -- if S.TODO = (RETURN_REF_VALUE z) :: ptask*
def $exact_stage(S, 3) = true
  -- if $exact_function(S, [103])
  -- if S.TODO = [RETURN_REF_UNWIND poperand z true porigin_source]
def $exact_stage(S, 4) = true
  -- if $exact_function(S, [104])
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if S_scope = $constant_frame_scope(S, pframe, pframe_tail*)
  -- if $exact_function(S_scope, [103])
  -- if $exact_value_tasks(pframe.TODO)
def $exact_stage(S, 5) = true
  -- if $exact_function(S, [112,105,110,103])
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if S_scope = $constant_frame_scope(S, pframe, pframe_tail*)
  -- if $exact_function(S_scope, [103])
  -- if $exact_finally_tasks(pframe.TODO)
def $exact_stage(S, 6) = true
  -- if $exact_function(S, [103])
  -- if S.TODO = (RETURN_REF_UNWIND poperand z b porigin_source) :: ptask*
def $exact_stage(S, n) = false -- otherwise
dec $exact_find(pstate, nat, nat) : pstate
def $exact_find(S, n_stage, n) = S[.COMPLETION = NORMAL]
  -- if $exact_stage(S, n_stage)
  -- if S.COMPLETION = BUDGET
def $exact_find(S, n_stage, n) = $exact_find($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, n_next)
  -- if ~$exact_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
  -- if n_next = $(n - 1)
dec $exact_resume(pstate, nat) : pstate
def $exact_resume(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $exact_resume(S, n) = S -- otherwise
dec $exact_output(pevent) : nat*
def $exact_output(OUTPUT n*) = n*
def $exact_output(pevent) = eps -- otherwise
dec $exact_outputs(pevent*) : nat*
def $exact_outputs(eps) = eps
def $exact_outputs(pevent :: pevent_tail*) = $exact_output(pevent) ++ $exact_outputs(pevent_tail*)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = json.loads((ROOT / 'tests/semantics/reference_return_exact_cases.json').read_text())
    cases = {row['id']: row for row in catalogue['cases']}
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def source(case):
        matches = [raw / case for raw in args.raw if (raw / case / 'checked.json').exists()]
        assert len(matches) == 1, (case, matches)
        directory = matches[0].resolve()
        report = json.loads((directory.parent / 'report.json').read_text())
        accepted = [row for row in report['records'] if row['id'] == case]
        assert len(accepted) == 1 and accepted[0]['pass'] and accepted[0]['prediction_match']
        original = (directory / 'source.php').read_bytes()
        assert hashlib.sha256(original).hexdigest() == cases[case]['source_sha256']
        assert original == cases[case]['source'].encode()
        checked = json.loads((directory / 'checked.json').read_text())
        assert checked['ok'] and checked['fixture']
        facts = json.loads((directory / 'request.json').read_text())
        native = json.loads((directory / 'native.json').read_text())
        assert base64.b64decode(native['stdout']) == cases[case]['predicted_stdout'].encode()
        assert native['exit_status'] == 0
        initial = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                   json.dumps(base64.b64encode(os.fsencode(directory / 'source.php')).decode()) +
                   ', ' + request_fixture(facts) + ')')
        return initial, str(list(base64.b64decode(native['stdout']))), directory

    def fixture(name, case, stage, checks, bad=()):
        initial, output, directory = source(case)
        common = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET',
                  'S_start = S_initial[.COMPLETION = NORMAL]',
                  f'S = $exact_find(S_start, {stage}, 2000)',
                  'S.COMPLETION = NORMAL', '$call_descriptors_valid(S)',
                  '$heap_valid($heap_graph(S))']
        rejected = []
        for index, change in enumerate(bad):
            rejected += [f'S_bad{index} = ' + change,
                         f'$call_descriptors_valid(S_bad{index}) = false',
                         f'S_rejected{index} = $drive(S_bad{index}, 0)',
                         f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
                         f'$drive(S_bad{index}, 10000) = S_rejected{index}']
        replay = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                  'S_one = $exact_resume(S_zero, 1)',
                  'S_adjacent = $exact_resume(S_one, 10000)',
                  'S_frontier = $drive(S, 10001)',
                  'S_whole = $drive(S_start, 10001)',
                  'S_adjacent = S_frontier', 'S_frontier = S_whole',
                  'S_whole.COMPLETION = NORMAL',
                  '$exact_outputs(S_whole.EVENTS) = ' + output,
                  'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps',
                  'S_whole.TODO = eps', 'S_whole.HELD = eps',
                  '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)']
        conditions = common + checks + rejected + replay
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + check + '\n' for check in conditions))
        records.append({'id': name, 'source_id': case, 'source_raw': str(directory),
                        'fixture': str(path.resolve()), 'assertions': len(conditions)})

    cell = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, [118]) = (n_v)']
    backing = ['S.STORE[n_v] = DEFINED (PSTRING ([115]))',
               '$parameter_backing_at(S.PARAMETERBACKINGS, n_v) = (pparameterbacking)',
               '$propref_at(S.PROPREFS, n_v) = (ppropref)']
    retained = ['S_next.STORE = S.STORE', 'S_next.PROPREFS = S.PROPREFS',
                'S_next.PARAMETERBACKINGS = S.PARAMETERBACKINGS',
                'S_next.REFCOERCIONS = S.REFCOERCIONS',
                '$heap_valid($heap_graph(S_next))', '$call_descriptors_valid(S_next)']
    fixture('forwarded-value', 'parameter-backing-reference-call', 2,
            cell + backing + ['S.TODO = (RETURN_REF_VALUE z) :: ptask_tail*',
                              'S.RESULT = REFERENCE n_v', 'S.ORIGIN = (porigin)',
                              'S_next = $drive_steps(S, 1)',
                              'S_next.TODO = (RETURN_REF_UNWIND (REFERENCE n_v) z false porigin_source) :: ptask_after*'] + retained,
            ['S[.ORIGIN = eps]', 'S[.TODO = (RETURN_REF_VALUE $(z + 100)) :: ptask_tail*]'])
    fixture('saved-forward', 'parameter-backing-reference-call', 4,
            cell + backing + ['S.FRAMES = pframe :: pframe_tail*',
                              '$exact_value_tasks(pframe.TODO)',
                              'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
                              '$exact_function(S_scope, [103])',
                              '$call_tasks_valid(S_scope, pframe.TODO)'],
            ['S[.FRAMES = pframe[.ORIGIN = eps] :: pframe_tail*]',
             'S[.FRAMES = pframe[.TODO = RETURN_NULL :: pframe.TODO] :: pframe_tail*]'])
    for used in (True, False):
        case = 'parameter-backing-finally-recheck' if used else 'parameter-backing-finally-unused'
        checks = cell + backing + ['S.TODO = [RETURN_REF_UNWIND (REFERENCE n_v) z true porigin_source]',
                                  '$reference_return_used(S) = ' + str(used).lower(),
                                  'S_checked = $finally_ref_recheck(S, REFERENCE n_v, z)',
                                  'S_checked.COMPLETION = NORMAL', 'S_checked.STORE = S.STORE',
                                  'S_checked.PROPREFS = S.PROPREFS',
                                  'S_checked.PARAMETERBACKINGS = S.PARAMETERBACKINGS',
                                  'S_checked.REFCOERCIONS = S.REFCOERCIONS',
                                  'S_next = $drive_steps(S, 1)',
                                  'S_next.STORE[n_v] = S.STORE[n_v]',
                                  'S_next.PROPREFS = S.PROPREFS',
                                  'S_next.PARAMETERBACKINGS = S.PARAMETERBACKINGS',
                                  'S_next.REFCOERCIONS = S.REFCOERCIONS',
                                  '$heap_valid($heap_graph(S_next))', '$call_descriptors_valid(S_next)']
        fixture('finally-' + ('used' if used else 'unused'), case, 3, checks,
                ['S[.TODO = [RETURN_REF_UNWIND (REFERENCE n_v) $(z + 100) true porigin_source]]'])
    for case, before, after in [
        ('ordinary-reference-conversion', 'PSTRING ([53])', 'PINT 5'),
        ('ordinary-reference-unused-conversion', 'PSTRING ([53])', 'PINT 5'),
        ('ordinary-reference-strict-int-float', 'PINT 2', 'PFLOAT $float_of_int(2)'),
    ]:
        fixture(case, case, 1, cell + [
            'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*',
            'S.STORE[n_v] = DEFINED (' + before + ')', 'S_next = $drive_steps(S, 1)',
            'S_next.STORE[n_v] = DEFINED (' + after + ')',
            'S_next.STORE[n_v] =/= S.STORE[n_v]',
            '$heap_valid($heap_graph(S_next))', '$call_descriptors_valid(S_next)'])
    for case in ('ordinary-computed-missing-unused', 'ordinary-nullable-missing-used',
                 'ordinary-nullable-missing-unused'):
        fixture(case, case, 1, ['S_initialized = $exact_find(S, 6, 2000)',
                               'S_initialized.LOCATION = ROOT n_missing',
                               'S_initialized.STORE[n_missing] = DEFINED PNULL',
                               '$heap_valid($heap_graph(S_initialized))',
                               '$call_descriptors_valid(S_initialized)'])
    fixture('ordinary-nullable-static-initialize', 'ordinary-nullable-static-initialize', 1, [
        'S_initialized = $exact_find(S, 6, 2000)',
        'S_initialized.LOCATION = CLASS_STATIC ppropertyid',
        '$class_static_at(S.CLASSSTATICS, ppropertyid) = (pclassstatic_before)',
        'pclassstatic_before.STATE = PROP_INITIAL',
        '$class_static_at(S_initialized.CLASSSTATICS, ppropertyid) = (pclassstatic_after)',
        'pclassstatic_after.STATE = PROP_VALUE (ALIAS n_missing)',
        'S_initialized.STORE[n_missing] = DEFINED PNULL',
        '$propref_source_present(S_initialized.PROPREFS, n_missing, CLASS_PROP_SOURCE ppropertyid)',
        '$heap_valid($heap_graph(S_initialized))', '$call_descriptors_valid(S_initialized)'])
    fixture('saved-finalizer', 'parameter-backing-finally-global-rebind', 5,
            cell + backing + ['S.FRAMES = pframe :: pframe_tail*',
                              '$exact_finally_tasks(pframe.TODO)',
                              'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
                              '$exact_function(S_scope, [103])',
                              '$call_tasks_valid(S_scope, pframe.TODO)'],
            ['S[.FRAMES = pframe[.ORIGIN = eps] :: pframe_tail*]',
             'S[.FRAMES = pframe[.TODO = RETURN_NULL :: pframe.TODO] :: pframe_tail*]'])
    fixture('finalizer-captured-target', 'parameter-backing-finally-global-rebind', 3, [
        'S.TODO = [RETURN_REF_UNWIND (REFERENCE n_v) z true porigin_source]',
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, [118]) = (n_new)',
        'n_new =/= n_v', 'S.STORE[n_new] = DEFINED (PSTRING ([110,101,119]))',
        *backing, 'S_next = $drive_steps(S, 1)',
        'S_next.STORE[n_v] = S.STORE[n_v]', 'S_next.STORE[n_new] = S.STORE[n_new]',
        'S_next.PROPREFS = S.PROPREFS', 'S_next.PARAMETERBACKINGS = S.PARAMETERBACKINGS',
        'S_next.REFCOERCIONS = S.REFCOERCIONS',
        '$heap_valid($heap_graph(S_next))', '$call_descriptors_valid(S_next)'])
    # The required-recheck-unused original exposes the separately held delayed
    # TypeError finalizer replay gap (native F|F|R|SHARED, model F|R|SHARED).
    # Preserve its source failure; do not include it among passing state gates.
    (args.output / 'fixtures.json').write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps({'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                      'output': str(args.output.resolve())}))


if __name__ == '__main__':
    main()

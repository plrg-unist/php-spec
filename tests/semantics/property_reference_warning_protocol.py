#!/usr/bin/env python3
"""Reached PHP 8.5 reference-cell property Warning ownership and cleanup."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import property_undefined_warning_protocol as warning

base, sources, cross, ROOT = warning.base, warning.sources, warning.cross, warning.ROOT
CASES = {
    'replacement': 'review-property-reference-call-replacement-last-owner20',
    'pending': 'review-property-reference-call-replacement-pending20',
    'stdclass': 'review-property-reference-call-stdclass20',
}
PREFIX = warning.PREFIX.replace(
    'def $undefined_warning_phase(S, n) = false -- otherwise', r'''
def $undefined_warning_phase(S, 4) = true
  -- if S.CURRENT =/= eps
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
  -- if ppropertywarning.CELL =/= eps
def $undefined_warning_phase(S, 21) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("ReferenceCallReplacementNew20") \/ $object_name(S, n) = $ptascii("ReferenceCallReplacementPendingNew20")
def $undefined_warning_phase(S, 22) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if $throwable_field(S, n, "message") = PSTRING $ptascii("B")
  -- if $throwable_previous_id(S, n) =/= eps
def $undefined_warning_phase(S, n) = false -- otherwise
''') + r'''
dec $reference_test_functions(pfunction*, porigin) : pfunction*
def $reference_test_functions(eps, porigin) = eps
def $reference_test_functions(pfunction :: pfunction_tail*, porigin) = pfunction[.SIGNATURE = pfunction.SIGNATURE[.BYREF = false]] :: pfunction_tail*
  -- if pfunction.ORIGIN = porigin
def $reference_test_functions(pfunction :: pfunction_tail*, porigin) = pfunction :: $reference_test_functions(pfunction_tail*, porigin)
  -- if pfunction.ORIGIN =/= porigin
'''


def start(run):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP',
        *warning.seek('S_initial', 'S_before', 0),
        'S_before.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z) :: (DIM_FETCH z) :: ptask_tail*',
        'S_before.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_before.RESULT = REFERENCE n_cell',
        'S_before.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
        '$property_undefined_reference_plan(S_before) = (ppropertywarning)',
        '$property_undefined_read_plan(S_before) = (ppropertywarning)',
        'ppropertywarning.CELL = (n_cell)', 'ppropertywarning.BORROWED', '~ppropertywarning.FREEING',
        'ppropertywarning.OBJECT = n_receiver',
        'ppropertywarning.READ.NAME = $base64(text_name)', 'ppropertywarning.READ.LINE = z',
        'S_before.ORIGIN = (ppropertywarning.READ.SITE)',
        '$property_undefined_reference_source(S_before, ppropertywarning.READ)',
        '$property_undefined_cell(S_before, n_cell)',
        '$property_undefined_slot(S_before, n_receiver, ppropertywarning.KEY)',
        '~$property_undefined_reference_receiver(S_before)',
        '$property_undefined_cell_tasks(S_before.TODO, n_cell, ppropertywarning.READ.SITE) = 0',
        '$machine_base_roots(S_before) = eps',
        '$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = [HCELL n_cell]',
        '$heap_owners($heap_graph(S_before), HCELL n_cell) = 2',
        '$heap_owners($heap_graph(S_before), HOBJECT n_receiver) = 1',
        '$trace_slot(S_before, S_before.ENV, $ptascii("weak")) = POBJECT n_weak',
        '$weakref_get(S_before, n_weak) = POBJECT n_receiver',
        'S_bad_base = S_before[.BASE = BASE_VALUE (KNOWN (POBJECT n_receiver))]',
        '$property_undefined_reference_plan(S_bad_base) = eps',
        'S_latent = S_before[.TODO = S_before.TODO ++ [PROPERTY_UNDEFINED_RESULT ppropertywarning]]',
        '$property_undefined_reference_plan(S_latent) = eps',
        'S_zero = $drive_steps(S_before, 0)', 'S_zero = S_before[.COMPLETION = BUDGET]',
        *warning.step('S_before', 'S_invoke'),
        'S_invoke.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
        'perrorcall.TARGET = eps', '$error_call_valid(S_invoke, perrorcall)',
        'S_invoke.RESULT = KNOWN PNULL', 'S_invoke.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_invoke), HCELL n_cell) = 2',
        '$heap_owners($heap_graph(S_invoke), HOBJECT n_receiver) = 1',
        '$property_undefined_cell_tasks(S_invoke.TODO, n_cell, ppropertywarning.READ.SITE) = 1']


def default_control():
    checks = []
    for state, reporting in (('S_default', ''), ('S_masked', '[.REPORTING = 0]')):
        checks += [f'{state} = S_before[.ERRORHANDLER = S_before.ERRORHANDLER[.LEVELS = 0]]{reporting}',
            f'~$error_handler_eligible({state}, 2)', f'$error_read_pending({state})',
            *warning.valid(state), *warning.step(state, state+'_resume'),
            f'{state}_resume.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: ptask_tail*',
            f'{state}_resume.RESULT = KNOWN PNULL',
            f'$heap_owners($heap_graph({state}_resume), HCELL n_cell) = 2',
            f'$heap_owners($heap_graph({state}_resume), HOBJECT n_receiver) = 1']
    return checks


def admission():
    checks = [
        'S_before.ORIGIN = (PORIGIN n_unit pcpath)',
        '$origin_node(S_before.SOURCES, ppropertywarning.READ.SITE) = (NExprPropertyFetch expression_receiver phpType20_name metadata_property)',
        'expression_receiver = NExprFuncCall name (SEQUENCE eps) metadata_call',
        '$code_at(S_before.CODE, n_unit) = (pcode)',
        '$code_name(pcode.NAMES, pcpath ++ [PCFIELD 0]) = ((ptbytes_callee, eps))',
        '$call_target(S_before, ptbytes_callee, eps) = (pfunction)',
        'S_nonref = S_before[.FUNCTIONS = $reference_test_functions(S_before.FUNCTIONS, pfunction.ORIGIN)]',
        '~$property_undefined_reference_source(S_nonref, ppropertywarning.READ)',
        '$property_undefined_reference_plan(S_nonref) = eps',
        'pcunit = S_before.SOURCES[n_unit]',
        'expression_noncall = NExprVariable (BYTES "cmVjZWl2ZXI=") metadata_call',
        'pcnode_noncall = NExprPropertyFetch expression_noncall phpType20_name metadata_property',
        'S_noncall = S_before[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath pcnode_noncall) :: pcunit.OCCURRENCES]]',
        '~$property_undefined_reference_source(S_noncall, ppropertywarning.READ)',
        'expression_dynamic = NExprFuncCall expression_noncall (SEQUENCE eps) metadata_call',
        'pcnode_dynamic = NExprPropertyFetch expression_dynamic phpType20_name metadata_property',
        'S_dynamic = S_before[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath pcnode_dynamic) :: pcunit.OCCURRENCES]]',
        '~$property_undefined_reference_source(S_dynamic, ppropertywarning.READ)',
        'S_duplicate = S_invoke[.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: S_invoke.TODO]',
        '$property_undefined_cell_tasks(S_duplicate.TODO, n_cell, ppropertywarning.READ.SITE) = 2',
        '~$call_descriptors_valid(S_duplicate)',
        '$lookup(S_invoke.ENV, $ptascii("weak")) = (n_wrong)',
        'S_wrong = $reference_cell(S_invoke, n_wrong)', '$property_undefined_cell(S_wrong, n_wrong)',
        '~$error_call_valid(S_wrong, perrorcall[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[.CELL = (n_wrong)]])',
        'S_no_cell = S_invoke[.REFCELLS = eps]',
        '~$call_descriptors_valid(S_no_cell)',
        *warning.seek('S_invoke', 'S_saved', 4),
        'S_saved.FRAMES = pframe :: pframe_saved_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_saved) :: ptask_saved_tail*',
        'perrorcall_saved.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
        'S_scope = $constant_frame_scope(S_saved, pframe, pframe_saved_tail*)',
        '$error_entered_call_valid(S_scope, perrorcall_saved)',
        '$property_undefined_cell_tasks(S_saved.TODO, n_cell, ppropertywarning.READ.SITE) = 0',
        '$property_undefined_cell_tasks(S_scope.TODO, n_cell, ppropertywarning.READ.SITE) = 1',
        'S_saved_duplicate = S_saved[.FRAMES = pframe[.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: pframe.TODO] :: pframe_saved_tail*]',
        '~$call_descriptors_valid(S_saved_duplicate)',
        'S_saved_missing = S_saved[.FRAMES = pframe[.TODO = ptask_saved_tail*] :: pframe_saved_tail*]',
        '~$call_descriptors_valid(S_saved_missing)']
    for field in ('.CELL = eps', '.CELL = (|S_invoke.STORE|)', '.BORROWED = false',
                  '.FREEING = true', '.READ.LINE = 999', '.READ.NAME = $ptascii("forged377")',
                  '.KEY = $ptascii("forged377")', '.OBJECT = |S_invoke.OBJECTS|'):
        checks += [f'~$error_call_valid(S_invoke, perrorcall[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]])',
            f'~$call_descriptors_valid(S_saved[.FRAMES = pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall_saved[.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning[{field}]]) :: ptask_saved_tail*] :: pframe_saved_tail*])']
    return checks


def retired(state):
    return [f'$lookup({state}.ENV, $ptascii("receiver")) = eps',
        f'~((HOBJECT n_receiver) <- {state}.ALLOCATIONS)',
        f'$weakref_get({state}, n_weak) = PNULL',
        f'$heap_owners($heap_graph({state}), HOBJECT n_receiver) = 0',
        f'$trace_slot({state}, {state}.ENV, $ptascii("replacement_weak")) = POBJECT n_replacement_weak',
        f'$weakref_get({state}, n_replacement_weak) = POBJECT n_replacement',
        f'{state}.STORE[n_cell] = DEFINED (POBJECT n_replacement)',
        f'$heap_owners($heap_graph({state}), HCELL n_cell) = 1',
        f'$heap_owners($heap_graph({state}), HOBJECT n_replacement) = 1',
        f'$property_undefined_read_valid({state}, ppropertywarning)']


def body(run, expected, group):
    checks = [*start(run), *default_control(), *admission()]
    if group == 'stdclass':
        checks += ['S_before.OBJECTS[n_receiver] = STDINSTANCE',
            '$trace_slot(S_before, S_before.ENV, $ptascii("child_weak")) = POBJECT n_child_weak',
            '$weakref_get(S_before, n_child_weak) = POBJECT n_child',
            '$node_children(S_before, HOBJECT n_receiver) = [HOBJECT n_child]']
    if group == 'pending':
        checks += [*warning.seek('S_saved', 'S_handler', 10),
            'S_handler.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$throwable_field(S_handler, n_error, "message") = PSTRING $ptascii("H")',
            '$throwable_previous_id(S_handler, n_error) = eps',
            *retired('S_handler'), *warning.seek('S_handler', 'S_cleanup', 21),
            'S_cleanup.CURRENT = (pcallcontext_cleanup)',
            '$destructor_context_call(pcallcontext_cleanup, S_cleanup.CURRENT, S_cleanup.FRAMES) = (pdestructorcall)',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.PENDING = (n_error)',
            '$weakref_get(S_cleanup, n_replacement_weak) = PNULL',
            '$throwable_field(S_cleanup, n_error, "message") = PSTRING $ptascii("H")',
            *warning.seek('S_cleanup', 'S_chained', 22),
            'S_chained.TODO = (THROW_SEARCH n_final) :: ptask_final_tail*',
            '$throwable_previous_id(S_chained, n_final) = (n_error)',
            *warning.finish('S_chained', expected)]
    else:
        checks += [*warning.seek('S_saved', 'S_handler', 2),
            'S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
            'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            '$error_entered_call_valid(S_handler, perrorcall_entered)',
            *retired('S_handler'), *warning.seek('S_handler', 'S_resume', 3),
            'S_resume.RESULT = KNOWN PNULL', 'S_resume.BASE = BASE_VALUE (KNOWN PNULL)',
            '$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = [HCELL n_cell]',
            # Constructed false-return branch after genuine handler effects.
            'S_false = S_handler[.RESULT = KNOWN (PBOOL false)]', *warning.valid('S_false'),
            *warning.step('S_false', 'S_fallback'),
            'S_fallback.EVENTS = $error_default(S_false, perrorcall_entered.EVENT, 2).EVENTS',
            *warning.seek('S_fallback', 'S_false_resume', 3),
            'S_false_resume.RESULT = KNOWN PNULL',
            '$property_undefined_read_valid(S_false_resume, ppropertywarning)',
            '$heap_owners($heap_graph(S_false_resume), HCELL n_cell) = 1',
            '$heap_owners($heap_graph(S_false_resume), HOBJECT n_replacement) = 1',
            '$weakref_get(S_false_resume, n_replacement_weak) = POBJECT n_replacement',
            *warning.step('S_resume', 'S_releasing'),
            *warning.finish('S_releasing', expected)]
    checks += ['~((HCELL n_cell) <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done, n_weak) = PNULL',
        '$weakref_get(S_done, n_replacement_weak) = PNULL']
    if group == 'stdclass':
        checks += ['$weakref_get(S_handler, n_child_weak) = PNULL',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)']
    return checks


def old_source_control(run):
    return ['S_old_initial = '+run,
        *warning.seek('S_old_initial', 'S_old', 0),
        '$property_undefined_read_plan(S_old) = (ppropertywarning_old)',
        'ppropertywarning_old.CELL = eps', 'ppropertywarning_old.BORROWED',
        '$property_undefined_read_valid(S_old, ppropertywarning_old)',
        '$lookup(S_old.ENV, $ptascii("receiver")) = (n_old_cell)',
        'S_old_ref = $reference_cell(S_old, n_old_cell)',
        '$property_undefined_cell(S_old_ref, n_old_cell)',
        '~$property_undefined_reference_source(S_old_ref, ppropertywarning_old.READ)',
        '~$property_undefined_read_valid(S_old_ref, ppropertywarning_old[.CELL = (n_old_cell)])']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='property-reference-warning-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(),
            *body(run, sources.EXPECTED[CASES[args.group]], args.group)]
        if args.group == 'replacement':
            old = out/'old-cv-control'; old.mkdir()
            old_source = old/'source.php'
            old_source.write_bytes(sources.CASES['review-property-undefined-borrowed-retirement19'])
            sources.prepare(old, old_source)
            old_run = '$php_run(program_old,0,'+json.dumps(base64.b64encode(os.fsencode(old_source)).decode())+')'
            clauses += ['program_old = '+(old/'program.watsup').read_text().strip(), *old_source_control(old_run)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture), assertions=len(clauses))
        if not args.prepare_only:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

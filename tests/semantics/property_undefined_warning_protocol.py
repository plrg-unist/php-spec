#!/usr/bin/env python3
"""Reached undefined-property warnings with borrowed and owned receivers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import instance_future_initial_read_protocol as initial

base = initial.base
sources = base.sources
cross = base.cross
ROOT = base.ROOT
CASES = {
    'borrowed': 'review-property-undefined-borrowed-retirement19',
    'owned': 'review-property-undefined-owned-retirement19',
    'pending': 'review-property-undefined-pending19',
}
PREFIX = initial.PREFIX + r'''
dec $undefined_warning_phase(pstate, nat) : bool
def $undefined_warning_phase(S, 0) = ($property_undefined_read_plan(S) =/= eps)
def $undefined_warning_phase(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
def $undefined_warning_phase(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
def $undefined_warning_phase(S, 3) = true
  -- if S.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: ptask*
def $undefined_warning_phase(S, 10) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
def $undefined_warning_phase(S, 11) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("UndefinedPendingSecond377")
def $undefined_warning_phase(S, 12) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask*
  -- if pforeachbind.VALUE = POBJECT n
  -- if $object_name(S, n) = $ptascii("UndefinedPendingParent377")
def $undefined_warning_phase(S, 20) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata_name) z) :: (DIM_FETCH z) :: ptask*
def $undefined_warning_phase(S, n) = false -- otherwise
dec $undefined_warning_seek(pstate, nat, nat) : pstate
def $undefined_warning_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $undefined_warning_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $undefined_warning_phase(S, n_phase)
def $undefined_warning_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$undefined_warning_phase(S, n_phase)
def $undefined_warning_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$undefined_warning_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $undefined_warning_seek(S, n_phase, n) = $undefined_warning_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$undefined_warning_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def valid(state):
    return [*base.valid(state), f'$scope_codes_valid({state}, {state}.CODE)']


def seek(parent, state, phase):
    return [f'{state}_found = $undefined_warning_seek({parent}, {phase}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$undefined_warning_phase({state}, {phase})', *valid(state)]


def step(parent, state):
    return [f'{state}_found = $drive_steps({parent}, 1)',
        f'{state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]', *valid(state)]


def start(run):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_before', 0),
        'S_before.TODO = (DIM_FETCH z) :: ptask_tail*',
        'S_before.BASE = BASE_PROPERTY (POBJECT n_receiver) ptbytes_name',
        '$property_undefined_read_plan(S_before) = (ppropertywarning)',
        'ppropertywarning.OBJECT = n_receiver',
        'ppropertywarning.READ.NAME = ptbytes_name',
        'ppropertywarning.READ.LINE = z',
        'S_before.ORIGIN = (ppropertywarning.READ.SITE)',
        '$property_resolve(S_before, n_receiver, ptbytes_name) = PROPERTY_ACCESS ppropertywarning.KEY',
        '$property_undefined_read_valid(S_before, ppropertywarning)',
        '$property_undefined_slot(S_before, n_receiver, ppropertywarning.KEY)',
        '$error_read_pending(S_before)',
        'ptbytes_message = $property_undefined_read_message(S_before, ppropertywarning)',
        '~$property_undefined_read_valid(S_before, ppropertywarning[.BORROWED = ~ppropertywarning.BORROWED])',
        '~$property_undefined_read_valid(S_before, ppropertywarning[.READ.LINE = 999])',
        '~$property_undefined_read_valid(S_before, ppropertywarning[.READ.NAME = $ptascii("forged377")])',
        '~$property_undefined_read_valid(S_before, ppropertywarning[.OBJECT = |S_before.OBJECTS|])',
        'S_zero = $drive_steps(S_before, 0)',
        'S_zero = S_before[.COMPLETION = BUDGET]',
        *step('S_before', 'S_invoke'),
        'S_invoke.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
        'perrorcall.TARGET = eps',
        'perrorcall.SITE = ppropertywarning.READ.SITE',
        'perrorcall.LINE = z', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = ptbytes_message',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" ptbytes_message z',
        '$error_call_valid(S_invoke, perrorcall)',
        '~$error_call_valid(S_invoke, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_invoke, perrorcall[.LEVEL = 8192])',
        'S_invoke.RESULT = KNOWN PNULL',
        'S_invoke.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_invoke.DESTRUCTION.OPERATIONS = S_before.DESTRUCTION.OPERATIONS']


def finish(state, expected):
    return [*base.finish(state, expected), '$scope_codes_valid(S_done, S_done.CODE)',
        f'S_paused = $drive_steps({state}, 0)',
        f'S_paused = {state}[.COMPLETION = BUDGET]',
        'S_done = $drive(S_paused[.COMPLETION = NORMAL], 2048)']


def lifetime_assertions(run, expected, borrowed):
    flag = 'true' if borrowed else 'false'
    before_owners = 1 if borrowed else 2
    prefix = 'C|H|D|1|' if borrowed else 'C|H|0|'
    checks = [*start(run),
        'ptbytes_name = $ptascii("missing")',
        f'ppropertywarning.BORROWED = {flag}', '~ppropertywarning.FREEING',
        '$lookup(S_before.ENV, $ptascii("receiver")) = (n_cell)',
        'S_before.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
        '$trace_slot(S_before, S_before.ENV, $ptascii("weak")) = POBJECT n_weak',
        '$weakref_get(S_before, n_weak) = POBJECT n_receiver',
        f'$heap_owners($heap_graph(S_before), HOBJECT n_receiver) = {before_owners}',
        f'$heap_owners($heap_graph(S_invoke), HOBJECT n_receiver) = {before_owners}',
        '$property_undefined_read_plan(S_invoke) = eps',
        *seek('S_invoke', 'S_handler', 2),
        'S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
        'perrorcall_entered.TARGET =/= eps',
        '$error_entered_call_valid(S_handler, perrorcall_entered)',
        '$lookup(S_handler.ENV, $ptascii("receiver")) = eps',
        '$instance_test_output(S_handler.EVENTS) = $ptascii('+json.dumps(prefix)+')',
        '$property_undefined_read_valid(S_handler, ppropertywarning)',
        *seek('S_handler', 'S_resume', 3),
        'S_resume.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: ptask_resume_tail*',
        '$call_task_valid(S_resume, PROPERTY_UNDEFINED_RESULT ppropertywarning)',
        'S_resume.RESULT = KNOWN PNULL',
        'S_resume.BASE = BASE_VALUE (KNOWN PNULL)']
    if borrowed:
        checks += [
            '$property_undefined_cv_receiver(S_before, ppropertywarning)',
            '$machine_base_roots(S_before) = eps',
            '$eager_base_inputs(S_before, DIM_FETCH z) = eps',
            '$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = eps',
            '~((HOBJECT n_receiver) <- S_handler.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_handler), HOBJECT n_receiver) = 0',
            '$weakref_get(S_handler, n_weak) = PNULL',
            '$property_undefined_class(S_handler, n_receiver) = false',
            '$property_undefined_history(S_handler, n_receiver)',
            '$heap_owners($heap_graph(S_resume), HOBJECT n_receiver) = 0',
            *step('S_resume', 'S_read'),
            'S_read = S_resume[.TODO = ptask_resume_tail*]',
            'S_read.DESTRUCTION.OPERATIONS = S_resume.DESTRUCTION.OPERATIONS']
    else:
        checks += [
            *seek('S_initial', 'S_prep', 20),
            'S_prep.RESULT = KNOWN (POBJECT n_receiver)',
            '~$property_undefined_reference_receiver(S_prep)',
            'S_plain = S_prep[.RESULT = VARIABLE $ptascii("receiver") z]',
            '~$property_undefined_reference_receiver(S_plain)',
            # Constructed raw-reference guard, not an observed ref-return run.
            'S_reference = $reference_cell(S_prep, n_cell)[.RESULT = REFERENCE n_cell]',
            'S_reference.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
            '(HCELL n_cell) <- S_reference.ALLOCATIONS',
            '$property_undefined_reference_receiver(S_reference)',
            'PhpStep: S_reference ~> S_reference_stop',
            'S_reference_stop = S_reference[.COMPLETION = UNSUPPORTED "undefined property reference receiver lifetime"]',
            'S_no_handler = S_reference[.ERRORHANDLER.CALLBACK = eps]',
            r'~($error_handler_eligible(S_no_handler, 2) \/ $eval_compile_recorded_error(S_no_handler, 2))',
            '~$property_undefined_reference_receiver(S_no_handler)',
            '$machine_base_roots(S_before) = [HOBJECT n_receiver]',
            '$eager_base_inputs(S_before, DIM_FETCH z) = [HOBJECT n_receiver]',
            '$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = [HOBJECT n_receiver]',
            '(HOBJECT n_receiver) <- S_handler.ALLOCATIONS',
            '$heap_owners($heap_graph(S_handler), HOBJECT n_receiver) = 1',
            '$weakref_get(S_handler, n_weak) = POBJECT n_receiver',
            '$heap_owners($heap_graph(S_resume), HOBJECT n_receiver) = 1',
            '~$property_undefined_read_valid(S_resume[.ALLOCATIONS = eps], ppropertywarning)',
            *step('S_resume', 'S_read'),
            'S_read.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_resume_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]',
            'pdestructionoperation.SOURCE = PROPERTY_UNDEFINED_RESULT ppropertywarning',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.PENDING = eps',
            '$heap_owners($heap_graph(S_read), HOBJECT n_receiver) = 1']
    # Constructed handler-false control at the genuine returned-handler state.
    checks += [
        'S_false = S_handler[.RESULT = KNOWN (PBOOL false)]',
        *valid('S_false'), *step('S_false', 'S_fallback'),
        'S_fallback.EVENTS = $error_default(S_false, perrorcall_entered.EVENT, 2).EVENTS',
        *seek('S_fallback', 'S_false_resume', 3),
        'S_false_resume.RESULT = KNOWN PNULL',
        '$call_task_valid(S_false_resume, PROPERTY_UNDEFINED_RESULT ppropertywarning)',
        *finish('S_read', expected),
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done, n_weak) = PNULL']
    return checks


def pending_assertions(run, expected):
    return [*start(run),
        'ppropertywarning.FREEING', '~ppropertywarning.BORROWED',
        'ptbytes_name = $ptascii("field")',
        '$instance_storage_for(S_before, n_receiver) = (pinstancestorage)',
        'pinstancestorage.NEXT = 1',
        '$instance_storage_frames(S_before.FRAMES) = [pinstancestorage]',
        '$instance_storage_tasks(S_before.TODO) = eps',
        '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_receiver]',
        '$machine_base_roots(S_before) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_before), HOBJECT n_receiver) = 2',
        '$heap_owners($heap_graph(S_invoke), HOBJECT n_receiver) = 2',
        '$property_slot_at(pinstancestorage.SLOTS, ptbytes_name) = (ppropertyslot)',
        'ppropertyslot.STATE = PROP_UNSET',
        '$instance_storage_untyped_unset_desc(S_before, n_receiver, ptbytes_name) = (ppropertydesc)',
        'ppropertydesc.TYPE = eps',
        '$instance_storage_unset_desc(S_before, n_receiver, ptbytes_name) = eps',
        '$instance_storage_quiet_result(S_before, n_receiver, ptbytes_name) = (PNULL)',
        'S_missing = S_before[.FRAMES = $instance_test_without_frames(S_before.FRAMES)]',
        '$instance_storage_for(S_missing, n_receiver) = eps',
        '~$property_undefined_read_valid(S_missing, ppropertywarning)',
        '~$call_descriptors_valid(S_missing)',
        'S_duplicate = S_before[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_before.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        '~$property_undefined_read_valid(S_duplicate, ppropertywarning)',
        '~$call_descriptors_valid(S_duplicate)',
        # A constructed default-reporting branch retains the actual receiver
        # release, with no handler continuation or hidden additional owner.
        'S_before.ERRORHANDLER.CALLBACK = (pvalue_registered)',
        'S_default = S_before[.ERRORHANDLER.CALLBACK = eps][.HELD = S_before.HELD ++ $value_nodes(pvalue_registered)]',
        *valid('S_default'),
        '~$error_read_pending(S_default)',
        *step('S_default', 'S_default_read'),
        'S_default_read.EVENTS = $diagnostic(S_default, "Warning", ptbytes_message, z).EVENTS',
        'S_default_read.RESULT = KNOWN PNULL',
        'S_default_read.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_default_read), HOBJECT n_receiver) = 2',
        *seek('S_invoke', 'S_pending', 10),
        'S_pending.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_pending_tail*',
        'perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
        '$error_entered_call_valid(S_pending, perrorcall_entered)',
        '$throwable_field(S_pending, n_error, "message") = PSTRING $ptascii("H")',
        '$throwable_previous_id(S_pending, n_error) = eps',
        '$heap_owners($heap_graph(S_pending), HOBJECT n_error) = 1',
        '$heap_owners($heap_graph(S_pending), HOBJECT n_receiver) = 2',
        '$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = [HOBJECT n_receiver]',
        '$error_read_discard(S_pending, PROPERTY_UNDEFINED_RESULT ppropertywarning) = S_pending',
        *step('S_pending', 'S_cleanup'),
        '$heap_owners($heap_graph(S_cleanup), HOBJECT n_receiver) = 2',
        '$heap_owners($heap_graph(S_cleanup), HOBJECT n_error) = 1',
        'S_cleanup.ERRORHANDLER.CALLBACK = (perrorcall_entered.CALLBACK)',
        *seek('S_cleanup', 'S_second', 11),
        '$instance_storage_for(S_second, n_receiver) = (pinstancestorage[.NEXT = 3])',
        '$heap_owners($heap_graph(S_second), HOBJECT n_receiver) = 1',
        '$node_children(S_second, HOBJECT n_receiver) = eps',
        '$objectprops_at(S_second.OBJECTPROPS, n_receiver) = (ppropertyslot_current*)',
        '$property_slot_at(ppropertyslot_current*, ptbytes_name) = (ppropertyslot)',
        '$instance_storage_untyped_unset_desc(S_second, n_receiver, ptbytes_name) = eps',
        '$property_undefined_read_valid(S_second[.ORIGIN = S_before.ORIGIN], ppropertywarning) = false',
        '$property_read(S_second, POBJECT n_receiver, ptbytes_name, z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        'S_second.DESTRUCTION.CALLS = pdestructorcall_second :: pdestructorcall_tail*',
        'pdestructorcall_second.PENDING = (n_error)',
        '$heap_owners($heap_graph(S_second), HOBJECT n_error) = 1',
        *seek('S_second', 'S_commit', 12),
        'S_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_commit) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_commit_tail*',
        'pdestructionoperation_commit.PENDING = (n_final)',
        '$throwable_previous_id(S_commit, n_final) = (n_error)',
        '$throwable_field(S_commit, n_final, "message") = PSTRING $ptascii("B")',
        '~((HOBJECT n_receiver) <- S_commit.ALLOCATIONS)',
        'n_selected = pforeachbind.NEW',
        'S_commit.STORE[n_selected] = DEFINED (PINT 2)',
        '$task_nodes(FOREACH_BIND_COMMIT pforeachbind) = [HCELL n_selected]',
        '$heap_owners($heap_graph(S_commit), HCELL n_selected) = 2',
        *step('S_commit', 'S_installed'),
        '$lookup(S_installed.ENV, $ptascii("value")) = (n_selected)',
        'S_installed.STORE[n_selected] = DEFINED (PINT 2)',
        'S_installed.TODO = (THROW_SEARCH n_final) :: ptask_commit_tail*',
        *finish('S_installed', expected)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='property-undefined-warning-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'
        source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        expected = sources.EXPECTED[CASES[args.group]]
        body = pending_assertions(run, expected) if args.group == 'pending' else lifetime_assertions(run, expected, args.group == 'borrowed')
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- '+('' if clause.startswith('PhpStep:') else 'if ')+clause+'\n' for clause in clauses)+
            '\ndec $main() : bool\ndef $main() = $body()\n')
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

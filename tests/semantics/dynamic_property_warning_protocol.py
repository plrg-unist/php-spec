#!/usr/bin/env python3
"""Reached warning producer ownership, source admission and live-table insertion."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources

cross = sources.cross
ROOT = sources.ROOT
PREFIX = r'''
dec $dynamic_is_output(pevent) : bool
dec $dynamic_output(pevent*) : ptbytes
def $dynamic_output(eps) = eps
def $dynamic_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $dynamic_output(pevent*)
def $dynamic_output(pevent :: pevent_tail*) = $dynamic_output(pevent_tail*) -- if ~$dynamic_is_output(pevent)
def $dynamic_is_output(OUTPUT ptbytes) = true
def $dynamic_is_output(pevent) = false -- otherwise
dec $dynamic_phase(pstate, nat) : bool
def $dynamic_phase(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty
def $dynamic_phase(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty
def $dynamic_phase(S, 2) = true
  -- if S.TODO = (PROPERTY_DYNAMIC_RESULT pdynamicproperty) :: ptask_tail*
def $dynamic_phase(S, 3) = true
  -- if S.TODO = (PROPERTY_DYNAMIC_INSERT pdynamicproperty) :: ptask_tail*
def $dynamic_phase(S, 4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (PROPERTY_DYNAMIC_INSERT pdynamicproperty) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = PROPERTY_DYNAMIC_RESULT pdynamicproperty_source
  -- if pdestructionoperation.PENDING =/= eps
def $dynamic_phase(S, 5) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if $exit_invoke_valid(S, pexitcall)
  -- if $property_dynamic_exit_pending(S)
def $dynamic_phase(S, 6) = true
  -- if $dynamic_output(S.EVENTS) = $ptascii("warning|receiver|")
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = PROPERTY_DYNAMIC_INSERT pdynamicproperty
  -- if pdestructorcall.OBJECT = pdynamicproperty.TARGET
def $dynamic_phase(S, n) = false -- otherwise
dec $dynamic_seek(pstate, nat, nat) : pstate
def $dynamic_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $dynamic_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $dynamic_phase(S, n_phase)
def $dynamic_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dynamic_phase(S, n_phase)
def $dynamic_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dynamic_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $dynamic_seek(S, n_phase, n) = $dynamic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dynamic_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $dynamic_seek({parent}, {phase}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$dynamic_phase({state}, {phase})', *valid(state)]


def assertions(initial, group, expected):
    if group in ['pending','pending-resurrection']:
        return pending_assertions(initial, expected, group=='pending-resurrection')
    if group=='exit':
        return exit_assertions(initial)
    clauses = ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_entry', 0),
        'S_entry.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_entry_tail*',
        'perrorcall.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty',
        'pdynamicproperty.PENDING = eps', '~pdynamicproperty.RETIRED',
        'pdynamicproperty.KEY = $ptascii("x")',
        'pdynamicproperty.RHS = KNOWN (PINT 7)',
        'pdynamicproperty.SELECTED = KNOWN (PINT 7)',
        '$task_nodes(PROPERTY_DYNAMIC_RESULT pdynamicproperty) = [HOBJECT pdynamicproperty.TARGET]',
        '$task_nodes(PROPERTY_DYNAMIC_INSERT pdynamicproperty) = eps',
        '$property_dynamic_valid(S_entry, pdynamicproperty)',
        '$property_dynamic_entry(S_entry, perrorcall, pdynamicproperty)',
        '$error_call_valid(S_entry, perrorcall)']
    forged = {
        'line': 'pdynamicproperty[.LINE = $(pdynamicproperty.LINE + 1)]',
        'literal': 'pdynamicproperty[.RHS = KNOWN (PINT 9)][.SELECTED = KNOWN (PINT 9)]',
        'retired': 'pdynamicproperty[.RETIRED = true]',
        'key': 'pdynamicproperty[.KEY = $ptascii("y")]'}
    for label, record in forged.items():
        bad = 'S_bad_'+label
        clauses += [f'pdynamicproperty_{label} = {record}',
            f'perrorcall_{label} = perrorcall[.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty_{label}]',
            f'{bad} = S_entry[.TODO = (ERROR_HANDLER_INVOKE perrorcall_{label}) :: ptask_entry_tail*]',
            f'$heap_graph({bad}) = $heap_graph(S_entry)',
            f'~$error_call_valid({bad}, perrorcall_{label})', f'~$call_descriptors_valid({bad})',
            f'S_rejected_{label} = $drive({bad}, 0)',
            f'S_rejected_{label}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
    clauses += ['perrorcall_coherent = perrorcall_line[.LINE = pdynamicproperty_line.LINE]',
        'S_bad_coherent = S_entry[.TODO = (ERROR_HANDLER_INVOKE perrorcall_coherent) :: ptask_entry_tail*]',
        '$heap_graph(S_bad_coherent) = $heap_graph(S_entry)',
        '~$error_call_valid(S_bad_coherent, perrorcall_coherent)',
        '~$call_descriptors_valid(S_bad_coherent)',
        *seek('S_entry', 'S_body', 1),
        'S_body.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_body_tail*',
        'perrorcall_entered.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty',
        'S_owner = $constant_frame_scope(S_body, pframe, pframe_tail*)',
        '$property_dynamic_valid(S_owner, pdynamicproperty)',
        '$error_entered_call_valid(S_owner, perrorcall_entered)',
        *seek('S_body', 'S_release', 2),
        'S_release.TODO = (PROPERTY_DYNAMIC_RESULT pdynamicproperty) :: ptask_release_tail*']
    if group in ['retirement','resurrection']:
        clauses += ['$heap_owners($heap_graph(S_release), HOBJECT pdynamicproperty.TARGET) = 1',
            'S_global = $global_table_view(S_release)', '$lookup(S_global.ENV, $ptascii("object")) = eps']
    clauses += [*seek('S_release', 'S_insert', 3),
        'S_insert.TODO = (PROPERTY_DYNAMIC_INSERT pdynamicproperty_insert) :: ptask_insert_tail*',
        'pdynamicproperty_insert = pdynamicproperty[.RETIRED = '+str(group!='reentry').lower()+']',
        '$property_dynamic_valid(S_insert, pdynamicproperty_insert)']
    if group=='reentry':
        clauses += ['$heap_member(HOBJECT pdynamicproperty.TARGET, S_insert.ALLOCATIONS)',
            '$objectprops_at(S_insert.OBJECTPROPS, pdynamicproperty.TARGET) = ([{DECL eps, NAME ($ptascii("x")), STATE PROP_VALUE (DIRECT (PINT 2))}])',
            '$property_dynamic_item(S_insert, pdynamicproperty) = (DIRECT (PINT 7), KNOWN (PINT 7))',
            'S_inserted_found = $drive_steps(S_insert, 1)', 'S_inserted_found.COMPLETION = BUDGET',
            'S_inserted = S_inserted_found[.COMPLETION = NORMAL]',
            *valid('S_inserted'),
            '$objectprops_at(S_inserted.OBJECTPROPS, pdynamicproperty.TARGET) = ([{DECL eps, NAME ($ptascii("x")), STATE PROP_VALUE (DIRECT (PINT 2))}, {DECL eps, NAME ($ptascii("x")), STATE PROP_VALUE (DIRECT (PINT 7))}])',
            '$property_duplicate_table(S_inserted, pdynamicproperty.TARGET)',
            '$location_slot(S_inserted, PROPERTY pdynamicproperty.TARGET ($ptascii("x"))) = DEFINED (PINT 7)']
        parent = 'S_inserted'
    else:
        clauses += [*retired_receiver('S_insert', group=='resurrection'),
            '$dynamic_output(S_insert.EVENTS) = $ptascii("warning|released|drop|")']
        parent = 'S_insert'
    clauses += [f'S_done = $drive_steps({parent}, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$dynamic_output(S_done.EVENTS) = '+cross.invoke.byte_expr(expected.encode()), *valid('S_done')]
    return clauses


def retired_receiver(state, resurrect):
    if not resurrect:
        return [f'~$heap_member(HOBJECT pdynamicproperty.TARGET, {state}.ALLOCATIONS)',
            f'$heap_owners($heap_graph({state}), HOBJECT pdynamicproperty.TARGET) = 0']
    cell='n_revived_'+state.removeprefix('S_')
    return [f'$heap_member(HOBJECT pdynamicproperty.TARGET, {state}.ALLOCATIONS)',
        f'$heap_owners($heap_graph({state}), HOBJECT pdynamicproperty.TARGET) = 1',
        f'$objectprops_at({state}.OBJECTPROPS, pdynamicproperty.TARGET) = (eps)',
        f'{state}_global = $global_table_view({state})',
        f'$lookup({state}_global.ENV, $ptascii("revived")) = ({cell})',
        f'{state}_global.STORE[{cell}] = DEFINED (POBJECT pdynamicproperty.TARGET)']


def pending_assertions(initial, expected, resurrect):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_entry', 0),
        'S_entry.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_entry_tail*',
        'perrorcall.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty',
        'pdynamicproperty.PENDING = eps', '~pdynamicproperty.RETIRED',
        '$property_dynamic_entry(S_entry, perrorcall, pdynamicproperty)',
        *seek('S_entry', 'S_release', 2),
        'S_release.TODO = (PROPERTY_DYNAMIC_RESULT pdynamicproperty_pending) :: ptask_release_tail*',
        'pdynamicproperty_pending.PENDING = (n_pending)',
        'pdynamicproperty_pending = pdynamicproperty[.PENDING = (n_pending)]',
        '$throwable_live(S_release, n_pending)',
        '$heap_owners($heap_graph(S_release), HOBJECT n_pending) = 1',
        '$heap_owners($heap_graph(S_release), HOBJECT pdynamicproperty.TARGET) = 1',
        'S_global = $global_table_view(S_release)',
        '$lookup(S_global.ENV, $ptascii("object")) = eps',
        *seek('S_release', 'S_cleanup', 4),
        'S_cleanup.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (PROPERTY_DYNAMIC_INSERT pdynamicproperty_cleared) :: ptask_cleanup_tail*',
        'S_cleanup.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = PROPERTY_DYNAMIC_RESULT pdynamicproperty_pending',
        'pdestructionoperation.PENDING = (n_pending)',
        'pdynamicproperty_cleared = pdynamicproperty_pending[.PENDING = eps][.RETIRED = true]',
        '$call_task_valid(S_cleanup, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
        '$heap_owners($heap_graph(S_cleanup), HOBJECT n_pending) = 1',
        *retired_receiver('S_cleanup', resurrect),
        *seek('S_cleanup', 'S_insert', 3),
        'S_insert.TODO = (PROPERTY_DYNAMIC_INSERT pdynamicproperty_insert) :: ptask_insert_tail*',
        'pdynamicproperty_insert = pdynamicproperty_pending[.RETIRED = true]',
        '$property_dynamic_valid(S_insert, pdynamicproperty_insert)',
        '$heap_owners($heap_graph(S_insert), HOBJECT n_pending) = 1',
        *retired_receiver('S_insert', resurrect),
        '$dynamic_output(S_insert.EVENTS) = $ptascii("warning|released|drop|")',
        'S_throw_found = $drive_steps(S_insert, 1)',
        'S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_SEARCH n_pending) :: ptask_insert_tail*',
        '$heap_owners($heap_graph(S_throw), HOBJECT n_pending) = 1',
        *valid('S_throw'),
        'S_done = $drive_steps(S_throw, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$dynamic_output(S_done.EVENTS) = '+cross.invoke.byte_expr(expected.encode()),
        *valid('S_done')]


def temporary_assertions(initial, used, expected):
    label = 'used' if used else 'unused'
    state = 'S_'+label
    record = 'pdynamicproperty_'+label
    rhs = 'n_rhs_'+label
    operation = 'pdestructionoperation_'+label
    call = 'pdestructorcall_'+label
    context = 'pcallcontext_'+label
    tail = 'ptask_'+label+'_tail*'
    return [state+'_initial = '+initial, '~'+state+'_initial.COMPILESTOP',
        *seek(state+'_initial', state+'_insert', 3),
        f'{state}_insert.TODO = (PROPERTY_DYNAMIC_INSERT {record}) :: {tail}',
        f'{record}.RHS = KNOWN (POBJECT {rhs})',
        f'{record}.SELECTED = {record}.RHS', f'~{record}.RETIRED',
        f'{record}.PENDING = eps', f'{record}.TARGET =/= {rhs}',
        f'$heap_owners($heap_graph({state}_insert), HOBJECT {record}.TARGET) = 1',
        f'$heap_owners($heap_graph({state}_insert), HOBJECT {rhs}) = 1',
        f'$objectprops_at({state}_insert.OBJECTPROPS, {record}.TARGET) = (eps)',
        *seek(state+'_insert', state+'_cleanup', 6),
        f'{state}_cleanup.CURRENT = ({context})',
        f'$destructor_context_call({context}, {state}_cleanup.CURRENT, {state}_cleanup.FRAMES) = ({call})',
        f'$destructor_context_valid({state}_cleanup, {context})',
        f'{call}.OBJECT = {record}.TARGET', f'{call}.OPERATION = ({operation})',
        f'{operation}.SOURCE = PROPERTY_DYNAMIC_INSERT {record}',
        f'{operation}.VALUE = '+(f'KNOWN (POBJECT {rhs})' if used else 'KNOWN PNULL'),
        f'{operation}.PENDING = eps',
        f'$heap_owners($heap_graph({state}_cleanup), HOBJECT {rhs}) = '+str(2 if used else 1),
        f'$objectprops_at({state}_cleanup.OBJECTPROPS, {record}.TARGET) = ([{{DECL eps, NAME ($ptascii("x")), STATE PROP_VALUE (DIRECT (POBJECT {rhs}))}}])',
        f'{state}_zero = $drive_steps({state}_cleanup, 0)',
        f'{state}_zero.COMPLETION = BUDGET',
        f'{state}_zero[.COMPLETION = NORMAL] = {state}_cleanup',
        f'{state}_one_found = $drive_steps({state}_cleanup, 1)',
        f'{state}_one_found.COMPLETION = BUDGET',
        f'{state}_one = {state}_one_found[.COMPLETION = NORMAL]', *valid(state+'_one'),
        f'{state}_done = $drive_steps({state}_one, 2048)',
        f'{state}_done.COMPLETION = NORMAL /\\ {state}_done.TODO = eps /\\ {state}_done.CURRENT = eps /\\ {state}_done.FRAMES = eps',
        f'~$heap_member(HOBJECT {record}.TARGET, {state}_done.ALLOCATIONS)',
        f'~$heap_member(HOBJECT {rhs}, {state}_done.ALLOCATIONS)',
        f'$dynamic_output({state}_done.EVENTS) = '+cross.invoke.byte_expr(expected.encode()),
        *valid(state+'_done')]


def exit_assertions(initial):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_entry', 0),
        'S_entry.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_entry_tail*',
        'perrorcall.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty',
        '$property_dynamic_entry(S_entry, perrorcall, pdynamicproperty)',
        *seek('S_entry', 'S_body', 1),
        *seek('S_body', 'S_invoke', 5),
        'S_invoke.TODO = (EXIT_INVOKE pexitcall) :: ptask_invoke_tail*',
        'S_invoke.FRAMES = pframe_exit :: pframe_exit_tail*',
        'pframe_exit.TODO = (ERROR_HANDLER_RESULT perrorcall_exit) :: ptask_exit_tail*',
        'perrorcall_exit.RESUME = PROPERTY_DYNAMIC_RESULT pdynamicproperty',
        'S_saved = $constant_frame_scope(S_invoke, pframe_exit, pframe_exit_tail*)',
        '$property_dynamic_valid(S_saved, pdynamicproperty)',
        '$error_entered_call_valid(S_saved, perrorcall_exit)',
        '$property_dynamic_exit_tasks(S_saved, pframe_exit.TODO)',
        '$property_dynamic_exit_pending(S_invoke)',
        '$heap_member(HOBJECT pdynamicproperty.TARGET, S_invoke.ALLOCATIONS)',
        '$objectprops_at(S_invoke.OBJECTPROPS, pdynamicproperty.TARGET) = (eps)',
        'S_received = $exit_receive(S_invoke[.TODO = ptask_invoke_tail*], pexitcall)',
        'S_received.COMPLETION = EXITED 0',
        'S_received.FRAMES = S_invoke.FRAMES',
        '$property_dynamic_exit_pending(S_received)',
        'S_stopped = $exit_start_unwind(S_received, 0)',
        'S_stopped.COMPLETION = UNSUPPORTED "dynamic property warning exit continuation"',
        'S_stopped.FRAMES = S_invoke.FRAMES',
        'S_stopped.SHUTDOWN = S_invoke.SHUTDOWN',
        '$dynamic_output(S_stopped.EVENTS) = $ptascii("warning|")',
        '$property_dynamic_exit_pending(S_stopped)',
        '$heap_valid($heap_graph(S_stopped))',
        'S_exit = $drive_steps(S_invoke, 2048)',
        'S_exit.COMPLETION = UNSUPPORTED "dynamic property warning exit continuation"',
        '$dynamic_output(S_exit.EVENTS) = $ptascii("warning|")',
        'S_exit.SHUTDOWN.PHASE = SHUTDOWN_PENDING',
        'S_exit.SHUTDOWN.ENTRIES = S_invoke.SHUTDOWN.ENTRIES',
        '|S_exit.SHUTDOWN.ENTRIES| = 1',
        *valid('S_exit')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=['reentry','retirement','resurrection','pending','pending-resurrection','temporary-cleanup','exit'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args=parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before=cross.snapshot(None)
    out=Path(tempfile.mkdtemp(prefix='dynamic-property-'+args.group+'-', dir=ROOT/'.tools'))
    name={'reentry':'dynamic-reentry-table', 'retirement':'dynamic-handler-retires-destination',
          'resurrection':'dynamic-retired-receiver-resurrects',
          'pending':'dynamic-handler-retires-and-throws',
          'pending-resurrection':'dynamic-retired-receiver-resurrects-pending',
          'exit':'dynamic-handler-exit-shutdown'}.get(args.group)
    report={'before':before, 'group':args.group, 'profile':cross.invoke.types.PROFILE,
            'passed':False, 'native_evaluations':0, 'model_evaluations':0,
            'state_assertions_evaluated':0, 'runner_mode':'SL', 'numeric_cap_seconds':120}
    print(out, flush=True)
    try:
        originals = []
        if args.group=='temporary-cleanup':
            clauses=[]
            hashes={}
            for used in [False,True]:
                name='dynamic-'+('used' if used else 'unused')+'-computed-receiver-rhs-cleanup'
                directory=out/name; directory.mkdir()
                source=directory/'source.php'; original=sources.CASES[name]
                source.write_bytes(original); originals.append((source,original))
                sources.prepare(directory,source)
                program='program_'+('used' if used else 'unused')
                initial='$php_run('+program+',0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
                clauses += [program+' = '+(directory/'program.watsup').read_text().strip(),
                    *temporary_assertions(initial,used,sources.EXPECTED[name])]
                hashes[name]=cross.invoke.sha(source)
            report['source_sha256']=hashes
        else:
            original=sources.BOUNDARIES[name][0] if args.group=='exit' else sources.CASES[name]
            source=out/'source.php'; source.write_bytes(original); originals.append((source,original))
            sources.prepare(out, source)
            initial='$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
            clauses=['program_source = '+(out/'program.watsup').read_text().strip(), *assertions(initial,args.group,sources.EXPECTED.get(name,''))]
            report['source_sha256']=cross.invoke.sha(source)
        fixture=out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+''.join('  -- if '+c+'\n' for c in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses,indent=2)+'\n')
        report.update(assertions=len(clauses),fixture_sha256=cross.invoke.sha(fixture))
        if not args.prepare_only:
            modules=json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result=cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',
                *[str(ROOT/module) for module in modules],str(fixture)],out/'numeric',120,ROOT)
            assert result.returncode==0 and result.stdout==b'true\n' and not result.stderr
            report['state_assertions_evaluated']=len(clauses)
        assert cross.snapshot(None)==before and all(path.read_bytes()==original for path,original in originals)
        report['passed']=True
    except BaseException as error:
        report['failure']={'type':type(error).__name__,'message':str(error)}
        raise
    finally:
        report['after']=cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(out/'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__=='__main__':
    main()

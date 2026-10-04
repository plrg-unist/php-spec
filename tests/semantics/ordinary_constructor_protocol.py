#!/usr/bin/env python3
"""Reached ordinary constructor slots survive effects without retaining raw objects."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from ordinary_constructor_sources import CASES, ROOT
OWN = ROOT / ".tools"
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $ordinary_owner_output(pevent*) : ptbytes
def $ordinary_owner_output(eps) = eps
def $ordinary_owner_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ordinary_owner_output(pevent*)
dec $ordinary_owner_is_output(pevent) : bool
def $ordinary_owner_is_output(OUTPUT ptbytes) = true
def $ordinary_owner_is_output(pevent) = false -- otherwise
def $ordinary_owner_output(pevent :: pevent_tail*) = $ordinary_owner_output(pevent_tail*)
  -- if ~$ordinary_owner_is_output(pevent)
dec $ordinary_owner_phase(pstate,nat) : bool
def $ordinary_owner_phase(S,0) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.CALL.MODE = CTOR_METHOD /\ pordinaryinternal.INDEX = 0
def $ordinary_owner_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if $ordinary_internal_string_record(pframe.TODO) = ((n,porigin,z,pordinaryinternal))
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if pordinaryinternal.CALL.MODE = CTOR_METHOD
def $ordinary_owner_phase(S,2) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.CALL.MODE = CTOR_METHOD /\ pordinaryinternal.INDEX = 1
def $ordinary_owner_phase(S,3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ORDINARY_CTOR_WARNING pordinaryinternal pvalue
  -- if pordinaryinternal.CALL.MODE = CTOR_METHOD
def $ordinary_owner_phase(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ORDINARY_CTOR_WARNING pordinaryinternal pvalue
  -- if perrorcall.TARGET = (pcallcontext.TARGET)
  -- if pordinaryinternal.CALL.MODE = CTOR_METHOD
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("receiver")) = eps
  -- if $lookup(S_global.ENV,$ptascii("previous")) = eps
def $ordinary_owner_phase(S,5) = true
  -- if S.TODO = (ORDINARY_CTOR_WARNING pordinaryinternal pvalue) :: ptask_tail*
  -- if pordinaryinternal.CALL.MODE = CTOR_METHOD
def $ordinary_owner_phase(S,6) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.CALL.MODE = CTOR_METHOD /\ pordinaryinternal.INDEX = 3
def $ordinary_owner_phase(S,7) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (ORDINARY_CTOR_STRING pordinaryinternal) :: ptask_tail*
  -- if $ordinary_internal_string_saved_site(S,S.FRAMES,porigin,z)
def $ordinary_owner_phase(S,n) = false -- otherwise
dec $ordinary_owner_saved_frame(pframe*,nat,porigin,int) : (pframe,pframe*)?
dec $ordinary_owner_frame_matches(pframe,nat,porigin,int) : bool
def $ordinary_owner_frame_matches(pframe,n,porigin,z) = true
  -- if $ordinary_internal_string_record(pframe.TODO) = ((n,porigin,z,pordinaryinternal))
def $ordinary_owner_frame_matches(pframe,n,porigin,z) = false -- otherwise
def $ordinary_owner_saved_frame(pframe :: pframe_tail*,n,porigin,z) = ((pframe,pframe_tail*))
  -- if $ordinary_owner_frame_matches(pframe,n,porigin,z)
def $ordinary_owner_saved_frame(pframe :: pframe_tail*,n,porigin,z) = $ordinary_owner_saved_frame(pframe_tail*,n,porigin,z)
  -- if ~$ordinary_owner_frame_matches(pframe,n,porigin,z)
def $ordinary_owner_saved_frame(eps,n,porigin,z) = eps
dec $ordinary_owner_seek(pstate,nat,nat) : pstate
def $ordinary_owner_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $ordinary_owner_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ordinary_owner_phase(S,n_phase)
def $ordinary_owner_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ordinary_owner_phase(S,n_phase)
def $ordinary_owner_seek(S,n_phase,n) = $ordinary_owner_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ordinary_owner_phase(S,n_phase) /\ $(n > 0)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $ordinary_owner_seek({parent},{phase},4096)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$ordinary_owner_phase({state},{phase})', *valid(state)]


def reject(name, expression, predicate):
    state = 'S_bad_' + name
    return [f'{state} = {expression}', f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})', '~' + predicate.replace('STATE', state)]


def owner(initial):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_ready',0),
        'S_ready.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal_ready) :: ptask_ready_tail*',
        'pordinaryinternal_ready.SOURCE = pordinaryinternal_ready.CALL',
        'pordinaryinternal_ready.VALUES = eps',
        'pordinaryinternal_ready.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_message)),NAMED_SENT (KNOWN pvalue_code),NAMED_SENT (KNOWN (POBJECT n_previous))]',
        'n_receiver = pordinaryinternal_ready.CALL.RECEIVER',
        '$reporting_lossy_value(pvalue_code) = ((4,ptbytes_warning))',
        '$ordinary_internal_receiving_valid(S_ready,pordinaryinternal_ready)',
        '$ordinary_internal_string_input(S_ready,pordinaryinternal_ready.SOURCE,0)',
        '(HOBJECT n_message) <- S_ready.ALLOCATIONS',
        '(HOBJECT n_previous) <- S_ready.ALLOCATIONS']
    for name, record in [
        ('index','pordinaryinternal_ready[.INDEX = 1]'),
        ('mode','pordinaryinternal_ready[.SOURCE = pordinaryinternal_ready.SOURCE[.MODE = CTOR_NEW]]'),
        ('base','pordinaryinternal_ready[.SOURCE = pordinaryinternal_ready.SOURCE[.BASE = "Error"]]'),
        ('line','pordinaryinternal_ready[.SOURCE = pordinaryinternal_ready.SOURCE[.LINE = $(pordinaryinternal_ready.SOURCE.LINE + 1)]]')]:
        checks += reject(name,'S_ready[.TODO = (ORDINARY_CTOR_RECEIVE '+record+') :: ptask_ready_tail*]',
                         '$ordinary_internal_receiving_valid(STATE,'+record+')')
    checks += [*seek('S_ready','S_string',1),
        'S_string.CURRENT = (pcallcontext_string)',
        'S_string.FRAMES = pframe_string :: pframe_string_tail*',
        'pframe_string.TODO = (STRINGIFY_RESULT n_message porigin_site z) :: (ORDINARY_CTOR_STRING pordinaryinternal_string) :: ptask_string_tail*',
        'pordinaryinternal_string = pordinaryinternal_ready',
        '$stringify_context(S_string,pcallcontext_string)',
        'S_string_owner = $constant_frame_scope(S_string,pframe_string,pframe_string_tail*)',
        '$ordinary_internal_user_string_valid(S_string_owner,pordinaryinternal_string)',
        '$ordinary_internal_string_marker(S_string_owner,n_message,porigin_site,z)']
    checks += reject('string_consumer',
        'S_string[.FRAMES = pframe_string[.TODO = (STRINGIFY_RESULT n_message porigin_site z) :: DISCARD :: ptask_string_tail*] :: pframe_string_tail*]',
        '$stringify_context(STATE,pcallcontext_string)')
    checks += [*seek('S_string','S_converted',2),
        'S_converted.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal_converted) :: ptask_converted_tail*',
        'pordinaryinternal_converted.VALUES = [PSTRING $ptascii("new")]',
        'pordinaryinternal_converted.SOURCE = pordinaryinternal_ready.SOURCE',
        '$named_slot_at(pordinaryinternal_converted.CALL.SENT,0) = NAMED_SENT (KNOWN (PSTRING $ptascii("new")))',
        '~((HOBJECT n_message) <- S_converted.ALLOCATIONS)',
        '$ordinary_internal_string_evidence(S_converted,n_message)',
        '$ordinary_internal_receiving_valid(S_converted,pordinaryinternal_converted)',
        '$ordinary_owner_output(S_converted.EVENTS) = $ptascii("T|")']
    wrong = 'pordinaryinternal_converted[.CALL = pordinaryinternal_converted.CALL[.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("wrong"))),NAMED_SENT (KNOWN pvalue_code),NAMED_SENT (KNOWN (POBJECT n_previous))]]]'
    checks += reject('rewritten_slot','S_converted[.TODO = (ORDINARY_CTOR_RECEIVE '+wrong+') :: ptask_converted_tail*]',
                     '$ordinary_internal_receiving_valid(STATE,'+wrong+')')
    checks += [*seek('S_converted','S_warning',3),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_warning_tail*',
        'perrorcall_warning.RESUME = ORDINARY_CTOR_WARNING pordinaryinternal_converted (PINT 4)',
        '$error_call_valid(S_warning,perrorcall_warning)',
        '$ordinary_internal_warning_valid(S_warning,pordinaryinternal_converted,PINT 4)',
        '$throwable_field(S_warning,n_receiver,"message") = PSTRING $ptascii("old")',
        '$throwable_field(S_warning,n_receiver,"code") = PINT 3',
        '$throwable_field(S_warning,n_receiver,"previous") = PNULL']
    warning_wrong = 'perrorcall_warning[.RESUME = ORDINARY_CTOR_WARNING pordinaryinternal_converted (PINT 5)]'
    checks += reject('warning_value','S_warning[.TODO = (ERROR_HANDLER_INVOKE '+warning_wrong+') :: ptask_warning_tail*]',
                     '$error_call_valid(STATE,'+warning_wrong+')')
    checks += [*seek('S_warning','S_handler',4),
        'S_handler.CURRENT = (pcallcontext_handler)',
        'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_handler) :: ptask_handler_tail*',
        'perrorcall_handler[.TARGET = eps] = perrorcall_warning',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        '$ordinary_internal_callback_context(S_handler,pcallcontext_handler)',
        'S_handler_owner = $constant_frame_scope(S_handler,pframe_handler,pframe_handler_tail*)',
        '$ordinary_internal_receiving_valid(S_handler_owner,pordinaryinternal_converted)',
        'S_global = $global_table_view(S_handler)',
        '$lookup(S_global.ENV,$ptascii("receiver")) = eps',
        '$lookup(S_global.ENV,$ptascii("previous")) = eps',
        '$(0 < $heap_owners($heap_graph(S_handler),HOBJECT n_receiver))',
        '$(0 < $heap_owners($heap_graph(S_handler),HOBJECT n_previous))',
        '~((HOBJECT n_message) <- S_handler.ALLOCATIONS)',
        '$ordinary_owner_output(S_handler.EVENTS) = $ptascii("T|H|")']
    handler_wrong = 'perrorcall_handler[.RESUME = ORDINARY_CTOR_WARNING pordinaryinternal_converted (PINT 5)]'
    checks += reject('handler_value','S_handler[.FRAMES = pframe_handler[.TODO = (ERROR_HANDLER_RESULT '+handler_wrong+') :: ptask_handler_tail*] :: pframe_handler_tail*]',
                     '$error_context_valid(STATE,pcallcontext_handler)')
    checks += [*seek('S_handler','S_returned',5),
        'S_returned.TODO = (ORDINARY_CTOR_WARNING pordinaryinternal_returned (PINT 4)) :: ptask_returned_tail*',
        'pordinaryinternal_returned = pordinaryinternal_converted',
        '$ordinary_internal_warning_valid(S_returned,pordinaryinternal_returned,PINT 4)',
        *seek('S_returned','S_complete',6),
        'S_complete.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal_complete) :: ptask_complete_tail*',
        'pordinaryinternal_complete.VALUES = [PSTRING $ptascii("new"),PINT 4,POBJECT n_previous]',
        '$named_slot_at(pordinaryinternal_complete.CALL.SENT,1) = NAMED_SENT (KNOWN pvalue_code)',
        '$throwable_field(S_complete,n_receiver,"message") = PSTRING $ptascii("old")',
        '$throwable_field(S_complete,n_receiver,"code") = PINT 3',
        'S_done = $drive_steps(S_complete,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$ordinary_owner_output(S_done.EVENTS) = $ptascii("T|H|new/4/p|gone/gone")',
        '~((HOBJECT n_message) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_previous) <- S_done.ALLOCATIONS)', *valid('S_done')]
    return checks


def recursive(initial):
    return ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *seek('S_initial','S_result',7),
        'S_result.TODO = (STRINGIFY_RESULT n_message porigin_site z) :: (ORDINARY_CTOR_STRING pordinaryinternal) :: ptask_tail*',
        '$stringify_result_valid(S_result,n_message,porigin_site,z)',
        '$ordinary_internal_user_string_valid(S_result,pordinaryinternal)',
        '$ordinary_internal_string_saved_site(S_result,S_result.FRAMES,porigin_site,z)',
        '$ordinary_owner_saved_frame(S_result.FRAMES,n_message,porigin_site,z) = ((pframe_outer,pframe_outer_tail*))',
        '$ordinary_internal_string_record(pframe_outer.TODO) = ((n_message,porigin_site,z,pordinaryinternal_outer))',
        'pordinaryinternal_outer.CALL.RECEIVER =/= pordinaryinternal.CALL.RECEIVER',
        r'pordinaryinternal_outer.CALL.MODE = CTOR_NEW /\ pordinaryinternal.CALL.MODE = CTOR_NEW',
        '$named_slot_at(pordinaryinternal_outer.CALL.SENT,0) = NAMED_SENT (KNOWN (POBJECT n_message))',
        'S_outer = $constant_frame_scope(S_result,pframe_outer,pframe_outer_tail*)',
        '$ordinary_internal_user_string_valid(S_outer,pordinaryinternal_outer)',
        'S_bad_consumer = S_result[.TODO = (STRINGIFY_RESULT n_message porigin_site z) :: (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_consumer))',
        '~$stringify_result_valid(S_bad_consumer,n_message,porigin_site,z)',
        '~$call_descriptors_valid(S_bad_consumer)',
        'S_done = $drive_steps(S_result,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$ordinary_owner_output(S_done.EVENTS) = $ptascii("T|H|F/m|T|H|F/m|")',
        *valid('S_done')]


def owner_group(initial, group):
    clauses = owner(initial)
    split = clauses.index('S_warning_found = $ordinary_owner_seek(S_converted,3,4096)')
    if group == 'string':
        return clauses[:split], split + 1, 0
    dependencies = [
        'S_initial = ' + initial, '~S_initial.COMPILESTOP',
        'S_ready_found = $ordinary_owner_seek(S_initial,0,4096)',
        r'S_ready_found.COMPLETION = NORMAL \/ S_ready_found.COMPLETION = BUDGET',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]',
        'S_ready.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal_ready) :: ptask_ready_tail*',
        'pordinaryinternal_ready.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_message)),NAMED_SENT (KNOWN pvalue_code),NAMED_SENT (KNOWN (POBJECT n_previous))]',
        'n_receiver = pordinaryinternal_ready.CALL.RECEIVER',
        'S_converted_found = $ordinary_owner_seek(S_ready,2,4096)',
        r'S_converted_found.COMPLETION = NORMAL \/ S_converted_found.COMPLETION = BUDGET',
        'S_converted = S_converted_found[.COMPLETION = NORMAL]',
        'S_converted.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal_converted) :: ptask_converted_tail*',
    ]
    return dependencies + clauses[split:], len(clauses) - split, len(dependencies) + 1


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['string','warning','recursive'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    name = 'ordinary-owned-method-retirement' if args.group != 'recursive' else 'ordinary-recursive-same-stringable-site'
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='ordinary-constructor-owner-' + args.group + '-', dir=OWN))
    source = out / 'source.php'; source.write_bytes(CASES[name])
    source_before = sha(source)
    report = {'passed':False,'before':before,'source':str(source),'source_sha256':source_before,
              'profile':cross.invoke.types.PROFILE,'mode':'unused' if args.elaborate_only else 'source-reached','group':args.group}
    print(out, flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,'-d',
            'extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        if args.group == 'recursive':
            body = recursive(initial); unique = len(body) + 1; dependencies = 0
        else:
            body, unique, dependencies = owner_group(initial, args.group)
        clauses = ['program_source = ' + checked['fixture'], *body]
        report.update(unique_original_assertions=unique, dependency_bindings=dependencies)
        (out / 'assertions.json').write_text(json.dumps(clauses,indent=2)+'\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+''.join('  -- if '+c+'\n' for c in clauses)+'\ndec $main() : bool\ndef $main() = '+('true' if args.elaborate_only else '$body()')+'\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),*[str(ROOT / p) for p in modules],str(fixture)],out / 'numeric',120,ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True,assertions=len(clauses),fixture_sha256=sha(fixture),state_assertions_evaluated=0 if args.elaborate_only else len(clauses),unused_body_assertions=len(clauses) if args.elaborate_only else 0)
    except BaseException as error:
        report['failure'] = {'type':type(error).__name__,'message':str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = cross.snapshot(args.freeze)
        report['source_unchanged'] = source_before == sha(source)
        report['passed'] = report['passed'] and report['before'] == report['after'] and report['source_unchanged']
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(out/'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Reached class-name operands and captured missing-read continuations."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / '.tools'
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
import object_class_name_sources as sources

PREFIX = r'''
dec $object_class_output(pevent*) : ptbytes
def $object_class_output(eps) = eps
def $object_class_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $object_class_output(pevent*)
dec $object_class_is_output(pevent) : bool
def $object_class_is_output(OUTPUT ptbytes) = true
def $object_class_is_output(pevent) = false -- otherwise
def $object_class_output(pevent :: pevent_tail*) = $object_class_output(pevent_tail*)
  -- if ~$object_class_is_output(pevent)
dec $object_class_phase(pstate,nat) : bool
def $object_class_phase(S,0) = true
  -- if S.TODO = (OBJECT_CLASS_NAME z) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
def $object_class_phase(S,1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = OBJECT_CLASS_NAME z
def $object_class_phase(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = OBJECT_CLASS_NAME z
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("missing")) = (n_cell)
  -- if S_global.STORE[n_cell] = DEFINED (POBJECT n)
def $object_class_phase(S,3) = true
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*
  -- if perrorread.ORIGINAL = OBJECT_CLASS_NAME z
def $object_class_phase(S,4) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $throwable_field(S,n,"previous") = POBJECT n_previous
  -- if $throwable_field(S,n_previous,"message") = PSTRING $ptascii("stop")
def $object_class_phase(S,n) = false -- otherwise
dec $object_class_seek(pstate,nat,nat) : pstate
def $object_class_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $object_class_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $object_class_phase(S,n_phase)
def $object_class_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$object_class_phase(S,n_phase)
def $object_class_seek(S,n_phase,n) = $object_class_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$object_class_phase(S,n_phase) /\ $(n > 0)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $object_class_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$object_class_phase({state},{phase})', *valid(state)]


def reject(name, expression, predicate):
    state = 'S_bad_' + name
    return [f'{state} = {expression}', f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})', '~' + predicate.replace('STATE', state)]


def completed(state, expected):
    return ['S_done = $drive_steps(' + state + ',2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$object_class_output(S_done.EVENTS) = ' + cross.invoke.byte_expr(expected), *valid('S_done')]


def temporary(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_task',0),
        'S_task.TODO = (OBJECT_CLASS_NAME z) :: ptask_tail*',
        'S_task.RESULT = KNOWN (POBJECT n_object)',
        'S_task.ORIGIN = (porigin)',
        '$origin_node(S_task.SOURCES,porigin) = (NExprClassConstFetch expression phpType20 metadata)',
        '$object_classname_task_valid(S_task,z)', '$getclass_live_object(S_task,n_object)',
        '$heap_owners($heap_graph(S_task),HOBJECT n_object) = 1',
        'S_dropped = S_task[.RESULT = KNOWN PNULL]',
        '$heap_owners($heap_graph(S_dropped),HOBJECT n_object) = 0']
    checks += reject('line','S_task[.TODO = (OBJECT_CLASS_NAME $(z + 1)) :: ptask_tail*]',
                     '$object_classname_task_valid(STATE,$(z + 1))')
    checks += reject('child','S_task[.ORIGIN = $origin_child(S_task.ORIGIN,[PCFIELD 0])]',
                     '$object_classname_task_valid(STATE,z)')
    checks += ['ptask_fixed = EVAL (NExprClassConstFetch (NScalarString (BYTES "Q2hpbGRDbGFzcw==") metadata) phpType20 metadata)']
    checks += reject('fixed','S_task[.TODO = ptask_fixed :: ptask_tail*]', '$call_task_valid(STATE,ptask_fixed)')
    checks += ['S_named_found = $drive_steps(S_task,1)', 'S_named_found.COMPLETION = BUDGET',
        'S_named = S_named_found[.COMPLETION = NORMAL]',
        'S_named.RESULT = KNOWN (PSTRING $ptascii("ChildClass"))',
        '~((HOBJECT n_object) <- S_named.ALLOCATIONS)', *valid('S_named'),
        *completed('S_named',expected)]
    return checks


def read(initial, expected, throwing):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_pending',1),
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorread.ORIGINAL = OBJECT_CLASS_NAME z',
        '$error_call_valid(S_pending,perrorcall)', '$error_read_valid(S_pending,perrorread)',
        'perrorread.RESULT = KNOWN PNULL', 'perrorread.TASK = OBJECT_CLASS_NAME z']
    for name, record in [('result','perrorread[.RESULT = KNOWN (PINT 1)]'),
                         ('task','perrorread[.TASK = DISCARD]'),
                         ('line','perrorread[.LINE = $(z + 1)]')]:
        checks += reject(name,'S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = ERROR_READ_RESULT '+record+']) :: ptask_tail*]',
                         '$error_read_valid(STATE,'+record+')')
    checks += reject('source','S_pending[.ORIGIN = $origin_child(S_pending.ORIGIN,[PCFIELD 0])]',
                     '$error_read_valid(STATE,perrorread)')
    if throwing:
        checks += [*seek('S_pending','S_chained',4),
            'S_chained.TODO = (THROW_SEARCH n_error) :: ptask_chained_tail*',
            r'$throwable_field(S_chained,n_error,"message") = PSTRING $ptascii("Cannot use \"::class\" on null")',
            '$throwable_field(S_chained,n_error,"previous") = POBJECT n_previous',
            '$object_name(S_chained,n_error) = $ptascii("TypeError")',
            '$object_name(S_chained,n_previous) = $ptascii("Exception")',
            '$throwable_chain_valid(S_chained,n_error)',
            '(HOBJECT n_error) <- S_chained.ALLOCATIONS', '(HOBJECT n_previous) <- S_chained.ALLOCATIONS',
            '$heap_owners($heap_graph(S_chained),HOBJECT n_previous) = 1',
            *completed('S_chained',expected)]
    else:
        checks += [*seek('S_pending','S_handler',2),
            'S_handler.CURRENT = (pcallcontext_handler)',
            'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
            'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_handler) :: ptask_handler_tail*',
            'perrorcall_handler[.TARGET = eps] = perrorcall',
            '$error_context_valid(S_handler,pcallcontext_handler)',
            'S_emitter = $constant_frame_scope(S_handler,pframe_handler,pframe_handler_tail*)',
            '$error_read_valid(S_emitter,perrorread)',
            'S_global = $global_table_view(S_handler)',
            '$lookup(S_global.ENV,$ptascii("missing")) = (n_cell)',
            'S_global.STORE[n_cell] = DEFINED (POBJECT n_created)',
            '$getclass_live_object(S_handler,n_created)',
            *seek('S_handler','S_returned',3),
            'S_returned.TODO = (ERROR_READ_RESULT perrorread) :: ptask_returned_tail*',
            '$getclass_live_object(S_returned,n_created)',
            'perrorread.RESULT = KNOWN PNULL',
            'S_resumed_found = $drive_steps(S_returned,1)', 'S_resumed_found.COMPLETION = BUDGET',
            'S_resumed = S_resumed_found[.COMPLETION = NORMAL]',
            'S_resumed.TODO = (OBJECT_CLASS_NAME z) :: ptask_returned_tail*',
            'S_resumed.RESULT = KNOWN PNULL', *valid('S_resumed'),
            *completed('S_resumed',expected)]
    return checks


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['temporary','returned','thrown'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    name = {'temporary':'dynamic-class-child-once','returned':'dynamic-class-handler-redefines-cv',
            'thrown':'dynamic-class-undefined-handler-throw-previous'}[args.group]
    expected = sources.EXPECTED[name]
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='object-class-protocol-' + args.group + '-', dir=OWN))
    source = out / 'source.php'
    source.write_bytes(sources.CASES[name])
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
        body = temporary(initial,expected) if args.group == 'temporary' else read(initial,expected,args.group == 'thrown')
        clauses = ['program_source = ' + checked['fixture'], *body]
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

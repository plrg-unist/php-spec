#!/usr/bin/env python3
"""Actual internal reception callbacks retain owned values and reject forged consumers."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from internal_default_reception_sources import CASES, ROOT
from internal_default_constructor_sources import OWNER_SOURCE
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $internal_effect_phase(pstate,nat) : bool
def $internal_effect_phase(S,0) = true
  -- if S.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal) :: ptask_tail*
  -- if pdefaultinternal.INDEX = 0
def $internal_effect_phase(S,1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal pvalue
def $internal_effect_phase(S,2) = true
  -- if S.TODO = (DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal pvalue) :: ptask_tail*
def $internal_effect_phase(S,3) = true
  -- if S.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal) :: ptask_tail*
  -- if pdefaultinternal.INDEX = 3
def $internal_effect_phase(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (DEFAULT_INTERNAL_CTOR_STRING pdefaultinternal) :: ptask_tail*
def $internal_effect_phase(S,5) = true
  -- if S.TODO = (DEFAULT_INTERNAL_CTOR_STRING pdefaultinternal) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $internal_effect_phase(S,6) = true
  -- if S.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal) :: ptask_tail*
  -- if pdefaultinternal.INDEX = 6
def $internal_effect_phase(S,7) = true
  -- if S.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall) :: ptask_tail*
  -- if pctorcall.INDEX = 3
def $internal_effect_phase(S,8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal pvalue
def $internal_effect_phase(S,n) = false -- otherwise
dec $internal_effect_seek(pstate,nat,nat) : pstate
def $internal_effect_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $internal_effect_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $internal_effect_phase(S,n_phase)
def $internal_effect_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$internal_effect_phase(S,n_phase)
def $internal_effect_seek(S,n_phase,n) = $internal_effect_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$internal_effect_phase(S,n_phase) /\ $(n > 0)
dec $internal_effect_output(pevent*) : ptbytes
def $internal_effect_output(eps) = eps
def $internal_effect_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $internal_effect_output(pevent*)
dec $internal_effect_is_output(pevent) : bool
def $internal_effect_is_output(OUTPUT ptbytes) = true
def $internal_effect_is_output(pevent) = false -- otherwise
def $internal_effect_output(pevent :: pevent_tail*) = $internal_effect_output(pevent_tail*)
  -- if ~$internal_effect_is_output(pevent)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$class_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $internal_effect_seek({parent},{phase},4096)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$internal_effect_phase({state},{phase})', *valid(state)]


def reject(name, expression):
    return [f'S_bad_{name} = {expression}', f'$heap_valid($heap_graph(S_bad_{name}))',
            f'~$call_descriptors_valid(S_bad_{name})']


def assertions(initial, initial_pure, initial_builtin):
    return [
        'S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *seek('S_initial','S_ready',0),
        'S_ready.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_ready) :: ptask_ready*',
        'S_ready.CURRENT = (pcallcontext_ready)',
        'pdefaultinternal_ready.NEW.VALUES = [PNULL,POBJECT n_filename]',
        'pdefaultinternal_ready.CALL.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 0)),NAMED_SENT (KNOWN (PINT 1)),NAMED_SENT (KNOWN (POBJECT n_filename))]',
        '$default_internal_receiving_valid(S_ready,pdefaultinternal_ready)',
        *reject('source','S_ready[.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_ready[.NEW.SITE = pcallcontext_ready.FUNCTION]) :: ptask_ready*]'),
        *reject('line','S_ready[.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_ready[.CALL.LINE = $(pdefaultinternal_ready.CALL.LINE + 1)]) :: ptask_ready*]'),
        *reject('prefix','S_ready[.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_ready[.VALUES = [PINT 0]][.INDEX = 1]) :: ptask_ready*]'),
        *seek('S_ready','S_pending',1),
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall_pending) :: ptask_pending*',
        'perrorcall_pending.RESUME = DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal_ready (PSTRING eps)',
        'perrorcall_bad = perrorcall_pending[.RESUME = DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal_ready (PSTRING $ptascii("bad"))]',
        *reject('pending_warning','S_pending[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_pending*]'),
        *seek('S_pending','S_handler',8),
        'S_handler.CURRENT = (pcallcontext_handler)',
        'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_handler) :: ptask_handler*',
        'perrorcall_handler.RESUME = DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal_ready (PSTRING eps)',
        '$error_context_kind(S_handler,pcallcontext_handler)',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        '$default_internal_callback_context(S_handler,pcallcontext_handler)',
        'S_emitter = $constant_frame_scope(S_handler,pframe_handler,pframe_handler_tail*)',
        '$default_internal_warning_valid(S_emitter,pdefaultinternal_ready,PSTRING eps)',
        '$error_call_valid(S_emitter,perrorcall_handler)',
        'perrorcall_handler_bad = perrorcall_handler[.RESUME = DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal_ready (PSTRING $ptascii("bad"))]',
        'pframe_handler_bad = pframe_handler[.TODO = (ERROR_HANDLER_RESULT perrorcall_handler_bad) :: ptask_handler*]',
        *reject('active_warning','S_handler[.FRAMES = pframe_handler_bad :: pframe_handler_tail*]'),
        '~$default_internal_callback_context(S_bad_active_warning,pcallcontext_handler)',
        *seek('S_handler','S_warning',2),
        'S_warning.TODO = (DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal_ready (PSTRING eps)) :: ptask_warning*',
        '$internal_effect_output(S_warning.EVENTS) = $ptascii("D4|")',
        *reject('result_warning','S_warning[.TODO = (DEFAULT_INTERNAL_CTOR_WARNING pdefaultinternal_ready (PINT 0)) :: ptask_warning*]'),
        *seek('S_warning','S_string_ready',3),
        'S_string_ready.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_string) :: ptask_string*',
        'pdefaultinternal_string.NEW = pdefaultinternal_ready.NEW',
        'pdefaultinternal_string.VALUES = [PSTRING eps,PINT 0,PINT 1]',
        '$heap_owners($heap_graph(S_string_ready),HOBJECT n_filename) = 2',
        'S_missing_owner = S_string_ready[.TODO = ptask_string*]',
        '$heap_owners($heap_graph(S_missing_owner),HOBJECT n_filename) = 0',
        '$heap_owners($heap_graph(S_missing_owner),HOBJECT pdefaultinternal_string.NEW.OBJECT) = 0',
        *seek('S_string_ready','S_string',4),
        'S_string.CURRENT = (pcallcontext_string)',
        'S_string.FRAMES = pframe_string :: pframe_tail*',
        'pframe_string.TODO = (STRINGIFY_RESULT n_filename porigin_site z) :: (DEFAULT_INTERNAL_CTOR_STRING pdefaultinternal_string) :: ptask_consumer*',
        '$default_internal_string_context_data(S_string,pcallcontext_string,S_string.CURRENT,S_string.FRAMES) = (pdefaultinternal_string)',
        '$default_internal_callback_context(S_string,pcallcontext_string)',
        'S_scope = $constant_frame_scope(S_string,pframe_string,pframe_tail*)',
        '$default_internal_string_marker(S_scope,n_filename,porigin_site,z)',
        'pframe_forged = pframe_string[.TODO = (STRINGIFY_RESULT n_filename porigin_site z) :: DISCARD :: ptask_consumer*]',
        *reject('string_consumer','S_string[.FRAMES = pframe_forged :: pframe_tail*]'),
        '~$default_internal_callback_context(S_bad_string_consumer,pcallcontext_string)',
        *seek('S_string','S_string_return',5),
        'S_string_return.TODO = (DEFAULT_INTERNAL_CTOR_STRING pdefaultinternal_string) :: ptask_string_return*',
        'S_string_return.RESULT = KNOWN (PSTRING $ptascii("after"))',
        *seek('S_string_return','S_received',6),
        'S_received.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_received) :: ptask_received*',
        'pdefaultinternal_received.VALUES = [PSTRING eps,PINT 0,PINT 1,PSTRING $ptascii("after"),PNULL,PNULL]',
        'pdefaultinternal_received.CALL.SENT = [NAMED_SENT (KNOWN (PSTRING eps)),NAMED_SENT (KNOWN (PINT 0)),NAMED_SENT (KNOWN (PINT 1)),NAMED_SENT (KNOWN (PSTRING $ptascii("after")))]',
        'S_done = $drive_steps(S_received,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$internal_effect_output(S_done.EVENTS) = $ptascii("D4|Tafter|F|after")',
        '~((HOBJECT n_filename) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pdefaultinternal_received.NEW.OBJECT) <- S_done.ALLOCATIONS)',
        r'S_done.CONSTCONTEXT = eps /\ S_done.PARAMETERBACKINGS = eps /\ S_done.HELD = eps',
        *valid('S_done'),
        'S_pure_initial = ' + initial_pure, '~S_pure_initial.COMPILESTOP',
        *seek('S_pure_initial','S_pure',7),
        'S_pure.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew_pure pctorcall_pure) :: ptask_pure*',
        '$default_internal_valid(S_pure,pdefaultnew_pure,pctorcall_pure)',
        '~$default_internal_effects(S_pure,pctorcall_pure,0)',
        'pdefaultinternal_forged = {NEW pdefaultnew_pure,CALL pctorcall_pure[.SENT = $default_internal_fill(pctorcall_pure.BASE,pctorcall_pure.SENT,0)],INDEX 0,VALUES eps}',
        '~$default_internal_receiving_valid(S_pure,pdefaultinternal_forged)',
        *reject('pure_effect','S_pure[.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_forged) :: ptask_pure*]'),
        'S_pure_done = $drive_steps(S_pure,4096)',
        '$internal_effect_output(S_pure_done.EVENTS) = $ptascii("outer/7/inner")',
        r'S_pure_done.COMPLETION = NORMAL /\ S_pure_done.TODO = eps /\ S_pure_done.CURRENT = eps /\ S_pure_done.FRAMES = eps',
        *valid('S_pure_done'),
        'S_builtin_initial = ' + initial_builtin, '~S_builtin_initial.COMPILESTOP',
        *seek('S_builtin_initial','S_builtin',0),
        'S_builtin.TODO = (DEFAULT_INTERNAL_CTOR_RECEIVE pdefaultinternal_builtin) :: ptask_builtin*',
        'pdefaultinternal_builtin.NEW.VALUES = [POBJECT n_builtin]',
        '$class_instanceof(S_builtin,POBJECT n_builtin,$ptascii("Stringable"))',
        '~$stringable_instance(S_builtin,n_builtin)',
        '$default_internal_string_valid(S_builtin,pdefaultinternal_builtin)',
        '~$default_internal_user_string_valid(S_builtin,pdefaultinternal_builtin)',
        *reject('builtin_marker','S_builtin[.TODO = (STRINGIFY_RESULT n_builtin pdefaultinternal_builtin.CALL.SITE pdefaultinternal_builtin.CALL.LINE) :: (DEFAULT_INTERNAL_CTOR_STRING pdefaultinternal_builtin) :: ptask_builtin*]'),
        '~$stringify_result_valid(S_bad_builtin_marker,n_builtin,pdefaultinternal_builtin.CALL.SITE,pdefaultinternal_builtin.CALL.LINE)',
        'S_builtin_done = $drive_steps(S_builtin,4096)',
        '$internal_effect_output(S_builtin_done.EVENTS) = $ptascii("Exception: inner")',
        r'S_builtin_done.COMPLETION = NORMAL /\ S_builtin_done.TODO = eps /\ S_builtin_done.CURRENT = eps /\ S_builtin_done.FRAMES = eps',
        '~((HOBJECT n_builtin) <- S_builtin_done.ALLOCATIONS)',
        '~((HOBJECT pdefaultinternal_builtin.NEW.OBJECT) <- S_builtin_done.ALLOCATIONS)',
        *valid('S_builtin_done')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--elaborate-only', action='store_true')
    parser.add_argument('--prefix', type=int)
    parser.add_argument('--group', choices=['owner','pure','builtin'])
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='internal-default-effects-owner-', dir=ROOT / '.tools'))
    SOURCE = out / 'owner.php'; SOURCE.write_bytes(CASES['internal-filename-owner-retirement'])
    PURE_SOURCE = out / 'pure.php'; PURE_SOURCE.write_bytes(OWNER_SOURCE)
    BUILTIN_SOURCE = out / 'builtin.php'; BUILTIN_SOURCE.write_bytes(CASES['internal-builtin-throwable-stringable'])
    report = {'passed': False, 'head': before['identity']['head'], 'before': before,
              'sources': {str(p): sha(p) for p in [SOURCE,PURE_SOURCE,BUILTIN_SOURCE]}, 'profile': cross.invoke.types.PROFILE,
              'mode': 'unused' if args.elaborate_only else 'source-reached'}
    print(out, flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        bindings = []
        for name, source in [('program_source',SOURCE),('program_pure',PURE_SOURCE),('program_builtin',BUILTIN_SOURCE)]:
            parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
            assert checked['ok'] is True
            bindings.append(name + ' = ' + checked['fixture'])
        def initial(name, source):
            return '$php_run(' + name + ',0,' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        clauses = [*bindings,*assertions(initial('program_source',SOURCE),initial('program_pure',PURE_SOURCE),initial('program_builtin',BUILTIN_SOURCE))]
        if args.group:
            assert not args.prefix
            markers = ['S_initial = ', 'S_pure_initial = ', 'S_builtin_initial = ']
            index = ['owner','pure','builtin'].index(args.group)
            start = next(n for n,c in enumerate(clauses) if c.startswith(markers[index]))
            end = next(n for n,c in enumerate(clauses) if index < 2 and c.startswith(markers[index+1])) if index < 2 else len(clauses)
            clauses = [bindings[index],*clauses[start:end]]
            report['group'] = args.group
        if args.prefix:
            assert not args.elaborate_only and 3 < args.prefix <= len(clauses)
            clauses = clauses[:args.prefix]
            report['mode'] = 'prefix-probe'
        (out/'assertions.json').write_text(json.dumps(clauses,indent=2)+'\n')
        body = 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + c + '\n' for c in clauses)
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = ' + ('true' if args.elaborate_only else '$body()') + '\n')
        modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*[str(ROOT/module) for module in modules],str(fixture)],out/'numeric',120,ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True,assertions=len(clauses),fixture_sha256=sha(fixture),state_assertions_evaluated=0 if args.elaborate_only else len(clauses),unused_body_assertions=len(clauses) if args.elaborate_only else 0)
    except BaseException as error:
        report['failure'] = {'type':type(error).__name__,'message':str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['sources_unchanged'] = report['sources'] == {str(p):sha(p) for p in [SOURCE,PURE_SOURCE,BUILTIN_SOURCE]}
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['sources_unchanged'] and report['before'] == report['after']
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(out/'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

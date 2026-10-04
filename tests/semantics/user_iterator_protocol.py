#!/usr/bin/env python3
"""Source-reached implicit Iterator frames, retained values and abrupt cleanup."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import user_iterator as source

ROOT = source.ROOT
PREFIX = r'''
dec $iterator_test_phase(pstate,nat) : bool
def $iterator_test_phase(S,0) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_site) z) :: (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*
def $iterator_test_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*
def $iterator_test_phase(S,2) = true
  -- if S.TODO = (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*
def $iterator_test_phase(S,3) = true
  -- if S.TODO = (USERITER_NEXT n n_object statement porigin_site z poperand) :: ptask_tail*
def $iterator_test_phase(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (USERITER_RESULT n n_object statement porigin_site z "next" poperand) :: ptask_tail*
def $iterator_test_phase(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe_inner :: pframe_middle :: pframe_outer :: pframe_tail*
  -- if pframe_inner.TODO = (USERITER_RESULT n_inner n_object statement_inner porigin_inner z_inner "current" poperand_inner) :: ptask_inner_tail*
  -- if pframe_middle.TODO = (USERITER_RESULT n_middle n_object statement_inner porigin_inner z_inner "current" poperand_middle) :: ptask_middle_tail*
  -- if pframe_outer.TODO = (USERITER_RESULT n_outer n_object statement_outer porigin_outer z_outer "current" poperand_outer) :: ptask_outer_tail*
def $iterator_test_phase(S,6) = true
  -- if S.TODO = (ERROR_UNWIND (USERFATAL ptbytes z_fatal b)) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_caller_tail*
def $iterator_test_phase(S,7) = true
  -- if S.TODO = (USERITER_RESULT n n_object statement porigin_site z "current" poperand) :: ptask_tail*
  -- if ~$useriter_has_key(statement)
def $iterator_test_phase(S,n) = false -- otherwise
dec $iterator_test_seek(pstate,nat,nat) : pstate
def $iterator_test_seek(S,n_phase,n) = S -- if $iterator_test_phase(S,n_phase)
def $iterator_test_seek(S,n_phase,n) = S -- if ~$iterator_test_phase(S,n_phase) /\ S.COMPILESTOP
def $iterator_test_seek(S,n_phase,n) = S
  -- if ~$iterator_test_phase(S,n_phase)
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $iterator_test_seek(S,n_phase,0) = S -- if ~$iterator_test_phase(S,n_phase)
def $iterator_test_seek(S,n_phase,n) = $iterator_test_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~$iterator_test_phase(S,n_phase)
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $iterator_test_output(pevent) : bool
def $iterator_test_output(OUTPUT ptbytes) = true
def $iterator_test_output(pevent) = false -- otherwise
dec $iterator_test_outputs(pevent*) : ptbytes
def $iterator_test_outputs(eps) = eps
def $iterator_test_outputs((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $iterator_test_outputs(pevent_tail*)
def $iterator_test_outputs(pevent :: pevent_tail*) = $iterator_test_outputs(pevent_tail*) -- if ~$iterator_test_output(pevent)
'''
OWNERS = source.source('$spare=new It;foreach(new It as $k=>$v){$v=null;echo "B";}echo "D";', {
    'current': 'function current():mixed {echo "C";return $this->a;}',
    'key': 'function key():mixed {echo "K";unset($this->a);return 0;}',
    'valid': 'function valid():bool {echo "V";return $this->i<1;}'},
    'public $i=0;public $a;function __construct(){$this->a=[&$GLOBALS["cell"]];}', prefix='$cell=7;')
NESTED = source.source('foreach(new It as $v){echo "B";}echo "D";', {
    'current': 'function current():mixed {echo "C";$this->depth++;if($this->depth<3){foreach($this as $v){echo "I";break;}}$this->depth--;return 10;}',
    'valid': 'function valid():bool {echo "V";return $this->i<1;}'}, 'public $i=0;public $depth=0;')
FATAL = OWNERS.replace(b'unset($this->a);return 0;', b'unset($this->a);@trigger_error("fatal",256);return 0;')
VALUE = source.source('foreach(new It as $v){echo "B";}echo "D";', {
    'valid': 'function valid():bool {echo "V";return $this->i<1;}'})
CASES = {'owners': (OWNERS, b'RVCKBNVD'), 'nested': (NESTED, b'RVCRVCRVCIIBNVD'),
         'fatal': (FATAL, b'RVCK'), 'value-only': (VALUE, b'RVCBNVD'),
         'cursor': (VALUE.replace(b' as $v)', b' as $k=>$v)'), b'RVCKBNVD'),
         'cursor-claims': (VALUE.replace(b' as $v)', b' as $k=>$v)'), b'RVCKBNVD'),
         'cursor-alias': (NESTED, b'RVCRVCRVCIIBNVD')}


def seek(state, previous, phase):
    return [f'{state}_found = $iterator_test_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$iterator_test_phase({state},{phase})']


def valid(state, full=False):
    # Later states change neither sources nor declarations. Check their mandatory
    # live gates directly; the first checkpoint checks the full public boundary.
    gates = [f'$call_tasks_valid({state},{state}.TODO)',
             f'$call_frames_valid({state},{state}.FRAMES)', f'$call_current_valid({state})',
             f'$useriter_chain_valid({state},{state}.CURRENT,{state}.FRAMES)',
             f'$heap_valid($heap_graph({state}))']
    return ([f'$call_descriptors_valid({state})'] if full else []) + gates


def rejected(checks, name, expression, heap=True, gate='tasks'):
    state = 'S_bad_' + name
    checks += [state + ' = ' + expression]
    if heap:
        checks += [f'$heap_valid($heap_graph({state}))']
    predicate = {'tasks': f'$call_tasks_valid({state},{state}.TODO)',
                 'chain': f'$useriter_chain_valid({state},{state}.CURRENT,{state}.FRAMES)',
                 'public': f'$call_descriptors_valid({state})'}[gate]
    checks += ['~' + predicate]


def assertions(checked, path, directory, name):
    checks = ['S_initial = $php_file_run(' + checked['fixture'] + ',0,' +
              source.driver.byte_expr(os.fsencode(path)) + ',' + source.driver.byte_expr(os.fsencode(directory)) + ')',
              '~S_initial.COMPILESTOP']
    if name == 'owners':
        checks += seek('S', 'S_initial', 0) + valid('S', True)
        checks += r'''
S.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_site) z) :: (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*
poperand = KNOWN (PARRAY n_array)
$iterator_lookup(S.ITERATORS,n) = (OBJECTITER n n_object 0 false)
$useriter_pending(S,METHOD_TARGET n_object porigin_method,porigin_site)
$useriter_method_selected(S,n_object,porigin_method,"key")
(HARRAY n_array) <- $task_nodes(USERITER_RESULT n n_object statement porigin_site z "key" poperand)
$trace_slot(S,S.ENV,$ptascii("spare")) = POBJECT n_spare
n_spare =/= n_object
S.OBJECTS[n_object] = INSTANCE porigin_class
$effective_method(S,porigin_class,$ptascii("current"),|S.CLASSES|) = (pmethoddesc_current)
porigin_current = pmethoddesc_current.FUNCTION.ORIGIN
porigin_current =/= porigin_method
'''.strip().splitlines()
        pending = '(CALL_ARGS __TARGET__ eps 0 eps (__SITE__) __LINE__) :: (USERITER_RESULT __ID__ __OBJECT__ statement __SITE__ __LINE__ __STAGE__ poperand) :: ptask_tail*'
        for label, replacement in [('stage', '"valid"'), ('id', '$(n + 100)'),
                                   ('object', 'n_spare'), ('line', '$(z + 1)')]:
            todo = pending.replace('__TARGET__', '(METHOD_TARGET n_object porigin_method)').replace('__SITE__', 'porigin_site').replace('__LINE__', replacement if label == 'line' else 'z').replace('__ID__', replacement if label == 'id' else 'n').replace('__OBJECT__', replacement if label == 'object' else 'n_object').replace('__STAGE__', replacement if label == 'stage' else '"key"')
            rejected(checks, label, 'S[.TODO = ' + todo + ']')
        rejected(checks, 'method', 'S[.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_current) eps 0 eps (porigin_site) z) :: (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*]')
        rejected(checks, 'site', 'S[.ORIGIN = (porigin_current)][.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_current) z) :: (USERITER_RESULT n n_object statement porigin_current z "key" poperand) :: ptask_tail*]')
        rejected(checks, 'cursor', 'S[.ITERATORS = [OBJECTITER n n_object 1 false]]', gate='public')
        checks += seek('S_entered', 'S', 1) + valid('S_entered')
        checks += r'''
S_entered.CURRENT = (pcallcontext)
S_entered.FRAMES = pframe :: pframe_tail*
pframe.TODO = (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*
$useriter_frame(S_entered,pcallcontext,pframe)
pcallcontext.CALLSITE = (porigin_site)
pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
pcallcontext.ARGC = 0
pcallcontext.LINE = z
'''.strip().splitlines()
        rejected(checks, 'entered_argc', 'S_entered[.CURRENT = (pcallcontext[.ARGC = 1])]', gate='chain')
        rejected(checks, 'entered_line', 'S_entered[.CURRENT = (pcallcontext[.LINE = $(z + 1)])]', gate='chain')
        rejected(checks, 'detached', 'S_entered[.FRAMES = pframe[.TODO = ptask_tail*] :: pframe_tail*]', gate='chain')
        checks += seek('S_restored', 'S_entered', 2) + valid('S_restored')
        checks += ['S_restored.TODO = (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*',
                   'S_restored.RESULT = KNOWN (PINT 0)', '(HARRAY n_array) <- S_restored.ALLOCATIONS']
        checks += seek('S_body', 'S_restored', 3) + valid('S_body')
        checks += ['S_body.TODO = (USERITER_NEXT n n_object statement porigin_site z poperand) :: ptask_tail*',
                   '$heap_owners($heap_graph(S_body),HARRAY n_array) = 1',
                   '$iterator_test_outputs(S_body.EVENTS) = $ptascii("RVCKB")']
        rejected(checks, 'ordinary_marker', 'S_body[.TODO = (FOREACH_NEXT n (HOBJECT n_object) statement (porigin_site) z) :: ptask_tail*]')
        checks += ['n_dead = |S_body.STORE|']
        rejected(checks, 'dead_reference', 'S_body[.TODO = (USERITER_NEXT n n_object statement porigin_site z (REFERENCE n_dead)) :: ptask_tail*]', False)
        checks += seek('S_next', 'S_body', 4) + valid('S_next')
        checks += ['~((HARRAY n_array) <- S_next.ALLOCATIONS)',
                   '$iterator_lookup(S_next.ITERATORS,n) = (OBJECTITER n n_object 0 false)']
        previous = 'S_next'
    elif name in ('nested', 'cursor-alias'):
        checks += seek('S', 'S_initial', 5) + valid('S', True)
        checks += r'''
S.CURRENT = (pcallcontext_inner)
S.FRAMES = pframe_inner :: pframe_middle :: pframe_outer :: pframe_tail*
pframe_inner.TODO = (USERITER_RESULT n_inner n_object statement_inner porigin_inner z_inner "current" poperand_inner) :: ptask_inner_tail*
pframe_middle.TODO = (USERITER_RESULT n_middle n_object statement_inner porigin_inner z_inner "current" poperand_middle) :: ptask_middle_tail*
pframe_outer.TODO = (USERITER_RESULT n_outer n_object statement_outer porigin_outer z_outer "current" poperand_outer) :: ptask_outer_tail*
pframe_inner.CONTEXT = (pcallcontext_middle)
pcallcontext_inner.CALLSITE = (porigin_inner)
pcallcontext_middle.CALLSITE = (porigin_inner)
n_inner =/= n_middle
n_middle =/= n_outer
$useriter_frame(S,pcallcontext_inner,pframe_inner)
$useriter_frame(S,pcallcontext_middle,pframe_middle)
'''.strip().splitlines()
        if name == 'nested':
            rejected(checks, 'saved_line', 'S[.FRAMES = pframe_inner[.CONTEXT = (pcallcontext_middle[.LINE = $(z_inner + 1)])] :: pframe_middle :: pframe_outer :: pframe_tail*]', gate='chain')
            rejected(checks, 'saved_marker_stage', 'S[.FRAMES = pframe_inner :: pframe_middle[.TODO = (USERITER_RESULT n_middle n_object statement_inner porigin_inner z_inner "valid" poperand_middle) :: ptask_middle_tail*] :: pframe_outer :: pframe_tail*]', gate='chain')
        else:
            checks += ['pframe_alias = pframe_inner[.TODO = (USERITER_RESULT n_middle n_object statement_inner porigin_inner z_inner "current" poperand_inner) :: ptask_inner_tail*]',
                       '$useriter_cursor_valid(S,n_middle,n_object)',
                       '$useriter_frame(S,pcallcontext_inner,pframe_alias)']
            rejected(checks, 'saved_cursor_alias', 'S[.FRAMES = pframe_alias :: pframe_middle :: pframe_outer :: pframe_tail*]', gate='public')
        previous = 'S'
    elif name == 'fatal':
        checks += seek('S', 'S_initial', 6) + valid('S', True)
        checks += r'''
S.TODO = (ERROR_UNWIND pcompletion) :: ptask_tail*
pcompletion = USERFATAL ($ptascii("fatal")) z_fatal true
S.FRAMES = pframe :: pframe_tail*
pframe.TODO = (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_caller_tail*
poperand = KNOWN (PARRAY n_array)
$iterator_lookup(S.ITERATORS,n) = (OBJECTITER n n_object 0 false)
(HARRAY n_array) <- S.ALLOCATIONS
S_after = $drive_steps(S,1)
$iterator_lookup(S_after.ITERATORS,n) = eps
~((HARRAY n_array) <- S_after.ALLOCATIONS)
'''.strip().splitlines()
        checks += valid('S_after')
        previous = 'S_after'
    elif name == 'cursor-claims':
        checks += seek('S', 'S_initial', 0) + valid('S', True)
        checks += ['S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_site) z) :: (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*',
                   '$useriter_cursor_valid(S,n,n_object)']
        rejected(checks, 'pending_claim', 'S[.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_site) z) :: (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*]', gate='chain')
        checks += seek('S_body', 'S', 3) + valid('S_body')
        checks += ['S_body.TODO = (USERITER_NEXT n n_object statement porigin_site z poperand_body) :: ptask_body_tail*']
        rejected(checks, 'body_claim', 'S_body[.TODO = (USERITER_NEXT n n_object statement porigin_site z poperand_body) :: (USERITER_NEXT n n_object statement porigin_site z poperand_body) :: ptask_body_tail*]', gate='chain')
        rejected(checks, 'wrapped_claim', 'S_body[.TODO = (USERITER_NEXT n n_object statement porigin_site z poperand_body) :: (AT porigin_site (USERITER_NEXT n n_object statement porigin_site z poperand_body)) :: ptask_body_tail*]', gate='chain')
        previous = 'S_body'
    elif name == 'cursor':
        checks += seek('S', 'S_initial', 0) + valid('S', True)
        checks += ['S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_site) z) :: (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*',
                   '$useriter_cursor_valid(S,n,n_object)', 'n_high = S.NEXTITER']
        rejected(checks, 'counter', 'S[.NEXTITER = n]')
        rejected(checks, 'duplicate', 'S[.ITERATORS = [OBJECTITER n n_object 0 false, OBJECTITER n n_object 0 false]]')
        rejected(checks, 'future_id', 'S[.ITERATORS = [OBJECTITER n_high n_object 0 false]][.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_site) z) :: (USERITER_RESULT n_high n_object statement porigin_site z "key" poperand) :: ptask_tail*]', gate='public')
        checks += seek('S_body', 'S', 3) + valid('S_body')
        checks += ['S_body.TODO = (USERITER_NEXT n n_object statement porigin_site z poperand_body) :: ptask_body_tail*',
                   '$useriter_cursor_valid(S_body,n,n_object)']
        rejected(checks, 'next_future_id', 'S_body[.ITERATORS = [OBJECTITER n_high n_object 0 false]][.TODO = (USERITER_NEXT n_high n_object statement porigin_site z poperand_body) :: ptask_body_tail*]')
        previous = 'S_body'
    else:
        checks += seek('S', 'S_initial', 7) + valid('S', True)
        checks += ['S.TODO = (USERITER_RESULT n n_object statement porigin_site z "current" poperand) :: ptask_tail*',
                   '~$useriter_has_key(statement)']
        rejected(checks, 'value_only_key', 'S[.TODO = (USERITER_RESULT n n_object statement porigin_site z "key" poperand) :: ptask_tail*]')
        previous = 'S'
    checks += [f'S_done = $drive({previous}[.COMPLETION = NORMAL],4096)',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.ITERATORS = eps',
               '$iterator_test_outputs(S_done.EVENTS) = ' + source.driver.byte_expr(CASES[name][1])]
    checks += valid('S_done')
    if name == 'fatal':
        checks += ['S_done.COMPLETION = USERFATAL ($ptascii("fatal")) z_fatal true']
    else:
        checks += ['S_done.COMPLETION = NORMAL']
    if name == 'owners':
        checks += ['~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HOBJECT n_object) <- S_done.ALLOCATIONS)']
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['fixtures', 'prepare', 'check'], default='check')
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES)
    assert names and len(names) == len(set(names)) and all(n in CASES for n in names)
    out = Path(tempfile.mkdtemp(prefix='iterator-protocol-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'mode': args.mode, 'records': [], 'assertions': 0,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': source.driver.types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    print(out, flush=True)
    try:
        report['tools'] = source.provenance(out)
        report['runtime'] = source.runtime(out)
        for name in names:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name][0])
            native = source.process([str(source.driver.types.PHP), '-n', *source.driver.types.FLAGS, str(path)], directory / 'native', 10, directory)
            assert native.returncode == (255 if name == 'fatal' else 0) and native.stdout == CASES[name][1], (name, native.stdout, native.stderr)
            assert b'Fatal error: fatal' in native.stderr if name == 'fatal' else not native.stderr
            frontend = Worker([str(source.driver.types.PHP), '-n', *source.driver.types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': source.driver.b64(path.read_bytes())})
                assert parsed['accepted']
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            finally:
                frontend.close()
            checks = assertions(checked, path, directory, name)
            (directory / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $body() : bool\ndef $body() = true\n' +
                               ''.join('  -- if ' + c + '\n' for c in checks) +
                               '\ndec $main() : bool\ndef $main() = ' + ('true' if args.mode == 'prepare' else '$body()') + '\n')
            row = {'id': name, 'assertions': len(checks), 'evaluated': args.mode == 'check'}
            report['records'].append(row)
            if args.mode != 'fixtures':
                source.driver.numeric(fixture, directory)
            report['assertions'] += len(checks) if args.mode == 'check' else 0
            row['passed'] = True
            print(name, args.mode, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Check exception-handler default selection, real owners and closed history."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_parameter_default_protocol import PREFIX
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SELECTIONS = {'exception': ROOT / 'tests/semantics/deprecated_handler_method_default/exception-shadow-callback.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $api_review_ready(pstate,nat) : bool
def $api_review_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 1) :: eps
def $api_review_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 1) :: eps
def $api_review_ready(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: eps
def $api_review_ready(S,n) = false -- otherwise
dec $api_review_pause(pstate,nat,nat) : pstate
def $api_review_pause(S,n_mode,n) = S -- if $api_review_ready(S,n_mode)
def $api_review_pause(S,n_mode,n) = $api_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$api_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $api_review_pause(S,n_mode,n) = S -- otherwise
dec $api_review_output_item(pevent) : ptbytes
def $api_review_output_item(OUTPUT ptbytes) = ptbytes
def $api_review_output_item(pevent) = eps -- otherwise
dec $api_review_output(pevent*) : ptbytes
def $api_review_output(eps) = eps
def $api_review_output(pevent :: pevent_tail*) = $api_review_output_item(pevent) ++ $api_review_output(pevent_tail*)
'''


def exception(fixture, path):
    return [
        'U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_receive = $api_review_pause(S_start[.COMPLETION = NORMAL],0,20000)',
        '$api_review_ready(S_receive,0)',
        'S_receive.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer',
        '$receiving_function(S_receive,pcallcontext.FUNCTION) = (pfunction)',
        '$parameter_shutdown_target(S_receive,pshutdownproducer.TARGET) = ((pmethoddesc,porigin_requested,porigin_called,n_receiver?))',
        'n_receiver? = (n_receiver)',
        '$exception_context_call(S_receive,pcallcontext) = (pexceptioncall)',
        '$exception_context_valid(S_receive,pcallcontext)',
        '$error_context_receiving_function(S_receive,pcallcontext) = eps',
        'pcallcontext.CALLSITE = eps', 'pcallcontext.LINE = $(-1)', 'pcallcontext.ARGC = 1',
        'pshutdownproducer.SITE = (pfunction.ORIGIN)',
        'pshutdownproducer.INTERNAL', 'pshutdownproducer.SCOPE = eps',
        'pshutdownproducer.BINDING = eps', 'pshutdownproducer.CLONE = eps',
        '$target_nodes(pcallcontext.TARGET) = eps', '$call_context_roots(S_receive.CURRENT) = eps',
        '$heap_owners($heap_graph(S_receive),HOBJECT pexceptioncall.OBJECT) = 2',
        '$parameter_default_recipient(S_receive,pfunction)',
        '$default_at(pfunction.DEFAULTS,1) = (pdefault)',
        '$default_receive_recipient(S_receive,pfunction,pdefault)',
        'S_bad_arity = S_receive[.CURRENT = (pcallcontext[.ARGC = 2])]',
        '$parameter_api_handler_current(S_bad_arity,pfunction) = eps',
        '~$default_receive_recipient(S_bad_arity,pfunction,pdefault)',
        'S_zero = $drive_steps(S_receive,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_receive',
        'S_one = $drive_steps(S_receive,1)', 'S_one.COMPLETION = BUDGET',
        'S_begin = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_owner(S_begin.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_begin,n_receive) = (preceivebirth)',
        'preceivebirth.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer)',
        'preceivebirth.ACTIVE', 'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        '$parameter_receive_source_valid(S_begin,preceivebirth)',
        '$parameter_receive_cache_entry(S_begin,preceivebirth)',
        '~$parameter_receive_cache_entry(S_begin,preceivebirth[.API_ENTRY = eps])',
        '~$parameter_receive_api_witness_valid(S_begin,preceivebirth[.API_ENTRY = (ERROR_RECEIVE pshutdownproducer)])',
        '~$parameter_receive_api_witness_valid(S_begin,preceivebirth[.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer[.INTERNAL = false])])',
        '~$parameter_receive_api_witness_valid(S_begin,preceivebirth[.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer[.SITE = (preceivebirth.ORIGIN)])])',
        '~$parameter_receive_api_witness_valid(S_begin,preceivebirth[.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer[.TARGET = OUTPUT_BORROWED_TARGET pshutdownproducer.TARGET])])',
        '$machine_roots(S_begin[.PARAMETERRECEIVES = eps]) = $machine_roots(S_begin)',
        '$call_descriptors_valid(S_begin)',
        'S_bind = $api_review_pause(S_begin,1,20000)', '$api_review_ready(S_bind,1)',
        'S_bind.CURRENT = (pcallcontext_bind)',
        '$exception_context_valid(S_bind,pcallcontext_bind)',
        '$parameter_api_handler_current(S_bind,pfunction) = (pshutdownproducer)',
        '$heap_owners($heap_graph(S_bind),HOBJECT pexceptioncall.OBJECT) = 2',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 1',
        '$call_context_roots(S_bind.CURRENT) = eps',
        '$task_nodes(EXCEPTION_HANDLER_RESULT pexceptioncall) = [HOBJECT pexceptioncall.OBJECT]',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        '$default_bind_task_valid(S_bind,pfunction.ORIGIN,1)',
        '$call_descriptors_valid(S_bind)',
        'S_after_step = $drive_steps(S_bind,1)', 'S_after_step.COMPLETION = BUDGET',
        'S_after = S_after_step[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_after,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_owner(S_after.CURRENT) = eps',
        '$parameter_receive_cache_entry(S_after,preceivebirth_closed)',
        '$default_current_cache(S_after,pdefault.ORIGIN) = (pdefaultcache)',
        '$call_descriptors_valid(S_after)',
        'S_result = $api_review_pause(S_after,2,20000)', '$api_review_ready(S_result,2)',
        '$heap_owners($heap_graph(S_result),HOBJECT pexceptioncall.OBJECT) = 1',
        '$parameter_receive_cache_entry(S_result,preceivebirth_closed)',
        'S_done = $drive(S_result,30000)', 'S_done.COMPLETION = NORMAL',
        '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
        'S_history = S_done[.OBJECTS = eps][.EXCEPTIONHANDLER = eps][.EXCEPTIONHANDLERS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.API_ENTRY = eps])',
        '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_receive,30000) = S_done',
        '$api_review_output(S_done.EVENTS) = $base64("RnxIfEx8TXxFfDl8WnxSfA==")',
    ]


def prepare(out, group):
    path = SELECTIONS[group]
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = globals()[group](checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
            for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SELECTIONS[args.group], *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules),
        'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, args.group)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Check named handler default selection, type-cache order and Throwable owners."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_named_callback_default_review'
SELECTIONS = {'reject': SOURCE / 'error-type-cache.php',
    'exception': SOURCE / 'exception-shadow.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $named_callback_ready(pstate,nat) : bool
def $named_callback_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 1) :: eps
def $named_callback_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 1) :: eps
def $named_callback_ready(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: eps
def $named_callback_ready(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 4) :: eps
def $named_callback_ready(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 4) :: eps
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,4) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $named_callback_ready(S,n) = false -- otherwise
dec $named_callback_pause(pstate,nat,nat) : pstate
def $named_callback_pause(S,n_mode,n) = S -- if $named_callback_ready(S,n_mode)
def $named_callback_pause(S,n_mode,n) = $named_callback_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$named_callback_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $named_callback_pause(S,n_mode,n) = S -- otherwise
dec $named_callback_output_item(pevent) : ptbytes
def $named_callback_output_item(OUTPUT ptbytes) = ptbytes
def $named_callback_output_item(pevent) = eps -- otherwise
dec $named_callback_output(pevent*) : ptbytes
def $named_callback_output(eps) = eps
def $named_callback_output(pevent :: pevent_tail*) = $named_callback_output_item(pevent) ++ $named_callback_output(pevent_tail*)
'''


def start(fixture, path, mode):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_front = $named_callback_pause(S_start[.COMPLETION = NORMAL],' + str(mode) + ',20000)',
        '$named_callback_ready(S_front,' + str(mode) + ')',
        'S_front.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer',
        '$function_at(S_front.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction)',
        'pshutdownproducer.TARGET = pfunction.ORIGIN',
        'pcallcontext.NAME = pfunction.NAME',
        'pcallcontext.LEXICAL_CLASS = eps', 'pcallcontext.CALLED_CLASS = eps',
        'pcallcontext.RECEIVER = eps', 'pcallcontext.INSTANCE = eps',
        'pcallcontext.WRAPPER = eps', 'pcallcontext.CACHE = eps',
        '$default_cache_owner(S_front) = (CACHE_SHARED)',
        '$class_method_origin(S_front.CLASSES,pfunction.ORIGIN) = eps',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S_front.CURRENT) = eps',
        '$parameter_default_recipient(S_front,pfunction)']


def reject(fixture, path):
    return start(fixture, path, 3) + [
        '$error_context_receiving_function(S_front,pcallcontext) = (pfunction)',
        '$error_context_call(S_front,pcallcontext) = (perrorcall)',
        'pcallcontext.ARGC = 4', 'pcallcontext.CALLSITE = (perrorcall.SITE)',
        'pshutdownproducer.SITE = pcallcontext.CALLSITE',
        '$default_at(pfunction.DEFAULTS,4) = (pdefault)',
        '$default_receive_recipient(S_front,pfunction,pdefault)',
        '$parameter_named_api_current(S_front,pfunction) = (pshutdownproducer)',
        '$parameter_named_api_current(S_front[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (pfunction.ORIGIN)])],pfunction) = eps',
        '$parameter_receive_owner(S_front.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_front,n_receive) = (preceivebirth)',
        'preceivebirth.API_ENTRY = (ERROR_RECEIVE pshutdownproducer)',
        'preceivebirth.ACTIVE', 'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        '$parameter_receive_named_entry(S_front,preceivebirth)',
        '$parameter_receive_cache_entry(S_front,preceivebirth)',
        '~$parameter_receive_named_entry(S_front,preceivebirth[.API_ENTRY = eps])',
        '~$parameter_receive_cache_entry(S_front,preceivebirth[.API_ENTRY = eps])',
        '~$parameter_receive_api_witness_valid(S_front,preceivebirth[.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer)])',
        '~$parameter_receive_api_witness_valid(S_front,preceivebirth[.API_ENTRY = (ERROR_RECEIVE pshutdownproducer[.INTERNAL = false])])',
        '$machine_roots(S_front[.PARAMETERRECEIVES = eps]) = $machine_roots(S_front)',
        '$default_current_cache(S_front,pdefault.ORIGIN) = eps',
        'S_front.RESULT = KNOWN (PARRAY n_array)',
        '$typed_parameter_conversion(S_front,pfunction.SIGNATURE.PARAMETERS[4],PARRAY n_array) = TYPEREJECT',
        '$parameter_default_error_candidate(S_front,pfunction,4,PARRAY n_array)',
        '$call_descriptors_valid(S_front)',
        'PhpStep: S_front ~> S_reject',
        'S_reject.COMPLETION = THROWN "TypeError" preqbytes_reject z_reject',
        'S_reject.CONSTCONTEXT = eps',
        '$parameter_receive_birth(S_reject,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_reject,preceivebirth_closed)',
        '$lookup(S_reject.ENV,pfunction.SIGNATURE.PARAMETERS[4].NAME) = (n_formal)',
        'S_reject.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '(HCELL n_formal) <- $machine_roots(S_reject)',
        '$default_current_cache(S_reject,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        'S_step_raw = $drive_steps(S_front,1)', 'S_step_raw.COMPLETION = BUDGET',
        'S_step = S_step_raw[.COMPLETION = NORMAL]',
        'S_step.TODO = (THROW_SEARCH n_error) :: eps',
        '$heap_valid($heap_graph(S_step))', '$call_descriptors_valid(S_step)',
        'S_warm = $named_callback_pause(S_step,4,20000)',
        '$named_callback_ready(S_warm,4)', 'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.TARGET = API_BORROWED_TARGET pshutdownproducer_warm',
        'pshutdownproducer_warm.TARGET = pfunction.ORIGIN',
        'pshutdownproducer_warm.SITE =/= pshutdownproducer.SITE',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        'S_warm.PARAMETERRECEIVES = S_step.PARAMETERRECEIVES',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        'S_bad = S_warm[.CURRENT = (pcallcontext_warm[.TARGET = API_BORROWED_TARGET pshutdownproducer_warm[.INTERNAL = false]])]',
        '~$default_receive_recipient(S_bad,pfunction,pdefault)',
        'PhpStep: S_warm ~> S_warm_reject',
        'S_warm_reject.COMPLETION = THROWN "TypeError" preqbytes_warm z_warm',
        '$lookup(S_warm_reject.ENV,pfunction.SIGNATURE.PARAMETERS[4].NAME) = (n_formal_warm)',
        'S_warm_reject.STORE[n_formal_warm] = DEFINED (PARRAY n_array)',
        'S_warm_reject.PARAMETERRECEIVES = S_warm.PARAMETERRECEIVES',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$named_callback_output(S_done.EVENTS) = $ptascii("T|T|Z|")']


def exception(fixture, path):
    return start(fixture, path, 0) + [
        '$exception_context_call(S_front,pcallcontext) = (pexceptioncall)',
        '$exception_context_valid(S_front,pcallcontext)',
        'pcallcontext.ARGC = 1', 'pcallcontext.CALLSITE = eps',
        'pcallcontext.LINE = $(-1)', 'pshutdownproducer.SITE = (pfunction.ORIGIN)',
        '$default_at(pfunction.DEFAULTS,1) = (pdefault)',
        '$default_receive_recipient(S_front,pfunction,pdefault)',
        '$parameter_named_api_current(S_front,pfunction) = (pshutdownproducer)',
        '$heap_owners($heap_graph(S_front),HOBJECT pexceptioncall.OBJECT) = 2',
        'S_zero = $drive_steps(S_front,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_front',
        'S_one = $drive_steps(S_front,1)', 'S_one.COMPLETION = BUDGET',
        'S_begin = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_owner(S_begin.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_begin,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE',
        'preceivebirth.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer)',
        '$parameter_receive_named_entry(S_begin,preceivebirth)',
        '$parameter_receive_cache_entry(S_begin,preceivebirth)',
        '~$parameter_receive_named_entry(S_begin,preceivebirth[.API_ENTRY = eps])',
        '~$parameter_receive_api_witness_valid(S_begin,preceivebirth[.API_ENTRY = (ERROR_RECEIVE pshutdownproducer)])',
        '~$parameter_receive_api_witness_valid(S_begin,preceivebirth[.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer[.SITE = (preceivebirth.ORIGIN)])])',
        'S_bind = $named_callback_pause(S_begin,1,20000)',
        '$named_callback_ready(S_bind,1)', 'S_bind.CURRENT = (pcallcontext_bind)',
        '$exception_context_valid(S_bind,pcallcontext_bind)',
        '$exception_context_call(S_bind,pcallcontext_bind) = (pexceptioncall)',
        '$heap_owners($heap_graph(S_bind),HOBJECT pexceptioncall.OBJECT) = 2',
        '$call_context_roots(S_bind.CURRENT) = eps',
        'S_bind.EXCEPTIONHANDLER = (pvalue_replaced)',
        'pvalue_replaced =/= pexceptioncall.CALLBACK',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        '$constant_expression_root(S_bind,preceivebirth.ORIGIN) = (porigin_initializer)',
        '$parameter_receive_effect_value(S_bind,preceivebirth,porigin_initializer)',
        '~$parameter_receive_effect_value(S_bind[.RESULT = KNOWN (PINT 9)],preceivebirth,porigin_initializer)',
        '$default_bind_task_valid(S_bind,pfunction.ORIGIN,1)',
        '$call_descriptors_valid(S_bind)',
        'S_bound_raw = $drive_steps(S_bind,1)', 'S_bound_raw.COMPLETION = BUDGET',
        'S_bound = S_bound_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_bound,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_bound,preceivebirth_closed)',
        '$default_current_cache(S_bound,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        'S_result = $named_callback_pause(S_bound,2,20000)',
        '$named_callback_ready(S_result,2)',
        '$heap_owners($heap_graph(S_result),HOBJECT pexceptioncall.OBJECT) = 1',
        '$task_nodes(EXCEPTION_HANDLER_RESULT pexceptioncall) = [HOBJECT pexceptioncall.OBJECT]',
        '$parameter_receive_cache_entry(S_result,preceivebirth_closed)',
        'S_done = $drive(S_result,30000)', 'S_done.COMPLETION = NORMAL',
        '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
        'S_history = S_done[.OBJECTS = eps][.ARRAYS = eps][.EXCEPTIONHANDLER = eps][.EXCEPTIONHANDLERS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.PUBLICATION = 0])',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.API_ENTRY = eps])',
        '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_front,30000) = S_done',
        '$named_callback_output(S_done.EVENTS) = $ptascii("H|N|B|E|9|L|T|Z|")']


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

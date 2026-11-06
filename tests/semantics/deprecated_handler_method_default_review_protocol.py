#!/usr/bin/env python3
"""Check error-handler extra-default owners and cold/warm type rejection."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_constructor_default_review_protocol import PREFIX, EXTRA
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_handler_method_default_review'
SELECTIONS = {'ownership': SOURCE / 'error-owner-replacement.php',
    'reject': SOURCE / 'error-type-cache.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $handler_review_ready(pstate,nat) : bool
def $handler_review_ready(S,0) = true
  -- if S.TODO = (DEFAULT_BIND porigin 4) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if $parameter_receive_owner(S.CURRENT) = (n)
  -- if $parameter_receive_birth(S,n) = (preceivebirth)
  -- if preceivebirth.API_ENTRY = (ERROR_RECEIVE pshutdownproducer)
def $handler_review_ready(S,1) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 4) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,4) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $handler_review_ready(S,2) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 4) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,4) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $handler_review_ready(S,n_mode) = false -- otherwise
dec $handler_review_pause(pstate,nat,nat) : pstate
def $handler_review_pause(S,n_mode,n) = S -- if $handler_review_ready(S,n_mode)
def $handler_review_pause(S,n_mode,n) = $handler_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$handler_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $handler_review_pause(S,n_mode,n) = S -- otherwise
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_bind = $handler_review_pause(S_start[.COMPLETION = NORMAL],0,10000)',
        '$handler_review_ready(S_bind,0)',
        'S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$class_method_origin(S_bind.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        'pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer',
        '$parameter_api_handler_current(S_bind,pfunction) = (pshutdownproducer)',
        '$error_context_receiving_function(S_bind,pcallcontext) = (pfunction)',
        '$error_context_call(S_bind,pcallcontext) = (perrorcall)',
        'perrorcall.TARGET = (pcallcontext.TARGET)',
        'pcallcontext.ARGC = 4',
        'pcallcontext.CALLSITE = (perrorcall.SITE)',
        'pcallcontext.LINE = $error_callback_line(S_bind,perrorcall)',
        'pcallcontext.LINE =/= $default_parameter_line(S_bind,pfunction.ORIGIN,4)',
        'pshutdownproducer.SITE = pcallcontext.CALLSITE',
        'perrorcall.CALLBACK = PARRAY n_callback',
        'S_bind.ERRORHANDLER.CALLBACK = eps',
        'pcallcontext.RECEIVER = (n_receiver)',
        '$call_context_roots(S_bind.CURRENT) = eps',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE', 'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth.ENTRY = eps', 'preceivebirth.CONSTRUCTOR_ENTRY = eps',
        'preceivebirth.SHUTDOWN_ENTRY = eps',
        'preceivebirth.API_ENTRY = (ERROR_RECEIVE pshutdownproducer)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.API_ENTRY = eps])',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.API_ENTRY = (EXCEPTION_RECEIVE pshutdownproducer)])',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        '$default_at(pfunction.DEFAULTS,4) = (pdefault)',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        '$parameter_default_recipient(S_bind,pfunction)',
        '$default_receive_recipient(S_bind,pfunction,pdefault)',
        '~$parameter_method_ordinary_current(S_bind,pfunction)',
        'S_wrong_site = S_bind[.CURRENT = (pcallcontext[.TARGET = API_BORROWED_TARGET pshutdownproducer[.SITE = (pfunction.ORIGIN)]])]',
        '$parameter_api_handler_current(S_wrong_site,pfunction) = eps',
        '~$default_receive_recipient(S_wrong_site,pfunction,pdefault)',
        '$parameter_api_handler_current(S_bind[.CURRENT = (pcallcontext[.ARGC = 1])],pfunction) = eps',
        '$call_descriptors_valid(S_bind)']


def ownership(fixture, path):
    checks = start(fixture, path)
    checks += [
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 2',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        'preceivebirth_closed.API_ENTRY = (ERROR_RECEIVE pshutdownproducer)',
        '$default_cache_at(S_one.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        'S_warm = $handler_review_pause(S_one,1,10000)',
        '$handler_review_ready(S_warm,1)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.RECEIVER = (n_next)', 'n_next =/= n_receiver',
        '~((HOBJECT n_receiver) <- S_warm.ALLOCATIONS)',
        '~((HARRAY n_callback) <- S_warm.ALLOCATIONS)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$parameter_api_handler_current(S_warm,pfunction) = eps',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '$machine_roots(S_warm[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warm)',
        'S_history = S_warm[.OBJECTS = eps][.ARRAYS = eps][.ERRORHANDLER.CALLBACK = eps][.ERRORHANDLERS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.PUBLICATION = 0])',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.API_ENTRY = (ERROR_RECEIVE pshutdownproducer[.INTERNAL = false])])',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.API_ENTRY = (ERROR_RECEIVE pshutdownproducer[.TARGET = pfunction.ORIGIN])])',
        '$call_descriptors_valid(S_warm)',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("M|E|L|D|R|M|E|L|D|Z|")',
    ]
    return checks


def reject(fixture, path):
    checks = start(fixture, path)
    checks += [
        '$typed_parameter_conversion(S_bind,pfunction.SIGNATURE.PARAMETERS[4],PARRAY n_array) = TYPEREJECT',
        '$parameter_default_error_candidate(S_bind,pfunction,4,PARRAY n_array)',
        'PhpStep: S_bind ~> S_reject',
        'S_reject.COMPLETION = THROWN "TypeError" preqbytes_reject z_reject',
        'S_reject.CURRENT = (pcallcontext[.DEFAULTRECEIVE = eps])',
        'S_reject.CONSTCONTEXT = eps',
        '$parameter_receive_birth(S_reject,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$lookup(S_reject.ENV,pfunction.SIGNATURE.PARAMETERS[4].NAME) = (n_formal)',
        'S_reject.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '(HCELL n_formal) <- $machine_roots(S_reject)',
        '$default_cache_at(S_reject.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$parameter_receive_cache_entry(S_reject,preceivebirth_closed)',
        'S_wrapped = $throwable_transition(S_bind,S_reject)',
        'S_wrapped.COMPLETION = THROWING n_type_error',
        'S_wrapped.STORE[n_formal] = DEFINED (PARRAY n_array)',
        'S_throw_raw = $drive_steps(S_bind,1)', 'S_throw_raw.COMPLETION = BUDGET',
        'S_throw = S_throw_raw[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_SEARCH n_type_error) :: eps',
        '$heap_valid($heap_graph(S_throw))', '$call_descriptors_valid(S_throw)',
        'S_warm = $handler_review_pause(S_throw,2,10000)',
        '$handler_review_ready(S_warm,2)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.ARGC = 4',
        '$parameter_api_handler_current(S_warm,pfunction) = (pshutdownproducer_warm)',
        'pshutdownproducer_warm.SITE =/= pshutdownproducer.SITE',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        '$parameter_default_error_candidate(S_warm,pfunction,4,PARRAY n_array)',
        'S_wrong_selected = S_warm[.CURRENT = (pcallcontext_warm[.TARGET = API_BORROWED_TARGET pshutdownproducer])]',
        '$parameter_api_handler_current(S_wrong_selected,pfunction) = eps',
        '~$default_receive_recipient(S_wrong_selected,pfunction,pdefault)',
        'PhpStep: S_warm ~> S_warm_reject',
        'S_warm_reject.COMPLETION = THROWN "TypeError" preqbytes_warm z_warm',
        '$lookup(S_warm_reject.ENV,pfunction.SIGNATURE.PARAMETERS[4].NAME) = (n_formal_warm)',
        'S_warm_reject.STORE[n_formal_warm] = DEFINED (PARRAY n_array)',
        'S_warm_reject.PARAMETERRECEIVES = S_warm.PARAMETERRECEIVES',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("T|T|D|Z|")',
    ]
    return checks


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
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
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
        'tests/semantics/deprecated_constructor_default_review_protocol.py',
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

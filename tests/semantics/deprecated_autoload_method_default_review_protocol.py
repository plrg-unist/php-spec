#!/usr/bin/env python3
"""Check borrowed autoload receivers and cold/warm default rejection."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_autoload_method_default_review'
SELECTIONS = {'retirement': SOURCE / 'self-unregister.php',
    'reject': SOURCE / 'type-cache.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $auto_review_ready(pstate,nat) : bool
def $auto_review_ready(S,0) = true
  -- if S.TODO = (DEFAULT_BIND porigin 1) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) =/= eps
def $auto_review_ready(S,1) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 1) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = eps
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) =/= eps
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,1) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $auto_review_ready(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $destructor_method(S,n) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
  -- if $class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Loader204")
def $auto_review_ready(S,n) = false -- otherwise
dec $auto_review_pause(pstate,nat,nat) : pstate
def $auto_review_pause(S,n_mode,n) = S -- if $auto_review_ready(S,n_mode)
def $auto_review_pause(S,n_mode,n) = $auto_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$auto_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $auto_review_pause(S,n_mode,n) = S -- otherwise
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.CURRENT = (pcallcontext)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        'pcallcontext.ARGC = 1', 'pcallcontext.INSTANCE = eps',
        'pcallcontext.WRAPPER = eps', 'pcallcontext.CACHE = eps',
        'pcallcontext.RECEIVER = (n_receiver)',
        '$autoload_context_call(pcallcontext,S_warn.CURRENT,S_warn.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))',
        'pautoloadcall.MODE = AUTO_LOOKUP',
        'pcallcontext.CALLSITE = (pautoloadcall.SITE)',
        'pcallcontext.LINE = pautoloadcall.LINE',
        'poperand = KNOWN (PSTRING pautoloadcall.NAME)',
        'pautoloadentry.TARGET = AUTO_TARGET pcalltarget',
        'pcallcontext.TARGET = AUTOLOAD_BORROWED_TARGET pcalltarget',
        '$autoload_method_shape(pautoloadentry)',
        '~$autoload_context_target(pautoloadentry[.CALL.OWNER = (n_receiver)],pcallcontext.TARGET)',
        '~$autoload_context_target(pautoloadentry[.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_receiver))]][.RAW = eps],pcallcontext.TARGET)',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S_warn.CURRENT) = eps',
        '$parameter_default_recipient(S_warn,pfunction)',
        '$default_at(pfunction.DEFAULTS,1) = (pdefault)',
        '$default_receive_recipient(S_warn,pfunction,pdefault)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE', 'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth.ENTRY = eps', 'preceivebirth.CONSTRUCTOR_ENTRY = eps',
        'preceivebirth.SHUTDOWN_ENTRY = eps', 'preceivebirth.API_ENTRY = eps',
        '$declaration_autoload_at(preceivebirth.CAUSE.AUTOLOAD,0) = ((pautoloadcall,pautoloadentry))',
        '$parameter_receive_cache_entry(S_warn,preceivebirth)',
        '$machine_roots(S_warn[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warn)',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_receiver) = 2',
        '$call_descriptors_valid(S_warn)']


def retirement(fixture, path):
    checks = start(fixture, path)
    checks += [
        'S_destructor = $auto_review_pause(S_warn,2,10000)',
        '$auto_review_ready(S_destructor,2)',
        'S_destructor.CURRENT = (pcallcontext_destructor)',
        'pcallcontext_destructor.RECEIVER = (n_receiver)',
        '(HOBJECT n_receiver) <- S_destructor.ALLOCATIONS',
        'S_destructor.DEFAULTCACHE = eps',
        'S_bind = $auto_review_pause(S_destructor,0,10000)',
        '$auto_review_ready(S_bind,0)',
        'S_bind.CURRENT = (pcallcontext_bind)',
        'pcallcontext_bind.TARGET = pcallcontext.TARGET',
        'pcallcontext_bind.RECEIVER = (n_receiver)',
        '~((HOBJECT n_receiver) <- S_bind.ALLOCATIONS)',
        '$ctor_review_output(S_bind.EVENTS) = $ptascii("H|D|W|")',
        '$target_function(S_bind,pcallcontext_bind.TARGET) = (pfunction)',
        '$autoload_context_valid(S_bind,pcallcontext_bind)',
        '$executor_boundary(S_bind) = eps',
        '$executor_boundary(S_bind[.TODO = [NAME_READ pcallcontext_bind.LINE]]) = ("retired autoload receiver access")',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        '$call_context_roots(S_bind.CURRENT) = eps',
        'S_wrong_current = S_bind[.CURRENT = (pcallcontext_bind[.TARGET = pcalltarget])]',
        '~$default_receive_recipient(S_wrong_current,pfunction,pdefault)',
        '$heap_valid($heap_graph(S_bind))', '$call_descriptors_valid(S_bind)',
        'S_zero = $drive(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'S_one_raw = $drive(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$default_cache_at(S_one.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$lookup(S_one.ENV,pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_formal)',
        'S_one.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '$call_descriptors_valid(S_one)',
        'S_done = $drive(S_bind,20000)', 'S_done.COMPLETION = NORMAL',
        '$drive(S_one,20000) = S_done',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("H|D|W|B|E|Z|")',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        'S_erased = S_done[.OBJECTS = eps][.ARRAYS = eps][.AUTOLOAD.ENTRIES = eps][.AUTOLOAD.BIRTHS = eps]',
        '$parameter_receive_cache_entry(S_erased,preceivebirth_closed)',
        'pautoloadentry_option? = (pautoloadentry)',
        'S_poison_registry = S_erased[.AUTOLOAD.ENTRIES = [pautoloadentry_option?]][.AUTOLOAD.BIRTHS = eps]',
        '$parameter_receive_cache_entry(S_poison_registry,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_erased,preceivebirth_closed[.PUBLICATION = 0])',
        '~$parameter_receive_cache_entry(S_erased,preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.AUTOLOAD = eps]])',
        'preceivebirth_wrong_index = preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.AUTOLOAD = [(1,pautoloadcall,pautoloadentry)]]]',
        '~$parameter_receive_cache_entry(S_erased,preceivebirth_wrong_index)',
        'preceivebirth_wrong_key = preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.AUTOLOAD = [(0,pautoloadcall[.KEY = eps],pautoloadentry)]]]',
        '~$parameter_receive_cache_entry(S_erased,preceivebirth_wrong_key)',
        'preceivebirth_wrong_target = preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.AUTOLOAD = [(0,pautoloadcall,pautoloadentry[.TARGET = AUTO_TARGET pfunction.ORIGIN])]]]',
        '~$parameter_receive_cache_entry(S_erased,preceivebirth_wrong_target)',
    ]
    return checks


def reject(fixture, path):
    checks = start(fixture, path)
    checks += [
        'S_bind = $auto_review_pause(S_warn,0,10000)',
        '$auto_review_ready(S_bind,0)', 'S_bind.CURRENT = (pcallcontext_bind)',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = eps',
        '$typed_parameter_conversion(S_bind,pfunction.SIGNATURE.PARAMETERS[1],PARRAY n_array) = TYPEREJECT',
        '$parameter_default_error_candidate(S_bind,pfunction,1,PARRAY n_array)',
        'PhpStep: S_bind ~> S_reject',
        'S_reject.COMPLETION = THROWN "TypeError" preqbytes_reject z_reject',
        '$parameter_receive_birth(S_reject,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$default_cache_at(S_reject.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$lookup(S_reject.ENV,pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_formal)',
        'S_reject.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '$parameter_receive_cache_entry(S_reject,preceivebirth_closed)',
        'S_throw_raw = $drive_steps(S_bind,1)', 'S_throw_raw.COMPLETION = BUDGET',
        'S_throw = S_throw_raw[.COMPLETION = NORMAL]',
        'S_warm = $auto_review_pause(S_throw,1,10000)',
        '$auto_review_ready(S_warm,1)', 'S_warm.CURRENT = (pcallcontext_warm)',
        '$autoload_context_call(pcallcontext_warm,S_warm.CURRENT,S_warm.FRAMES) = ((pautoloadcall_warm,pautoloadentry,poperand_warm))',
        'pautoloadcall_warm.MODE = AUTO_EXPLICIT pconfigcall',
        'pcallcontext_warm.CALLSITE = eps', 'pcallcontext_warm.LINE = $(-1)',
        'pcallcontext_warm.ARGC = 1', 'pcallcontext_warm.RECEIVER = (n_receiver)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        '$target_nodes(pcallcontext_warm.TARGET) = eps',
        '$call_context_roots(S_warm.CURRENT) = eps',
        '$default_cache_owner(S_warm) = (CACHE_SHARED)',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        '$parameter_default_error_candidate(S_warm,pfunction,1,PARRAY n_array)',
        '$call_descriptors_valid(S_warm)',
        'PhpStep: S_warm ~> S_warm_reject',
        'S_warm_reject.COMPLETION = THROWN "TypeError" preqbytes_warm z_warm',
        'S_warm_reject.PARAMETERRECEIVES = S_warm.PARAMETERRECEIVES',
        '$lookup(S_warm_reject.ENV,pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_formal_warm)',
        'S_warm_reject.STORE[n_formal_warm] = DEFINED (PARRAY n_array)',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("H|T|T|D|Z|")',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
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
        'tests/semantics/profile.json',
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

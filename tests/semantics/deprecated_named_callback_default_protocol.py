#!/usr/bin/env python3
"""Check named autoload, shutdown and pending direct-child default authority."""
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
SELECTIONS = {name: ROOT / 'tests/semantics/deprecated_named_callback_default' / source for name,source in [('autoload','autoload-direct.php'),('reentry','tick-direct-reentry.php'),('shutdown','cold-shutdown.php')]}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTED = r'''
dec $named_probe_ready(pstate,nat) : bool
def $named_probe_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $parameter_named_autoload_current(S,pfunction)
  -- if S.TODO = (DEFAULT_BIND pfunction.ORIGIN 1) :: eps
def $named_probe_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))
  -- if pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 1) :: eps
def $named_probe_ready(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $parameter_receive_owner(S.CURRENT) = (n_receive)
  -- if $parameter_receive_birth(S,n_receive) = (preceivebirth)
  -- if preceivebirth.PARENT =/= eps /\ preceivebirth.TICK_ENTRY = eps
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $named_probe_ready(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $parameter_receive_owner(S.CURRENT) = (n_receive)
  -- if $parameter_receive_birth(S,n_receive) = (preceivebirth)
  -- if preceivebirth.TICK_ENTRY =/= eps
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $named_probe_ready(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $parameter_named_shutdown_current(S,pfunction) = (pshutdownreceive)
  -- if pshutdownreceive.INDEX = 0
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $named_probe_ready(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.SHUTDOWN.INDEX = 1
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
def $named_probe_ready(S,n) = false -- otherwise
dec $named_probe_pause(pstate,nat,nat) : pstate
def $named_probe_pause(S,n_mode,n) = S -- if $named_probe_ready(S,n_mode)
def $named_probe_pause(S,n_mode,n) = $named_probe_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$named_probe_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $named_probe_pause(S,n_mode,n) = S -- otherwise
dec $named_probe_output_item(pevent) : ptbytes
def $named_probe_output_item(OUTPUT ptbytes) = ptbytes
def $named_probe_output_item(pevent) = eps -- otherwise
dec $named_probe_output(pevent*) : ptbytes
def $named_probe_output(eps) = eps
def $named_probe_output(pevent :: pevent_tail*) = $named_probe_output_item(pevent) ++ $named_probe_output(pevent_tail*)
'''


def begin(fixture,path,mode):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET',f'S_bind = $named_probe_pause(S_start[.COMPLETION = NORMAL],{mode},20000)',
        f'$named_probe_ready(S_bind,{mode})','S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$parameter_named_callback_source(S_bind,pfunction)',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        '$parameter_receive_source_valid(S_bind,preceivebirth)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        r'pcallcontext.LEXICAL_CLASS = eps /\ pcallcontext.CALLED_CLASS = eps /\ pcallcontext.RECEIVER = eps',
        '$default_cache_owner(S_bind) = (CACHE_SHARED)',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        '$call_descriptors_valid(S_bind)']


def finish(path):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive(S_warm,30000)','S_done.COMPLETION = NORMAL',
        '$named_probe_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')']


def autoload(fixture,path):
    return begin(fixture,path,0)+[
        '$parameter_named_autoload_current(S_bind,pfunction)',
        'pcallcontext.TARGET = pfunction.ORIGIN', 'pcallcontext.ARGC = 1',
        '$declaration_autoload_at(preceivebirth.CAUSE.AUTOLOAD,0) = ((pautoloadcall,pautoloadentry))',
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadentry.TARGET = AUTO_TARGET pfunction.ORIGIN',
        'preceivebirth.CALLSITE = (pautoloadcall.SITE)',
        r'preceivebirth.API_ENTRY = eps /\ preceivebirth.TICK_ENTRY = eps /\ preceivebirth.SHUTDOWN_ENTRY = eps',
        '$user_constant_at(S_bind.USERCONSTANTS,$user_constant_key($ptascii("Ns206Auto\\\\X"))) = (puserconstant)',
        'puserconstant.RECEIVES = [preceivecut]', '$parameter_receive_cut_source(S_bind,preceivecut)',
        'preceivecut.CAUSE.AUTOLOAD = $parameter_autoload_shift(preceivebirth.CAUSE.AUTOLOAD,1)',
        '~$parameter_receive_cut_source(S_bind,preceivecut[.CAUSE = preceivecut.CAUSE[.AUTOLOAD = eps]])',
        '~$parameter_receive_cut_source(S_bind,preceivecut[.CAUSE = preceivecut.CAUSE[.AUTOLOAD = preceivebirth.CAUSE.AUTOLOAD]])',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.CAUSE = preceivebirth.CAUSE[.AUTOLOAD = eps]])',
        '~$parameter_named_birth(S_bind,preceivebirth[.PUBLICATION = 0],pfunction.ORIGIN)',
        '$parameter_named_callback_target(S_bind,CALLBACK_BORROWED_TARGET pfunction.ORIGIN) = eps',
        'S_one = $drive_steps(S_bind,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_after,n_receive) = (preceivebirth_closed)', '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_after,preceivebirth_closed)',
        'S_warm = $named_probe_pause(S_after,1,20000)', '$named_probe_ready(S_warm,1)',
        'S_warm.CURRENT = (pcallcontext_warm)', 'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        r'pcallcontext_warm.CALLSITE = eps /\ pcallcontext_warm.LINE = $(-1)',
        '$parameter_named_autoload_current(S_warm,pfunction)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_at(pfunction.DEFAULTS,1) = (pdefault)',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_cache','S_warm.ARRAYS[n_cache].ITEMS = eps',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        'S_history = S_warm[.AUTOLOAD.ENTRIES = eps][.AUTOLOAD.BIRTHS = eps][.ARRAYS = eps][.OBJECTS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '$call_descriptors_valid(S_warm)',
    ]+finish(path)+['S_done.PARAMETERSEQ = S_warm.PARAMETERSEQ',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)']


def reentry(fixture,path):
    return begin(fixture,path,2)+[
        'preceivebirth.PARENT = (n_parent)',
        '$parameter_receive_birth(S_bind,n_parent) = (preceivebirth_parent)',
        'preceivebirth_parent.TICK_ENTRY = (ptickreceive)',
        'ptickreceive.TARGET = pfunction.ORIGIN',
        'preceivebirth_parent.FUNCTION = preceivebirth.FUNCTION',
        'preceivebirth_parent.ORIGIN = preceivebirth.ORIGIN',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_parent)',
        '$parameter_receive_child_entry(S_bind,preceivebirth_parent,preceivebirth)',
        'preceivebirth.CAUSE.CALLS = (preceivebirth.FUNCTION,porigin_site_option?,eps,eps) :: pdeclcalls',
        'preceivebirth_bad = preceivebirth[.CAUSE = preceivebirth.CAUSE[.CALLS = (preceivebirth.FUNCTION,porigin_site_option?,(pfunction.ORIGIN),eps) :: pdeclcalls]]',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_bad)',
        '~$parameter_receive_child_entry(S_bind,preceivebirth_parent,preceivebirth_bad)',
        'preceivebirth_bad_called = preceivebirth[.CAUSE = preceivebirth.CAUSE[.CALLS = (preceivebirth.FUNCTION,porigin_site_option?,eps,(pfunction.ORIGIN)) :: pdeclcalls]]',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_bad_called)',
        '~$parameter_receive_child_entry(S_bind,preceivebirth_parent,preceivebirth_bad_called)',
        'S_child_one = $drive_steps(S_bind,1)','S_child_one.COMPLETION = BUDGET',
        'S_child_after = S_child_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_child_after,n_receive) = (preceivebirth_child_closed)',
        '~preceivebirth_child_closed.ACTIVE',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_current_cache(S_child_after,pdefault.ORIGIN) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PINT 9',
        'S_warm = $named_probe_pause(S_child_after,3,20000)', '$named_probe_ready(S_warm,3)',
        '$parameter_receive_birth(S_warm,n_parent) = (preceivebirth_parent_current)',
        'preceivebirth_parent_current = preceivebirth_parent',
        '$parameter_receive_cache_child(S_warm,preceivebirth_parent,n_parent,preceivebirth_child_closed)',
        '$default_cache_birth_valid(S_warm,preceivebirth_parent)',
        '$default_bind_task_valid(S_warm,pfunction.ORIGIN,0)',
        '$call_descriptors_valid(S_warm)',
    ]+finish(path)+[
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache_parent)',
        'pdefaultcache_parent.VALUE = PARRAY n_array', 'S_done.ARRAYS[n_array].ITEMS = eps',
        '$parameter_receive_cache_entry(S_done,preceivebirth_child_closed)',
        '$parameter_receive_birth(S_done,n_parent) = (preceivebirth_parent_closed)',
        '~preceivebirth_parent_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_done,preceivebirth_parent_closed)',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
    ]


def shutdown(fixture,path):
    return begin(fixture,path,4)+[
        '$parameter_named_shutdown_current(S_bind,pfunction) = (pshutdownreceive)',
        'preceivebirth.SHUTDOWN_ENTRY = (pshutdownreceive)',
        'pshutdownreceive.INDEX = 0', 'pshutdownreceive.TARGET = pfunction.ORIGIN',
        r'pcallcontext.CALLSITE = eps /\ pcallcontext.LINE = $(-1) /\ pcallcontext.ARGC = 0',
        'preceivebirth.CAUSE.CALLS = [(pfunction.ORIGIN,eps,eps,eps)]',
        '$call_context_roots(S_bind.CURRENT) = eps',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.SHUTDOWN_ENTRY = eps])',
        '~$parameter_receive_shutdown_witness_valid(S_bind,preceivebirth[.SHUTDOWN_ENTRY = (pshutdownreceive[.TARGET = CALLBACK_BORROWED_TARGET pfunction.ORIGIN])])',
        '~$parameter_receive_shutdown_witness_valid(S_bind,preceivebirth[.PUBLICATION = 0])',
        'S_one = $drive_steps(S_bind,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_after,n_receive) = (preceivebirth_closed)', '~preceivebirth_closed.ACTIVE',
        'S_warm = $named_probe_pause(S_after,5,20000)', '$named_probe_ready(S_warm,5)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        '$parameter_named_shutdown_current(S_warm,pfunction) = (pshutdownreceive_warm)',
        'pshutdownreceive_warm.INDEX = 1', 'pshutdownreceive_warm.TARGET = pfunction.ORIGIN',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array','S_warm.ARRAYS[n_array].ITEMS = eps',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        'S_history = S_warm[.SHUTDOWN.ENTRIES = eps][.SHUTDOWN.INDEX = 0][.ARRAYS = eps][.OBJECTS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '$call_descriptors_valid(S_warm)',
    ]+finish(path)+['S_done.PARAMETERSEQ = S_warm.PARAMETERSEQ',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)']


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
    paths = [Path(__file__), SELECTIONS[args.group], SELECTIONS[args.group].parent / 'cases.json', *modules, *(ROOT / path for path in (
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

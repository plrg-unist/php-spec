#!/usr/bin/env python3
"""Check raw callable CV instance ownership and same-site function cache identity."""
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
SELECTIONS = {name: ROOT / 'tests/semantics/deprecated_raw_callable_default' / source for name,source in [('instance','instance-before-arguments.php'),('reentry','same-site-functions.php'),('fcc','raw-parent-fcc-child.php')]}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTED = r'''
dec $raw_probe_ready(pstate,nat) : bool
def $raw_probe_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = ARRAY_METHOD_TARGET pcalltarget parrayselection
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 1) :: eps
def $raw_probe_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if S.TODO = (DEFAULT_RECEIVE porigin 1) :: eps
def $raw_probe_ready(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if $ptlc(pmethoddesc.NAME) = $ptascii("second")
  -- if $default_at(pmethoddesc.FUNCTION.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) = eps
def $raw_probe_ready(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if $ptlc(pmethoddesc.NAME) = $ptascii("first")
def $raw_probe_ready(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $raw_probe_ready(S,n) = false -- otherwise
dec $raw_probe_pause(pstate,nat,nat) : pstate
def $raw_probe_pause(S,n_mode,n) = S -- if $raw_probe_ready(S,n_mode)
def $raw_probe_pause(S,n_mode,n) = $raw_probe_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$raw_probe_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $raw_probe_pause(S,n_mode,n) = S -- otherwise
dec $raw_probe_output_item(pevent) : ptbytes
def $raw_probe_output_item(OUTPUT ptbytes) = ptbytes
def $raw_probe_output_item(pevent) = eps -- otherwise
dec $raw_probe_output(pevent*) : ptbytes
def $raw_probe_output(eps) = eps
def $raw_probe_output(pevent :: pevent_tail*) = $raw_probe_output_item(pevent) ++ $raw_probe_output(pevent_tail*)
'''


def begin(fixture,path,mode):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET',f'S_bind = $raw_probe_pause(S_start[.COMPLETION = NORMAL],{mode},20000)',
        f'$raw_probe_ready(S_bind,{mode})','S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$parameter_raw_callable_current(S_bind,pfunction)',
        '$class_method_origin(S_bind.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
        'pcallcontext.CALLSITE = (porigin_site)', '$parameter_raw_callable_site(S_bind,porigin_site)',
        '$call_selected_valid(S_bind,pcallcontext.TARGET,(porigin_site))',
        '$default_cache_owner(S_bind) = (CACHE_SHARED)']


def finish(path):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive(S_warm,30000)','S_done.COMPLETION = NORMAL',
        '$raw_probe_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')']


def instance(fixture,path):
    return begin(fixture,path,0)+[
        'pcallcontext.TARGET = ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver pfunction.ORIGIN) parrayselection',
        'pcallcontext.RECEIVER = (n_receiver)',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        'preceivebirth.ENTRY = eps', 'preceivebirth.RAW_ENTRY',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.RAW_ENTRY = false])',
        'S_bind.GLOBALTABLE = (psymboltable)',
        '$lookup(psymboltable.ENV,$ptascii("callback")) = (n_callback)',
        '$lookup(psymboltable.ENV,$ptascii("receiver")) = (n_global_receiver)',
        'S_bind.STORE[n_callback] = DEFINED PNULL',
        'S_bind.STORE[n_global_receiver] = DEFINED PNULL',
        '(HOBJECT n_receiver) <- S_bind.ALLOCATIONS',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 1',
        '$parameter_default_recipient(S_bind,pfunction)',
        '$call_descriptors_valid(S_bind)',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        'S_wrong = S_bind[.CURRENT = (pcallcontext[.TARGET = METHOD_TARGET n_receiver pfunction.ORIGIN])]',
        '~$parameter_raw_callable_current(S_wrong,pfunction)',
        '~$parameter_method_current_valid(S_wrong,pfunction)',
        'S_wrong_wrapper = S_bind[.CURRENT = (pcallcontext[.TARGET = ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver pfunction.ORIGIN) parrayselection[.SITE = pfunction.ORIGIN]])]',
        '~$parameter_raw_callable_current(S_wrong_wrapper,pfunction)',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.PUBLICATION = 0])',
        'S_one = $drive_steps(S_bind,1)','S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_after,n_receive) = (preceivebirth_closed)','~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_after,preceivebirth_closed)',
        'S_warm = $raw_probe_pause(S_after,1,20000)','$raw_probe_ready(S_warm,1)',
        '~((HOBJECT n_receiver) <- S_warm.ALLOCATIONS)',
        'S_warm.CURRENT = (pcallcontext_warm)','pcallcontext_warm.RECEIVER = (n_next)','n_next =/= n_receiver',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$parameter_default_recipient(S_warm,pfunction)',
        '~$parameter_raw_callable_current(S_warm,pfunction)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        'n_after = $(n_receiver + 1)', 'n_tail = $nabs($(|S_warm.OBJECTS| - n_after))',
        'S_poison = S_warm[.OBJECTS = S_warm.OBJECTS[0:n_receiver] ++ [STDINSTANCE] ++ S_warm.OBJECTS[n_after:n_tail]][.STORE = $set_cell(S_warm.STORE,n_callback,UNDEFINED)]',
        '$parameter_receive_cache_entry(S_poison,preceivebirth_closed)',
        '$machine_roots(S_warm[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warm)',
        '$call_descriptors_valid(S_warm)',
    ]+finish(path)


def reentry(fixture,path):
    return begin(fixture,path,2)+[
        'pcallcontext.TARGET = ARRAY_METHOD_TARGET pcalltarget parrayselection',
        '$parameter_receive_parent(S_bind.FRAMES) = (n_parent)',
        '$parameter_receive_birth(S_bind,n_parent) = (preceivebirth_parent)',
        '$class_method_origin(S_bind.CLASSES,preceivebirth_parent.FUNCTION) = (pmethoddesc_parent)',
        'pmethoddesc_parent.FUNCTION.ORIGIN =/= pfunction.ORIGIN',
        'pmethoddesc_parent.OWNER = pmethoddesc.OWNER',
        'preceivebirth_parent.CALLSITE = (porigin_site)',
        'preceivebirth_parent.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth_parent.RAW_ENTRY',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_parent[.RAW_ENTRY = false])',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_parent)',
        '$default_at(pmethoddesc_parent.FUNCTION.DEFAULTS,0) = (pdefault_parent)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault_child)',
        'pdefault_parent.ORIGIN =/= pdefault_child.ORIGIN',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault_parent.ORIGIN) = eps',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault_child.ORIGIN) = eps',
        '$call_descriptors_valid(S_bind)',
        'S_warm = $raw_probe_pause(S_bind,3,20000)','$raw_probe_ready(S_warm,3)',
        '$parameter_receive_birth(S_warm,n_parent) = (preceivebirth_parent_current)',
        'preceivebirth_parent_current = preceivebirth_parent',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault_child.ORIGIN) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PINT 9',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault_parent.ORIGIN) = eps',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_parent)',
        '~$parameter_receive_cache_child(S_warm,preceivebirth_parent,n_parent,preceivebirth_parent[.FUNCTION = pfunction.ORIGIN][.ORIGIN = $default_parameter_origin(S_warm,pfunction.ORIGIN,0)])',
        'S_warm.CURRENT = (pcallcontext_parent)',
        'pcallcontext_parent.FUNCTION = pmethoddesc_parent.FUNCTION.ORIGIN',
        '~$parameter_raw_callable_current(S_warm[.CURRENT = (pcallcontext_parent[.FUNCTION = pfunction.ORIGIN])],pfunction)',
        '$default_bind_task_valid(S_warm,pmethoddesc_parent.FUNCTION.ORIGIN,0)',
        '$call_descriptors_valid(S_warm)',
    ]+finish(path)+[
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault_child.ORIGIN) = (pdefaultcache_child)',
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault_parent.ORIGIN) = (pdefaultcache_parent)',
        'pdefaultcache_parent.VALUE = PARRAY n_parent_array','S_done.ARRAYS[n_parent_array].ITEMS = eps',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
    ]


def fcc(fixture,path):
    return ['U = '+fixture,
        'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET',
        'S_bind = $raw_probe_pause(S_start[.COMPLETION = NORMAL],4,20000)',
        '$raw_probe_ready(S_bind,4)',
        'S_bind.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_fcc',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$method_fcc_current(S_bind,pfunction)',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth_child)',
        'preceivebirth_child.ENTRY = (n_fcc)', '~preceivebirth_child.RAW_ENTRY',
        'preceivebirth_child.PARENT = (n_parent)',
        '$parameter_receive_birth(S_bind,n_parent) = (preceivebirth_parent)',
        'preceivebirth_parent.RAW_ENTRY', 'preceivebirth_parent.ENTRY = eps',
        'preceivebirth_parent.FUNCTION = pfunction.ORIGIN',
        'preceivebirth_parent.ORIGIN = preceivebirth_child.ORIGIN',
        'preceivebirth_parent.CALLSITE = preceivebirth_child.CALLSITE',
        'preceivebirth_parent.CACHE_OWNER = preceivebirth_child.CACHE_OWNER',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_parent)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_child)',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_child[.ENTRY = eps])',
        '~$parameter_raw_callable_current(S_bind,pfunction)',
        '~$parameter_method_current_valid(S_bind,pfunction)',
        '$parameter_default_recipient(S_bind,pfunction)',
        '$call_descriptors_valid(S_bind)',
        'S_one = $drive_steps(S_bind,1)', 'S_one.COMPLETION = BUDGET',
        'S_warm = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_warm,n_receive) = (preceivebirth_child_closed)',
        '~preceivebirth_child_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_child_closed)',
        '$parameter_receive_cache_child(S_warm,preceivebirth_parent,n_parent,preceivebirth_child_closed)',
        '~$parameter_receive_cache_entry(S_warm,preceivebirth_child_closed[.ENTRY = eps])',
        '~$parameter_receive_child_entry(S_warm,preceivebirth_parent,preceivebirth_child_closed[.ENTRY = eps])',
        '~$parameter_receive_cache_child(S_warm,preceivebirth_parent,n_parent,preceivebirth_child_closed[.ENTRY = eps])',
        '$machine_roots(S_warm[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warm)',
    ]+finish(path)+[
        '$parameter_receive_birth(S_done,n_parent) = (preceivebirth_parent_closed)',
        '~preceivebirth_parent_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_done,preceivebirth_parent_closed)',
        '~$parameter_receive_cache_entry(S_done,preceivebirth_parent_closed[.RAW_ENTRY = false])',
        '$parameter_receive_cache_entry(S_done,preceivebirth_child_closed)',
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

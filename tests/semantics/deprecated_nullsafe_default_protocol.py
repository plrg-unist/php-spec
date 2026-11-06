#!/usr/bin/env python3
"""Check nullsafe short circuiting, live ownership and inherited default caches."""
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
SELECTIONS = {name: ROOT / 'tests/semantics/deprecated_nullsafe_default' / source for name,source in [('instance','null-live-instance.php'),('reentry','same-site-inheritance.php')]}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTED = r'''
dec $ns_output_item(pevent) : ptbytes
def $ns_output_item(OUTPUT ptbytes) = ptbytes
def $ns_output_item(pevent) = eps -- otherwise
dec $ns_output(pevent*) : ptbytes
def $ns_output(eps) = eps
def $ns_output(pevent :: pevent_tail*) = $ns_output_item(pevent) ++ $ns_output(pevent_tail*)
dec $ns_ready(pstate,nat) : bool
def $ns_ready(S,0) = true
  -- if $ns_output(S.EVENTS) = $ptascii("N|")
  -- if S.CURRENT = eps
def $ns_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $parameter_nullsafe_site(S,porigin_site)
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 1) :: eps
def $ns_ready(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if ~$parameter_nullsafe_site(S,porigin_site)
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 1) :: eps
def $ns_ready(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $parameter_nullsafe_site(S,porigin_site)
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $ns_ready(S,n) = false -- otherwise
dec $ns_pause(pstate,nat,nat) : pstate
def $ns_pause(S,n_mode,n) = S -- if $ns_ready(S,n_mode)
def $ns_pause(S,n_mode,n) = $ns_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$ns_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $ns_pause(S,n_mode,n) = S -- otherwise
'''


def start(fixture,path):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET']


def finish(path):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive(S_warm,30000)','S_done.COMPLETION = NORMAL',
        '$ns_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')']


def instance(fixture,path):
    return start(fixture,path)+[
        'S_nil = $ns_pause(S_start[.COMPLETION = NORMAL],0,20000)','$ns_ready(S_nil,0)',
        'S_nil.PARAMETERSEQ = 0','S_nil.PARAMETERRECEIVES = eps','S_nil.DEFAULTCACHE = eps',
        '$lookup(S_nil.ENV,$ptascii("receiver")) = (n_receiver_cell)',
        'S_nil.STORE[n_receiver_cell] = DEFINED PNULL',
        'S_bind = $ns_pause(S_nil,1,20000)','$ns_ready(S_bind,1)',
        '$ns_output(S_bind.EVENTS) = $ptascii("N|A|H|")',
        'S_bind.CURRENT = (pcallcontext)','$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        'pcallcontext.TARGET = METHOD_TARGET n_receiver pfunction.ORIGIN','pcallcontext.RECEIVER = (n_receiver)',
        '$parameter_method_source(S_bind,pfunction) = (pmethoddesc)',
        '$parameter_nullsafe_current(S_bind,pfunction)','$parameter_default_recipient(S_bind,pfunction)',
        '$method_call_selected(S_bind,pcallcontext.TARGET,pcallcontext.CALLSITE)',
        'S_bind.STORE[n_receiver_cell] = DEFINED PNULL','(HOBJECT n_receiver) <- S_bind.ALLOCATIONS',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 1',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE','~preceivebirth.RAW_ENTRY','preceivebirth.ENTRY = eps',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)','$parameter_receive_source_valid(S_bind,preceivebirth)',
        '$default_at(pfunction.DEFAULTS,1) = (pdefault)','$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = eps',
        '$call_descriptors_valid(S_bind)',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        'S_wrong = S_bind[.CURRENT = (pcallcontext[.TARGET = STATIC_METHOD_TARGET pmethoddesc.OWNER pfunction.ORIGIN])]',
        '~$parameter_nullsafe_current(S_wrong,pfunction)',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.PUBLICATION = 0])',
        'S_one = $drive_steps(S_bind,1)','S_one.COMPLETION = BUDGET','S_after = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_after,n_receive) = (preceivebirth_closed)','~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_after,preceivebirth_closed)',
        'S_warm = $ns_pause(S_after,2,20000)','$ns_ready(S_warm,2)',
        '~((HOBJECT n_receiver) <- S_warm.ALLOCATIONS)','S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN','pcallcontext_warm.RECEIVER = (n_warm)','n_warm =/= n_receiver',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array','S_warm.ARRAYS[n_array].ITEMS = eps',
        '$parameter_receive_owner(S_warm.CURRENT) = eps','$parameter_default_recipient(S_warm,pfunction)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        'S_erased = S_warm[.GLOBALTABLE = eps][.STORE = eps][.OBJECTS = eps][.ARRAYS = eps][.ALLOCATIONS = eps]',
        '$parameter_receive_cache_entry(S_erased,preceivebirth_closed)',
        '$call_descriptors_valid(S_warm)',
    ]+finish(path)


def reentry(fixture,path):
    return start(fixture,path)+[
        'S_child = $ns_pause(S_start[.COMPLETION = NORMAL],3,20000)','$ns_ready(S_child,3)',
        'S_child.CURRENT = (pcallcontext_child)','$receiving_function(S_child,pcallcontext_child.FUNCTION) = (pfunction_child)',
        '$parameter_nullsafe_current(S_child,pfunction_child)',
        '$parameter_receive_owner(S_child.CURRENT) = (n_child)','$parameter_receive_birth(S_child,n_child) = (preceivebirth_child)',
        '$parameter_receive_parent(S_child.FRAMES) = (n_parent)','$parameter_receive_birth(S_child,n_parent) = (preceivebirth_parent)',
        '$class_method_origin(S_child.CLASSES,preceivebirth_parent.FUNCTION) = (pmethoddesc_parent)',
        '$class_method_origin(S_child.CLASSES,pfunction_child.ORIGIN) = (pmethoddesc_child)',
        'pmethoddesc_parent.NAME = pmethoddesc_child.NAME','pmethoddesc_parent.OWNER =/= pmethoddesc_child.OWNER',
        'preceivebirth_parent.FUNCTION =/= preceivebirth_child.FUNCTION',
        'preceivebirth_parent.CALLSITE = preceivebirth_child.CALLSITE','preceivebirth_parent.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth_child.CACHE_OWNER = (CACHE_SHARED)','~preceivebirth_parent.RAW_ENTRY','~preceivebirth_child.RAW_ENTRY',
        '$parameter_receive_cache_entry(S_child,preceivebirth_parent)','$parameter_receive_cache_entry(S_child,preceivebirth_child)',
        '$default_at(pmethoddesc_parent.FUNCTION.DEFAULTS,0) = (pdefault_parent)',
        '$default_at(pfunction_child.DEFAULTS,0) = (pdefault_child)','pdefault_parent.ORIGIN =/= pdefault_child.ORIGIN',
        '$default_cache_at(S_child.DEFAULTCACHE,pdefault_parent.ORIGIN) = eps','$default_cache_at(S_child.DEFAULTCACHE,pdefault_child.ORIGIN) = eps',
        '$call_descriptors_valid(S_child)','S_one = $drive_steps(S_child,1)','S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]','$parameter_receive_birth(S_after,n_child) = (preceivebirth_child_closed)',
        '~preceivebirth_child_closed.ACTIVE',
        '~$parameter_receive_cache_child(S_after,preceivebirth_parent,n_parent,preceivebirth_child_closed)',
        'S_warm = $ns_pause(S_after,3,20000)','$ns_ready(S_warm,3)',
        '$parameter_receive_birth(S_warm,n_parent) = (preceivebirth_parent)',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault_child.ORIGIN) = (pdefaultcache_child)','pdefaultcache_child.VALUE = PINT 9',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault_parent.ORIGIN) = eps',
        'S_warm.CURRENT = (pcallcontext_parent)','pcallcontext_parent.FUNCTION = pmethoddesc_parent.FUNCTION.ORIGIN',
        'pcallcontext_parent.TARGET = METHOD_TARGET n_parent_receiver pmethoddesc_parent.FUNCTION.ORIGIN',
        '$parameter_nullsafe_current(S_warm,pmethoddesc_parent.FUNCTION)',
        'S_wrong = S_warm[.CURRENT = (pcallcontext_parent[.FUNCTION = pfunction_child.ORIGIN][.LEXICAL_CLASS = (pmethoddesc_child.OWNER)][.TARGET = METHOD_TARGET n_parent_receiver pfunction_child.ORIGIN])]',
        '~$parameter_nullsafe_current(S_wrong,pfunction_child)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_child_closed)','$call_descriptors_valid(S_warm)',
    ]+finish(path)+[
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault_child.ORIGIN) = (pdefaultcache_child)',
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault_parent.ORIGIN) = (pdefaultcache_parent)',
        'pdefaultcache_parent.VALUE = PARRAY n_parent_array','S_done.ARRAYS[n_parent_array].ITEMS = eps',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
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

#!/usr/bin/env python3
"""Check selected method functions, inherited cache keys and retired receivers."""
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
PEER = ROOT / 'tests/semantics/deprecated_method_name_default_review'
AUTHOR = ROOT / 'tests/semantics/deprecated_cv_method_default'
SELECTIONS = {'static': PEER / 'inherited-static-name.php',
    'receiver': PEER / 'receiver-retirement.php', 'nested': AUTHOR / 'nested-different-method.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $method_review_ready(pstate,nat,porigin,porigin) : bool
def $method_review_ready(S,0,porigin_parent,porigin_site) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin_child 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin_child /\ porigin_child =/= porigin_parent
  -- if pcallcontext.CALLSITE = (porigin_site)
def $method_review_ready(S,1,porigin,porigin_site) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 0) :: eps
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $method_review_ready(S,n_mode,porigin,porigin_site) = false -- otherwise
dec $method_review_pause(pstate,nat,porigin,porigin,nat) : pstate
def $method_review_pause(S,n_mode,porigin,porigin_site,n) = S
  -- if $method_review_ready(S,n_mode,porigin,porigin_site)
def $method_review_pause(S,n_mode,porigin,porigin_site,n) = $method_review_pause(S_next[.COMPLETION = NORMAL],n_mode,porigin,porigin_site,$nabs($(n - 1)))
  -- if ~$method_review_ready(S,n_mode,porigin,porigin_site)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $method_review_pause(S,n_mode,porigin,porigin_site,n) = S -- otherwise
'''


def bytes_term(value):
    return '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET', 'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.CURRENT = (pcallcontext)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        '$class_method_origin(S_warn.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        'pcallcontext.CALLSITE = (porigin_site)', '$parameter_cv_method_site(S_warn,porigin_site)',
        '$target_function(S_warn,pcallcontext.TARGET) = (pfunction)',
        '$parameter_cv_method_current(S_warn,pfunction)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        'preceivebirth.FUNCTION = pfunction.ORIGIN',
        'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth.ENTRY = eps', 'preceivebirth.CONSTRUCTOR_ENTRY = eps',
        '$parameter_receive_cache_entry(S_warn,preceivebirth)',
        '$machine_roots(S_warn[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warn)',
        '$call_descriptors_valid(S_warn)']


def static(fixture, path):
    checks = start(fixture, path)
    checks += [
        'pmethoddesc.STATIC', 'pcallcontext.RECEIVER = eps',
        'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext.CALLED_CLASS = (porigin_called)', 'porigin_called =/= pmethoddesc.OWNER',
        'pcallcontext.TARGET = SCOPED_TARGET porigin_called pfunction.ORIGIN porigin_called eps poperand_selector',
        '$scoped_call_selected(S_warn,pcallcontext.TARGET,(porigin_site))',
        'S_bind = $parameter_test_pause(S_warn,0,10000)',
        'S_bind.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("member")) = (n_member)',
        'S_bind.STORE[n_member] = DEFINED pvalue_member',
        '$string_bytes(pvalue_member) = ($ptascii("other"))',
        '$parameter_cv_method_current(S_bind,pfunction)',
        '$parameter_default_recipient(S_bind,pfunction)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        'S_step_raw = $drive_steps(S_bind,1)', 'S_step_raw.COMPLETION = BUDGET',
        'S_step = S_step_raw[.COMPLETION = NORMAL]',
        '$default_cache_at(S_step.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'S_warm = $method_review_pause(S_step,1,pfunction.ORIGIN,porigin_site,10000)',
        '$method_review_ready(S_warm,1,pfunction.ORIGIN,porigin_site)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pcallcontext.FUNCTION',
        'pcallcontext_warm.CALLED_CLASS =/= pcallcontext.CALLED_CLASS',
        'pcallcontext_warm.LEXICAL_CLASS = pcallcontext.LEXICAL_CLASS',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$parameter_receive_birth(S_warm,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_warm,preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.CALLS = (pfunction.ORIGIN,pcallcontext.CALLSITE,pcallcontext.LEXICAL_CLASS,pcallcontext_warm.CALLED_CLASS) :: eps]])',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = ' + bytes_term('H|Child201|E|N|Other201|E|Base201|E|'),
    ]
    return checks


def receiver(fixture, path):
    checks = start(fixture, path)
    checks += [
        'pcallcontext.RECEIVER = (n_receiver)',
        'pcallcontext.TARGET = METHOD_TARGET n_receiver pfunction.ORIGIN',
        'S_bind = $parameter_test_pause(S_warn,0,10000)',
        'S_bind.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("receiver")) = (n_global_receiver)',
        'S_bind.STORE[n_global_receiver] = DEFINED PNULL',
        '$lookup(psymboltable_global.ENV,$ptascii("member")) = (n_member)',
        'S_bind.STORE[n_member] = DEFINED pvalue_member',
        '$string_bytes(pvalue_member) = ($ptascii("other"))',
        '(HOBJECT n_receiver) <- S_bind.ALLOCATIONS',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 1',
        '$parameter_cv_method_current(S_bind,pfunction)',
        'S_step_raw = $drive_steps(S_bind,1)', 'S_step_raw.COMPLETION = BUDGET',
        'S_step = S_step_raw[.COMPLETION = NORMAL]',
        'S_warm = $method_review_pause(S_step,1,pfunction.ORIGIN,porigin_site,10000)',
        '$method_review_ready(S_warm,1,pfunction.ORIGIN,porigin_site)',
        '~((HOBJECT n_receiver) <- S_warm.ALLOCATIONS)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.RECEIVER = (n_next)', 'n_next =/= n_receiver',
        '$parameter_receive_birth(S_warm,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        'n_after_receiver = $(n_receiver + 1)',
        'n_object_tail = $nabs($(|S_warm.OBJECTS| - n_after_receiver))',
        'S_poison_receiver = S_warm[.OBJECTS = S_warm.OBJECTS[0:n_receiver] ++ [STDINSTANCE] ++ S_warm.OBJECTS[n_after_receiver:n_object_tail]]',
        '$parameter_receive_cache_entry(S_poison_receiver,preceivebirth_closed)',
        'S_poison_name = S_warm[.STORE = $set_cell(S_warm.STORE,n_member,UNDEFINED)]',
        '$parameter_receive_cache_entry(S_poison_name,preceivebirth_closed)',
        '$parameter_cv_method_current(S_warm,pfunction)',
        'S_wrong_target = S_warm[.CURRENT = (pcallcontext_warm[.TARGET = METHOD_TARGET n_receiver pfunction.ORIGIN])]',
        '~$parameter_cv_method_current(S_wrong_target,pfunction)',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = ' + bytes_term('H|L|M|E|D|R|G|N|M|E|D|Z|'),
    ]
    return checks


def nested(fixture, path):
    checks = start(fixture, path)
    checks += [
        'S_child = $method_review_pause(S_warn,0,pfunction.ORIGIN,porigin_site,10000)',
        '$method_review_ready(S_child,0,pfunction.ORIGIN,porigin_site)',
        'S_child.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.FUNCTION =/= pcallcontext.FUNCTION',
        'pcallcontext_child.CALLSITE = pcallcontext.CALLSITE',
        'pcallcontext_child.RECEIVER = pcallcontext.RECEIVER',
        '$receiving_function(S_child,pcallcontext_child.FUNCTION) = (pfunction_child)',
        '$parameter_cv_method_current(S_child,pfunction_child)',
        'S_bind = $parameter_test_pause(S_child,0,10000)',
        'S_bind.PARAMETERRECEIVES = [preceivebirth_parent,preceivebirth_child]',
        'preceivebirth_parent.FUNCTION = pfunction.ORIGIN',
        'preceivebirth_child.FUNCTION = pfunction_child.ORIGIN',
        'preceivebirth_child.CACHE_OWNER = preceivebirth_parent.CACHE_OWNER',
        'preceivebirth_child.ORIGIN =/= preceivebirth_parent.ORIGIN',
        '~preceivebirth_child.ACTIVE',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_child)',
        '~$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_receive,preceivebirth_child)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_at(pfunction_child.DEFAULTS,0) = (pdefault_child)',
        'pdefault_child.ORIGIN =/= pdefault.ORIGIN',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = eps',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault_child.ORIGIN) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PINT 9',
        '$parameter_default_recipient(S_bind,pfunction)',
        'S_wrong_function = S_bind[.CURRENT = (pcallcontext[.FUNCTION = pfunction_child.ORIGIN])]',
        '~$parameter_cv_method_current(S_wrong_function,pfunction_child)',
        'S_step_raw = $drive_steps(S_bind,1)', 'S_step_raw.COMPLETION = BUDGET',
        'S_step = S_step_raw[.COMPLETION = NORMAL]',
        '$default_cache_at(S_step.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache_parent)',
        'pdefaultcache_parent.VALUE = PARRAY n_array',
        '$default_cache_at(S_step.DEFAULTCACHE,pdefault_child.ORIGIN) = (pdefaultcache_child)',
        'S_done = $drive(S_step,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = ' + bytes_term('H|B|N|Q|F|E|R|F|E|B|N|'),
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
        + ''.join('  -- if ' + check + '\n' for check in checks))
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

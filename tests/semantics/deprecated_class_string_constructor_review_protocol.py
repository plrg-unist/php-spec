#!/usr/bin/env python3
"""Check selected class-string entry receipts across reentry and retirement."""
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
PEER = ROOT / 'tests/semantics/deprecated_class_string_constructor_review'
AUTHOR = ROOT / 'tests/semantics/deprecated_class_string_constructor_default'
SELECTIONS = {'selection': PEER / 'promoted-retired-warm.php',
    'nested': AUTHOR / 'nested-same-site.php', 'exit': PEER / 'case-body-exit.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

CHILD = r'''
dec $classstring_review_child_ready(pstate,porigin,nat) : bool
def $classstring_review_child_ready(S,porigin,n_parent) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_child)
  -- if n_child =/= n_parent
def $classstring_review_child_ready(S,porigin,n_parent) = false -- otherwise
dec $classstring_review_child_pause(pstate,porigin,nat,nat) : pstate
def $classstring_review_child_pause(S,porigin,n_parent,n) = S
  -- if $classstring_review_child_ready(S,porigin,n_parent)
def $classstring_review_child_pause(S,porigin,n_parent,n) = $classstring_review_child_pause(S_next[.COMPLETION = NORMAL],porigin,n_parent,$nabs($(n - 1)))
  -- if ~$classstring_review_child_ready(S,porigin,n_parent)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $classstring_review_child_pause(S,porigin,n_parent,n) = S -- otherwise
'''


def output(value):
    return '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET', 'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.CURRENT = (pcallcontext)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        'pcallcontext.TARGET = METHOD_TARGET n_parent pfunction.ORIGIN',
        'pcallcontext.RECEIVER = (n_parent)',
        'S_warn.FRAMES = pframe_caller :: pframe_tail*',
        'pframe_caller.TODO = (CTOR_RESULT n_parent) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_caller_tail*',
        'pcallcontext.CALLSITE = (pdynamicnew.SITE)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        'preceivebirth.CONSTRUCTOR_ENTRY = (pdynamicnew)',
        'preceivebirth.CACHE_OWNER = (CACHE_SHARED)', 'preceivebirth.ENTRY = eps',
        r'pdynamicnew.SCOPE = eps /\ pdynamicnew.CALLED = eps /\ pdynamicnew.CLOSURE = eps',
        '$dynamic_new_record_valid(S_warn,pdynamicnew)',
        '$parameter_constructor_current(S_warn,pfunction)',
        '$parameter_receive_cache_entry(S_warn,preceivebirth)',
        '$task_nodes(DYNAMIC_NEW_FINISH pdynamicnew) = eps',
        '$machine_roots(S_warn[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warn)',
        '~$parameter_receive_cache_entry(S_warn,preceivebirth[.CONSTRUCTOR_ENTRY = eps])',
        'S_no_finish = S_warn[.FRAMES = pframe_caller[.TODO = (CTOR_RESULT n_parent) :: ptask_caller_tail*] :: pframe_tail*]',
        '~$parameter_constructor_current(S_no_finish,pfunction)',
        '$call_descriptors_valid(S_warn)']


def selection(fixture, path):
    checks = start(fixture, path)
    checks += [
        '$string_bytes(pdynamicnew.SOURCE) = (' + output('Box199') + ')',
        'pdynamicnew.CLASS = ' + output('Box199'),
        'S_wrong_finish = S_warn[.FRAMES = pframe_caller[.TODO = (CTOR_RESULT n_parent) :: (DYNAMIC_NEW_FINISH pdynamicnew[.SOURCE = PSTRING ' + output('Other199') + '][.CLASS = ' + output('Other199') + ']) :: ptask_caller_tail*] :: pframe_tail*]',
        '~$parameter_constructor_current(S_wrong_finish,pfunction)',
        'S_bind = $parameter_test_pause(S_warn,0,10000)',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        'S_bind.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("selector")) = (n_selector)',
        'S_bind.STORE[n_selector] = DEFINED pvalue_rebound',
        '$string_bytes(pvalue_rebound) = (' + output('Other199') + ')',
        '$parameter_constructor_current(S_bind,pfunction)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        'S_bind.RESULT = KNOWN (PARRAY n_array)', '$call_descriptors_valid(S_bind)',
        'S_zero = $drive(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'S_one_raw = $drive(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.CONSTRUCTOR_ENTRY = (pdynamicnew)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_cache_at(S_one.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        'S_warm = $ctor_review_pause(S_one,2,n_parent,pfunction.ORIGIN,10000)',
        '$ctor_review_ready(S_warm,2,n_parent,pfunction.ORIGIN)',
        '~((HOBJECT n_parent) <- S_warm.ALLOCATIONS)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        'S_warm.FRAMES = pframe_warm :: pframe_warm_tail*',
        'pframe_warm.TODO = (CTOR_RESULT n_warm) :: (DYNAMIC_NEW_FINISH pdynamicnew_warm) :: ptask_warm_tail*',
        'pdynamicnew_warm.CLASS = pdynamicnew.CLASS',
        'pdynamicnew_warm.SITE =/= pdynamicnew.SITE',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_warm,preceivebirth_closed[.CONSTRUCTOR_ENTRY = (pdynamicnew_warm)])',
        '$parameter_constructor_current(S_warm,pfunction)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$machine_roots(S_warm[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warm)',
        'S_done = $drive(S_bind,20000)', 'S_done.COMPLETION = NORMAL',
        '$drive(S_one,20000) = S_done',
        '$ctor_review_output(S_done.EVENTS) = ' + output('H|L|C|B|E|R|C|E|R|'),
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
    ]
    return checks


def nested(fixture, path):
    checks = start(fixture, path)
    checks += [
        'S_child = $classstring_review_child_pause(S_warn,pfunction.ORIGIN,n_parent,10000)',
        '$classstring_review_child_ready(S_child,pfunction.ORIGIN,n_parent)',
        'S_child.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.RECEIVER = (n_child)',
        'pcallcontext_child.FUNCTION = pcallcontext.FUNCTION',
        'S_child.FRAMES = pframe_child :: pframe_child_tail*',
        'pframe_child.TODO = (CTOR_RESULT n_child) :: (DYNAMIC_NEW_FINISH pdynamicnew_child) :: ptask_child_tail*',
        'pdynamicnew_child.SITE = pdynamicnew.SITE',
        'pdynamicnew_child.CLASS =/= pdynamicnew.CLASS',
        'pcallcontext_child.CALLED_CLASS =/= pcallcontext.CALLED_CLASS',
        '$parameter_constructor_current(S_child,pfunction)',
        'S_child_wrong = S_child[.FRAMES = pframe_child[.TODO = (CTOR_RESULT n_child) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_child_tail*] :: pframe_child_tail*]',
        '~$parameter_constructor_current(S_child_wrong,pfunction)',
        'S_bind = $parameter_test_pause(S_child,0,10000)',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth_parent)',
        'preceivebirth_parent.CONSTRUCTOR_ENTRY = (pdynamicnew)',
        'S_bind.PARAMETERRECEIVES = [preceivebirth_parent,preceivebirth_child]',
        'preceivebirth_child.CONSTRUCTOR_ENTRY = (pdynamicnew_child)',
        '~preceivebirth_child.ACTIVE',
        'preceivebirth_child.CACHE_OWNER = preceivebirth_parent.CACHE_OWNER',
        'preceivebirth_child.FUNCTION = preceivebirth_parent.FUNCTION',
        'preceivebirth_child.ORIGIN = preceivebirth_parent.ORIGIN',
        'preceivebirth_child.CALLSITE = preceivebirth_parent.CALLSITE',
        '~((HOBJECT n_child) <- S_bind.ALLOCATIONS)',
        '(HOBJECT n_parent) <- S_bind.ALLOCATIONS',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_child)',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_child[.CONSTRUCTOR_ENTRY = (pdynamicnew)])',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_parent[.CONSTRUCTOR_ENTRY = (pdynamicnew_child)])',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_child[.CONSTRUCTOR_ENTRY = eps])',
        '$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_receive,preceivebirth_child)',
        '$parameter_constructor_current(S_bind,pfunction)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_pending_cache_valid(S_bind,pdefault)',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PINT 9',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        '$call_descriptors_valid(S_bind)',
        'S_after_raw = $drive_steps(S_bind,1)', 'S_after_raw.COMPLETION = BUDGET',
        'S_after = S_after_raw[.COMPLETION = NORMAL]',
        '$default_cache_at(S_after.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache_parent)',
        'pdefaultcache_parent.VALUE = PARRAY n_array',
        'S_done = $drive(S_after,20000)', 'S_done.COMPLETION = NORMAL',
        '$parameter_receive_cache_entry(S_done,preceivebirth_child)',
        '$ctor_review_output(S_done.EVENTS) = ' + output('H|Ns199\\Other199|N|D|Q|Ns199\\First199|E|R|D|Z|'),
    ]
    return checks


def exit_checks(fixture, path):
    checks = start(fixture, path)
    checks += [
        '$string_bytes(pdynamicnew.SOURCE) = (' + output('\\cAsEeXiT199') + ')',
        'pdynamicnew.CLASS = $ppcall_literal_name(' + output('\\cAsEeXiT199') + ')',
        '$object_class_origin(S_warn,n_parent) = (porigin_selected)',
        '$class_named(S_warn.CLASSNAMES,$ptlc(pdynamicnew.CLASS)) = (porigin_selected)',
        'S_exit = $ctor_review_pause(S_warn,4,n_parent,pfunction.ORIGIN,10000)',
        '$ctor_review_ready(S_exit,4,n_parent,pfunction.ORIGIN)',
        'S_exit.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("selector")) = (n_selector)',
        'S_exit.STORE[n_selector] = DEFINED pvalue_rebound',
        '$string_bytes(pvalue_rebound) = (' + output('Other199') + ')',
        '$parameter_constructor_current(S_exit,pfunction)',
        '$parameter_receive_birth(S_exit,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.CONSTRUCTOR_ENTRY = (pdynamicnew)',
        '$parameter_receive_cache_entry(S_exit,preceivebirth_closed)',
        '~(n_parent <- S_exit.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_exit),HOBJECT n_parent) = 3',
        'S_exit_step_raw = $drive_steps(S_exit,1)', 'S_exit_step_raw.COMPLETION = BUDGET',
        'S_exit_step = S_exit_step_raw[.COMPLETION = NORMAL]',
        'S_exit_step.TODO = (EXIT_UNWIND 7) :: eps',
        'n_parent <- S_exit_step.DESTRUCTION.CALLED',
        '(HOBJECT n_parent) <- S_exit_step.ALLOCATIONS',
        '$heap_owners($heap_graph(S_exit_step),HOBJECT n_parent) = 3',
        'S_done = $drive_steps(S_exit_step,20000)', 'S_done.COMPLETION = EXITED 7',
        '$ctor_review_output(S_done.EVENTS) = ' + output('H|C|E|S|E|Z|'),
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
    checks = (exit_checks if group == 'exit' else globals()[group])(checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + CHILD + '\ndec $main() : bool\ndef $main() = true\n'
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

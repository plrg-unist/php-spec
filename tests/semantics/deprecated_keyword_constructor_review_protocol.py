#!/usr/bin/env python3
"""Check keyword factory scopes independently of constructor and receiver life."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_constructor_default_review_protocol import PREFIX, EXTRA
from deprecated_class_string_constructor_review_protocol import CHILD
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
PEER = ROOT / 'tests/semantics/deprecated_keyword_constructor_review'
AUTHOR = ROOT / 'tests/semantics/deprecated_keyword_constructor_default'
SELECTIONS = {'factory': PEER / 'factory-receiver-retirement.php',
    'nested': AUTHOR / 'nested-late-called.php', 'exit': PEER / 'self-body-exit.php',
    'entry': AUTHOR / 'nested-late-called.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_term(value):
    return '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET', 'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.CURRENT = (pcallcontext_ctor)',
        '$receiving_function(S_warn,pcallcontext_ctor.FUNCTION) = (pfunction)',
        'pcallcontext_ctor.RECEIVER = (n_ctor)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        'preceivebirth.CONSTRUCTOR_ENTRY = (pdynamicnew)',
        '$parameter_keyword_constructor_source(S_warn,pdynamicnew) = (pmethoddesc_factory)',
        'pdynamicnew.CLOSURE = eps', 'pdynamicnew.SCOPE = (pmethoddesc_factory.OWNER)',
        'pdynamicnew.CALLED = (porigin_factory_called)',
        'pcallcontext_ctor.LEXICAL_CLASS = (porigin_ctor_owner)',
        'porigin_ctor_owner =/= pmethoddesc_factory.OWNER',
        'S_warn.FRAMES = pframe_factory :: pframe_tail*',
        'pframe_factory.TODO = (CTOR_RESULT n_ctor) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_factory_tail*',
        'pframe_factory.CONTEXT = (pcallcontext_factory)',
        'pcallcontext_factory.FUNCTION = pmethoddesc_factory.FUNCTION.ORIGIN',
        'pcallcontext_factory.LEXICAL_CLASS = pdynamicnew.SCOPE',
        'pcallcontext_factory.CALLED_CLASS = pdynamicnew.CALLED',
        '~$dynamic_new_valid(S_warn,pdynamicnew)',
        '$dynamic_new_valid($constant_frame_scope(S_warn,pframe_factory,pframe_tail*),pdynamicnew)',
        '$parameter_constructor_current(S_warn,pfunction)',
        'n_factory_calls = $nabs($(|preceivebirth.CAUSE.CALLS| - 1))',
        'pdeclcalls_factory = preceivebirth.CAUSE.CALLS[1:n_factory_calls]',
        '$parameter_keyword_constructor_calls(S_warn,pdynamicnew,pdeclcalls_factory,preceivebirth.PUBLICATION)',
        '$task_nodes(DYNAMIC_NEW_FINISH pdynamicnew) = eps',
        '$machine_roots(S_warn[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warn)',
        '$call_descriptors_valid(S_warn)']


def factory(fixture, path):
    checks = start(fixture, path)
    checks += [
        'pdynamicnew.SOURCE = PSTRING $ptascii("parent")',
        'pcallcontext_factory.RECEIVER = (n_factory)', 'n_factory =/= n_ctor',
        'porigin_factory_called =/= pmethoddesc_factory.OWNER',
        'pcallcontext_ctor.CALLED_CLASS = (porigin_ctor_owner)',
        'pdynamicnew_wrong_called = pdynamicnew[.CALLED = pdynamicnew.SCOPE]',
        '$dynamic_new_record_valid(S_warn,pdynamicnew_wrong_called)',
        '$dynamic_new_record_name(S_warn,pdynamicnew_wrong_called) = (pdynamicnew.CLASS)',
        '~$parameter_keyword_constructor_calls(S_warn,pdynamicnew_wrong_called,pdeclcalls_factory,preceivebirth.PUBLICATION)',
        '~$parameter_receive_cache_entry(S_warn,preceivebirth[.CONSTRUCTOR_ENTRY = (pdynamicnew_wrong_called)])',
        'S_wrong_caller = S_warn[.FRAMES = pframe_factory[.TODO = (CTOR_RESULT n_ctor) :: (DYNAMIC_NEW_FINISH pdynamicnew_wrong_called) :: ptask_factory_tail*] :: pframe_tail*]',
        '~$parameter_constructor_current(S_wrong_caller,pfunction)',
        'S_bind = $parameter_test_pause(S_warn,0,10000)',
        'S_bind.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("factory")) = (n_global_factory)',
        'S_bind.STORE[n_global_factory] = DEFINED PNULL',
        '(HOBJECT n_factory) <- S_bind.ALLOCATIONS',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_factory) = 1',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_ctor) = 2',
        '$parameter_constructor_current(S_bind,pfunction)',
        'S_done = $drive(S_bind,20000)', 'S_done.COMPLETION = NORMAL',
        '~((HOBJECT n_factory) <- S_done.ALLOCATIONS)',
        '$parameter_receive_birth(S_done,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_done,preceivebirth_closed[.CONSTRUCTOR_ENTRY = (pdynamicnew_wrong_called)])',
        'n_after_factory = $(n_factory + 1)',
        'n_object_tail = $nabs($(|S_done.OBJECTS| - n_after_factory))',
        'S_poison_factory = S_done[.OBJECTS = S_done.OBJECTS[0:n_factory] ++ [STDINSTANCE] ++ S_done.OBJECTS[n_after_factory:n_object_tail]]',
        '$parameter_receive_cache_entry(S_poison_factory,preceivebirth_closed)',
        '$ctor_review_output(S_done.EVENTS) = ' + bytes_term('C|Leaf200|N|F|H|C|Root200|E|D|Leaf200|R|G|E|D|Root200|Z|'),
    ]
    return checks


def nested(fixture, path):
    checks = start(fixture, path)
    checks += [
        'pdynamicnew.SOURCE = PSTRING $ptascii("static")',
        'pcallcontext_ctor.CALLED_CLASS = pdynamicnew.CALLED',
        'S_child = $classstring_review_child_pause(S_warn,pfunction.ORIGIN,n_ctor,10000)',
        '$classstring_review_child_ready(S_child,pfunction.ORIGIN,n_ctor)',
        'S_child.CURRENT = (pcallcontext_child)', 'pcallcontext_child.RECEIVER = (n_child)',
        'S_child.FRAMES = pframe_child :: pframe_child_tail*',
        'pframe_child.TODO = (CTOR_RESULT n_child) :: (DYNAMIC_NEW_FINISH pdynamicnew_child) :: ptask_child_tail*',
        'pdynamicnew_child.SITE = pdynamicnew.SITE',
        'pdynamicnew_child.SCOPE = pdynamicnew.SCOPE',
        'pdynamicnew_child.CALLED =/= pdynamicnew.CALLED',
        'pcallcontext_child.CALLED_CLASS = pdynamicnew_child.CALLED',
        '$parameter_constructor_current(S_child,pfunction)',
        'S_bind = $parameter_test_pause(S_child,0,10000)',
        'S_bind.PARAMETERRECEIVES = [preceivebirth_parent,preceivebirth_child]',
        'preceivebirth_parent.CONSTRUCTOR_ENTRY = (pdynamicnew)',
        'preceivebirth_child.CONSTRUCTOR_ENTRY = (pdynamicnew_child)',
        '~preceivebirth_child.ACTIVE',
        '~((HOBJECT n_child) <- S_bind.ALLOCATIONS)',
        'preceivebirth_child.CACHE_OWNER = preceivebirth_parent.CACHE_OWNER',
        'n_child_factory_calls = $nabs($(|preceivebirth_child.CAUSE.CALLS| - 1))',
        'pdeclcalls_child_factory = preceivebirth_child.CAUSE.CALLS[1:n_child_factory_calls]',
        '$parameter_keyword_constructor_calls(S_bind,pdynamicnew_child,pdeclcalls_child_factory,preceivebirth_child.PUBLICATION)',
        '~$parameter_keyword_constructor_calls(S_bind,pdynamicnew,pdeclcalls_child_factory,preceivebirth_child.PUBLICATION)',
        '$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_receive,preceivebirth_child)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_child)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_parent)',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        'S_done = $drive(S_bind,20000)', 'S_done.COMPLETION = NORMAL',
        '$parameter_receive_cache_entry(S_done,preceivebirth_child)',
        '$ctor_review_output(S_done.EVENTS) = ' + bytes_term('H|Ns200\\Other200|N|D|Q|Ns200\\First200|E|R|D|Z|'),
    ]
    return checks


def exit_checks(fixture, path):
    checks = start(fixture, path)
    checks += [
        'pdynamicnew.SOURCE = PSTRING $ptascii("self")',
        'pcallcontext_ctor.CALLED_CLASS = pdynamicnew.SCOPE',
        'pdynamicnew.CALLED =/= pdynamicnew.SCOPE',
        'pdynamicnew_wrong_called = pdynamicnew[.CALLED = pdynamicnew.SCOPE]',
        '$dynamic_new_record_valid(S_warn,pdynamicnew_wrong_called)',
        '~$parameter_keyword_constructor_calls(S_warn,pdynamicnew_wrong_called,pdeclcalls_factory,preceivebirth.PUBLICATION)',
        'S_exit = $ctor_review_pause(S_warn,4,n_ctor,pfunction.ORIGIN,10000)',
        '$ctor_review_ready(S_exit,4,n_ctor,pfunction.ORIGIN)',
        '$parameter_constructor_current(S_exit,pfunction)',
        '$parameter_receive_birth(S_exit,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '~$parameter_receive_cache_entry(S_exit,preceivebirth_closed[.CONSTRUCTOR_ENTRY = (pdynamicnew_wrong_called)])',
        'S_step_raw = $drive_steps(S_exit,1)', 'S_step_raw.COMPLETION = BUDGET',
        'S_step = S_step_raw[.COMPLETION = NORMAL]',
        'S_step.TODO = (EXIT_UNWIND 7) :: eps',
        'n_ctor <- S_step.DESTRUCTION.CALLED',
        '$heap_owners($heap_graph(S_step),HOBJECT n_ctor) = 3',
        'S_done = $drive_steps(S_step,20000)', 'S_done.COMPLETION = EXITED 7',
        '$ctor_review_output(S_done.EVENTS) = ' + bytes_term('H|C|Base200|E|S|E|Z|'),
    ]
    return checks


def entry(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET', 'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.CURRENT = (pcallcontext_ctor)',
        '$receiving_function(S_warn,pcallcontext_ctor.FUNCTION) = (pfunction)',
        'pcallcontext_ctor.RECEIVER = (n_ctor)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        'S_child = $classstring_review_child_pause(S_warn,pfunction.ORIGIN,n_ctor,10000)',
        '$classstring_review_child_ready(S_child,pfunction.ORIGIN,n_ctor)',
        'S_bind = $parameter_test_pause(S_child,0,10000)',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        'S_bind.PARAMETERRECEIVES = [preceivebirth_parent,preceivebirth_child]',
        '~preceivebirth_child.ACTIVE', 'preceivebirth_child.CONSTRUCTOR_ENTRY =/= eps',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_child)',
        '$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_receive,preceivebirth_child)',
        'preceivebirth_missing = preceivebirth_child[.CONSTRUCTOR_ENTRY = eps]',
        '$parameter_receive_source_valid(S_bind,preceivebirth_missing)',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_missing)',
        '~$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_receive,preceivebirth_missing)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '~$default_pending_cache_valid(S_bind[.PARAMETERRECEIVES = [preceivebirth_parent,preceivebirth_missing]],pdefault)']


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
        'tests/semantics/deprecated_class_string_constructor_review_protocol.py',
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

#!/usr/bin/env python3
"""Check genuine shutdown method entries, registry owners and closed receives."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_shutdown_method_default_review'
SELECTIONS = {'registry': SOURCE / 'registry-retention.php',
    'reentry': SOURCE / 'callback-direct-reentry.php',
    'factory': SOURCE / 'implicit-this-factory.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $shutdown_review_ready(pstate,nat,porigin) : bool
def $shutdown_review_ready(S,0,porigin) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (SHUTDOWN_RESULT 0 poperand*) :: eps
def $shutdown_review_ready(S,1,porigin) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (SHUTDOWN_RESULT 1 poperand*) :: eps
def $shutdown_review_ready(S,2,porigin) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE =/= eps
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $shutdown_review_ready(S,3,porigin) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 0) :: eps
  -- if S.SHUTDOWN.INDEX = 1
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = eps
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $shutdown_review_ready(S,n_mode,porigin) = false -- otherwise
dec $shutdown_review_pause(pstate,nat,porigin,nat) : pstate
def $shutdown_review_pause(S,n_mode,porigin,n) = S
  -- if $shutdown_review_ready(S,n_mode,porigin)
def $shutdown_review_pause(S,n_mode,porigin,n) = $shutdown_review_pause(S_next[.COMPLETION = NORMAL],n_mode,porigin,$nabs($(n - 1)))
  -- if ~$shutdown_review_ready(S,n_mode,porigin)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $shutdown_review_pause(S,n_mode,porigin,n) = S -- otherwise
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.CURRENT = (pcallcontext)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        '$class_method_origin(S_warn.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        'pcallcontext.CALLSITE = eps', 'pcallcontext.LINE = $(-1)',
        '$shutdown_context_call(pcallcontext,S_warn.CURRENT,S_warn.FRAMES) = ((n_index,poperand_sent*))',
        'n_index = 0', 'S_warn.SHUTDOWN.INDEX = n_index',
        'pshutdownentry = S_warn.SHUTDOWN.ENTRIES[n_index]',
        'pcallcontext.TARGET = CALLBACK_BORROWED_TARGET pcalltarget',
        'pcalltarget = pshutdownentry.TARGET',
        'pcalltarget = HANDLER_METHOD_TARGET b_class porigin_requested ptbytes_method pcalltarget_inner',
        '$shutdown_context_valid(S_warn,pcallcontext)',
        '$parameter_default_recipient(S_warn,pfunction)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE', 'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth.ENTRY = eps', 'preceivebirth.CONSTRUCTOR_ENTRY = eps',
        'preceivebirth.SHUTDOWN_ENTRY = (pshutdownreceive)',
        'pshutdownreceive.INDEX = n_index',
        'pshutdownreceive.REGISTRATION = pshutdownentry.CALL.SITE',
        'pshutdownreceive.LINE = pshutdownentry.CALL.LINE',
        'pshutdownreceive.TARGET = pshutdownentry.TARGET',
        '$parameter_receive_cache_entry(S_warn,preceivebirth)',
        '~$parameter_receive_cache_entry(S_warn,preceivebirth[.SHUTDOWN_ENTRY = eps])',
        '$machine_roots(S_warn[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warn)',
        '$call_descriptors_valid(S_warn)']


def registry(fixture, path):
    checks = start(fixture, path)
    checks += [
        'pshutdownentry.CACHEOBJECT = (n_receiver)',
        'pcallcontext.RECEIVER = (n_receiver)',
        'pshutdownentry.ARGS = [POBJECT n_argument]',
        '$call_context_roots(S_warn.CURRENT) = eps',
        '$shutdown_roots(S_warn.SHUTDOWN.ENTRIES) = [HOBJECT n_receiver,HOBJECT n_argument]',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_argument) = 2',
        '~$parameter_default_recipient(S_warn[.CURRENT = (pcallcontext[.CALLSITE = (pshutdownentry.CALL.SITE)])],pfunction)',
        '~$parameter_default_recipient(S_warn[.SHUTDOWN.INDEX = 1],pfunction)',
        '~$parameter_default_recipient(S_warn[.CURRENT = (pcallcontext[.ARGC = 0])],pfunction)',
        '~$parameter_default_recipient(S_warn[.SHUTDOWN.SENT = eps],pfunction)',
        'S_bind = $parameter_test_pause(S_warn,0,10000)',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 1) :: eps',
        'S_bind.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("receiver")) = (n_global_receiver)',
        'S_bind.STORE[n_global_receiver] = DEFINED PNULL',
        '$lookup(psymboltable_global.ENV,$ptascii("argument")) = (n_global_argument)',
        'S_bind.STORE[n_global_argument] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_argument) = 2',
        '$shutdown_context_valid(S_bind,pcallcontext)',
        '$parameter_default_recipient(S_bind,pfunction)', '$call_descriptors_valid(S_bind)',
        'S_result = $shutdown_review_pause(S_bind,0,pfunction.ORIGIN,10000)',
        '$shutdown_review_ready(S_result,0,pfunction.ORIGIN)',
        'S_result.TODO = (SHUTDOWN_RESULT 0 poperand_sent*) :: eps',
        '$task_nodes(SHUTDOWN_RESULT 0 poperand_sent*) = eps',
        '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_result),HOBJECT n_argument) = 1',
        '$parameter_receive_birth(S_result,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_result,preceivebirth_closed)',
        'S_last = $shutdown_review_pause(S_result,1,pfunction.ORIGIN,10000)',
        '$shutdown_review_ready(S_last,1,pfunction.ORIGIN)',
        'PhpStep: S_last ~> S_queue',
        'S_queue.SHUTDOWN.PHASE = SHUTDOWN_DONE',
        '|S_queue.SHUTDOWN.ENTRIES| = 2',
        '$heap_owners($heap_graph(S_queue),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_queue),HOBJECT n_argument) = 1',
        '$parameter_receive_cache_entry(S_queue,preceivebirth_closed)',
        '$call_descriptors_valid(S_queue)',
        'n_after_receiver = $(n_receiver + 1)',
        'n_receiver_tail = $nabs($(|S_queue.OBJECTS| - n_after_receiver))',
        'S_history = S_queue[.SHUTDOWN.ENTRIES = eps][.SHUTDOWN.INDEX = 0][.OBJECTS = S_queue.OBJECTS[0:n_receiver] ++ [STDINSTANCE] ++ S_queue.OBJECTS[n_after_receiver:n_receiver_tail]]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.SHUTDOWN_ENTRY = (pshutdownreceive[.TARGET = pfunction.ORIGIN])])',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.SHUTDOWN_ENTRY = (pshutdownreceive[.TARGET = HANDLER_METHOD_TARGET b_class porigin_requested ptbytes_method (OUTPUT_BORROWED_TARGET pcalltarget_inner)])])',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.SHUTDOWN_ENTRY = (pshutdownreceive[.LINE = $(-1)])])',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.PUBLICATION = 0])',
        'S_done = $drive(S_queue,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("R|H|L|M|A|E|Z|D|G|")',
    ]
    return checks


def reentry(fixture, path):
    checks = start(fixture, path)
    checks += [
        'pshutdownentry.ARGS = eps',
        'S_bind = $parameter_test_pause(S_warn,0,10000)',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth_parent)',
        'n_child = $(n_receive + 1)',
        '$parameter_receive_birth(S_bind,n_child) = (preceivebirth_child)',
        '~preceivebirth_child.ACTIVE',
        'preceivebirth_child.FUNCTION = pfunction.ORIGIN',
        'preceivebirth_child.ORIGIN = preceivebirth_parent.ORIGIN',
        'preceivebirth_child.CACHE_OWNER = preceivebirth_parent.CACHE_OWNER',
        'preceivebirth_child.SHUTDOWN_ENTRY = eps',
        'preceivebirth_child.CALLSITE = (porigin_child_site)',
        '$parameter_method_call(S_bind,porigin_child_site)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_child)',
        '$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_receive,preceivebirth_child)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PINT 9',
        '$parameter_default_recipient(S_bind,pfunction)',
        '$call_descriptors_valid(S_bind)',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$default_cache_at(S_one.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache_parent)',
        'pdefaultcache_parent.VALUE = PARRAY n_array',
        '$lookup(S_one.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_formal)',
        'S_one.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        'preceivebirth_closed.SHUTDOWN_ENTRY = (pshutdownreceive)',
        '$parameter_receive_cache_entry(S_one,preceivebirth_closed)',
        'S_warm = $shutdown_review_pause(S_one,2,pfunction.ORIGIN,10000)',
        '$shutdown_review_ready(S_warm,2,pfunction.ORIGIN)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.CALLSITE =/= eps',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache_parent)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '$parameter_default_recipient(S_warm,pfunction)',
        '$call_descriptors_valid(S_warm)',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("R|H|M|N|Q|M|E|F|M|E|Z|")',
    ]
    return checks


def factory(fixture, path):
    checks = start(fixture, path)
    checks += [
        'b_class', '~pmethoddesc.STATIC',
        'pcalltarget_inner = SCOPED_TARGET porigin_requested pfunction.ORIGIN porigin_called (n_receiver) poperand_selector',
        'porigin_requested = pmethoddesc.OWNER', 'porigin_called =/= porigin_requested',
        'pcallcontext.LEXICAL_CLASS = (porigin_requested)',
        'pcallcontext.CALLED_CLASS = (porigin_called)',
        'pcallcontext.RECEIVER = (n_receiver)',
        'pshutdownentry.CAPTURE = eps', 'pshutdownentry.PRODUCER = eps',
        '$declaration_cause_owner(S_warn,pshutdownreceive.REGISTRATION) = (pfunction_factory)',
        '$class_method_origin(S_warn.CLASSES,pfunction_factory.ORIGIN) = (pmethoddesc_factory)',
        'pmethoddesc_factory.OWNER = porigin_called',
        'pfunction_factory.ORIGIN =/= pfunction.ORIGIN',
        'S_warn.FRAMES = [pframe_caller]',
        'pframe_caller.CONTEXT = eps',
        'pframe_caller.TODO = [SHUTDOWN_RESULT 0 eps]',
        '$call_context_roots(S_warn.CURRENT) = eps',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_receiver) = 2',
        'S_bind = $parameter_test_pause(S_warn,0,10000)',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_one,preceivebirth_closed)',
        'S_warm = $shutdown_review_pause(S_one,3,pfunction.ORIGIN,10000)',
        '$shutdown_review_ready(S_warm,3,pfunction.ORIGIN)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        '$parameter_shutdown_current(S_warm,pfunction) = (pshutdownreceive_warm)',
        'pshutdownreceive_warm.INDEX = 1',
        'pshutdownreceive_warm.TARGET = pshutdownreceive.TARGET',
        'pshutdownreceive_warm.REGISTRATION =/= pshutdownreceive.REGISTRATION',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'S_bad_index = S_warm[.SHUTDOWN.INDEX = 0]',
        '$parameter_shutdown_current(S_bad_index,pfunction) = eps',
        '~$default_receive_recipient(S_bad_index,pfunction,pdefault)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '$machine_roots(S_warm[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warm)',
        '$call_descriptors_valid(S_warm)',
        'S_history = S_warm[.SHUTDOWN.ENTRIES = eps][.SHUTDOWN.INDEX = 0][.OBJECTS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.SHUTDOWN_ENTRY = (pshutdownreceive[.TARGET = HANDLER_METHOD_TARGET false porigin_requested ptbytes_method pcalltarget_inner])])',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(
            b'F|M|H|Ns202Implicit\\Child202|A|E|Ns202Implicit\\Child202|A|E|D|').decode()) + ')',
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

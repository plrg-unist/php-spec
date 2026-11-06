#!/usr/bin/env python3
"""Check raw method-callable default scopes and real static-source retirement."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_raw_callable_default_review'
SELECTIONS = {'scope': SOURCE / 'inherited-static-alias.php',
    'retirement': SOURCE / 'static-source-retirement.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $raw_review_target(pcalltarget) : bool
def $raw_review_target(ARRAY_METHOD_TARGET pcalltarget parrayselection) = true
def $raw_review_target(STRING_METHOD_TARGET pcalltarget pstringselection) = true
def $raw_review_target(pcalltarget) = false -- otherwise
dec $raw_review_ready(pstate,nat) : bool
def $raw_review_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = STRING_METHOD_TARGET pcalltarget pstringselection
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $raw_review_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = ARRAY_METHOD_TARGET pcalltarget parrayselection
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $raw_review_ready(S,2) = true
  -- if $raw_review_ready(S,1)
  -- if S.CURRENT = (pcallcontext)
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if pcallcontext.CALLED_CLASS = (pmethoddesc.OWNER)
def $raw_review_ready(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = ARRAY_METHOD_TARGET pcalltarget parrayselection
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $raw_review_ready(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if ~$raw_review_target(pcallcontext.TARGET)
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if $default_at(pmethoddesc.FUNCTION.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $raw_review_ready(S,n) = false -- otherwise
dec $raw_review_pause(pstate,nat,nat) : pstate
def $raw_review_pause(S,n_mode,n) = S -- if $raw_review_ready(S,n_mode)
def $raw_review_pause(S,n_mode,n) = $raw_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$raw_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $raw_review_pause(S,n_mode,n) = S -- otherwise
dec $raw_review_output_item(pevent) : ptbytes
def $raw_review_output_item(OUTPUT ptbytes) = ptbytes
def $raw_review_output_item(pevent) = eps -- otherwise
dec $raw_review_output(pevent*) : ptbytes
def $raw_review_output(eps) = eps
def $raw_review_output(pevent :: pevent_tail*) = $raw_review_output_item(pevent) ++ $raw_review_output(pevent_tail*)
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET']


def bound():
    return ['S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$class_method_origin(S_bind.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
        'pmethoddesc.STATIC', 'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext.RECEIVER = eps', 'pcallcontext.INSTANCE = eps',
        'pcallcontext.WRAPPER = eps', 'pcallcontext.CACHE = eps',
        'pcallcontext.CALLSITE = (porigin_site)',
        '$call_selected_valid(S_bind,pcallcontext.TARGET,pcallcontext.CALLSITE)',
        '$target_function(S_bind,pcallcontext.TARGET) = (pfunction)',
        '$call_context_roots(S_bind.CURRENT) = eps',
        '$default_cache_owner(S_bind) = (CACHE_SHARED)',
        '$parameter_default_recipient(S_bind,pfunction)',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE', 'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth.ENTRY = eps', 'preceivebirth.API_ENTRY = eps',
        'preceivebirth.SHUTDOWN_ENTRY = eps', 'preceivebirth.TICK_ENTRY = eps',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        '$parameter_method_invocation(S_bind,pfunction,preceivebirth.CAUSE.CALLS,preceivebirth.PUBLICATION)',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_receive_recipient(S_bind,pfunction,pdefault)',
        '$default_current_cache(S_bind,pdefault.ORIGIN) = eps',
        'S_bind.RESULT = KNOWN (PARRAY n_value)',
        '$default_bind_task_valid(S_bind,pfunction.ORIGIN,0)',
        '$call_descriptors_valid(S_bind)']


def finish(group):
    case = json.loads((SOURCE / 'cases.json').read_text())[SELECTIONS[group].stem]
    value = json.dumps(base64.b64encode(case['stdout'].encode()).decode())
    return ['S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$raw_review_output(S_done.EVENTS) = $base64(' + value + ')',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
        'S_history = S_done[.ENV = eps][.GLOBAL.ENV = eps][.STORE = eps][.OBJECTS = eps][.ARRAYS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.PUBLICATION = 0])']


def scope(fixture, path):
    return start(fixture, path) + [
        'S_bind = $raw_review_pause(S_start[.COMPLETION = NORMAL],0,20000)',
        '$raw_review_ready(S_bind,0)'] + bound() + [
        'pcallcontext.TARGET = STRING_METHOD_TARGET pcalltarget pstringselection',
        'pstringselection.SITE = porigin_site',
        'pcallcontext.CALLED_CLASS = (porigin_child)',
        'porigin_child =/= pmethoddesc.OWNER',
        '$lookup(S_bind.GLOBAL.ENV,$ptascii("callback207")) = (n_callback)',
        'S_bind.STORE[n_callback] = DEFINED pvalue_rebound',
        '$string_bytes(pvalue_rebound) = ($base64("TnMyMDdTY29wZVxDaGlsZDIwNzo6b3RoZXI="))',
        'preceivebirth.CAUSE.CALLS = (pfunction.ORIGIN,pcallcontext.CALLSITE,(pmethoddesc.OWNER),(porigin_child)) :: pdeclcalls',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.CAUSE = preceivebirth.CAUSE[.CALLS = (pfunction.ORIGIN,pcallcontext.CALLSITE,eps,eps) :: pdeclcalls]])',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        'S_warm_child = $raw_review_pause(S_one,1,20000)',
        '$raw_review_ready(S_warm_child,1)',
        'S_warm_child.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.TARGET = ARRAY_METHOD_TARGET pcalltarget_child parrayselection_child',
        'pcallcontext_child.CALLED_CLASS = (porigin_child)',
        'pcallcontext_child.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_child.FUNCTION = pfunction.ORIGIN',
        '$parameter_receive_owner(S_warm_child.CURRENT) = eps',
        '$default_current_cache(S_warm_child,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_value',
        'S_warm_child.ARRAYS[n_value].ITEMS = eps',
        '$default_receive_recipient(S_warm_child,pfunction,pdefault)',
        'S_bad = S_warm_child[.CURRENT = (pcallcontext_child[.NAME = $ptascii("other")])]',
        '~$default_receive_recipient(S_bad,pfunction,pdefault)',
        'S_child_raw = $drive_steps(S_warm_child,1)', 'S_child_raw.COMPLETION = BUDGET',
        'S_warm = $raw_review_pause(S_child_raw[.COMPLETION = NORMAL],2,20000)',
        '$raw_review_ready(S_warm,2)', 'S_warm.CURRENT = (pcallcontext_base)',
        'pcallcontext_base.TARGET = ARRAY_METHOD_TARGET pcalltarget_base parrayselection_base',
        'pcallcontext_base.CALLED_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_base.FUNCTION = pfunction.ORIGIN',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '$call_descriptors_valid(S_warm)'] + finish('scope')


def retirement(fixture, path):
    return start(fixture, path) + [
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],20000)',
        '$dep_ready(S_warn.TODO)',
        '$lookup(S_warn.GLOBAL.ENV,$ptascii("callback207")) = (n_callback)',
        'S_warn.STORE[n_callback] = DEFINED (PARRAY n_source_array)',
        '$entry_lookup(S_warn.ARRAYS[n_source_array].ITEMS,KINT 0) = (DIRECT (POBJECT n_source))',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_source) = 1',
        '$heap_owners($heap_graph(S_warn),HARRAY n_source_array) = 1',
        '$call_context_roots(S_warn.CURRENT) = eps',
        'S_bind = $raw_review_pause(S_warn,3,20000)',
        '$raw_review_ready(S_bind,3)'] + bound() + [
        'pcallcontext.TARGET = ARRAY_METHOD_TARGET pcalltarget parrayselection',
        'parrayselection.REQUESTED = pmethoddesc.OWNER',
        'S_bind.STORE[n_callback] = DEFINED PNULL',
        '~((HOBJECT n_source) <- S_bind.ALLOCATIONS)',
        '~((HARRAY n_source_array) <- S_bind.ALLOCATIONS)',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$raw_review_output(S_bind.EVENTS) = $ptascii("H|D|W|")',
        'S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_one,preceivebirth_closed)',
        'S_warm = $raw_review_pause(S_one,4,20000)',
        '$raw_review_ready(S_warm,4)', 'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        'pcallcontext_warm.RECEIVER = eps',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_value',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        '$call_descriptors_valid(S_warm)'] + finish('retirement') + [
        '$drive(S_one,30000) = S_done', '$drive(S_bind,30000) = S_done']


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
    paths = [Path(__file__), SELECTIONS[args.group], SOURCE / 'cases.json', *modules, *(ROOT / path for path in (
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

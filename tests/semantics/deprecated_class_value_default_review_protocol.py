#!/usr/bin/env python3
"""Check class-value static scopes and source-object retirement."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_class_value_default_review'
SELECTIONS = {'scope': SOURCE / 'inherited-selector.php',
    'retirement': SOURCE / 'object-selector-retirement.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $class_value_review_ready(pstate,nat) : bool
def $class_value_review_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = SCOPED_TARGET porigin_class pcallcontext.FUNCTION porigin_class eps poperand
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $class_value_review_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $parameter_class_value_site(S,porigin_site)
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $class_value_review_ready(S,2) = true
  -- if $class_value_review_ready(S,1)
  -- if S.CURRENT = (pcallcontext)
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if pcallcontext.CALLED_CLASS = (pmethoddesc.OWNER)
def $class_value_review_ready(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if ~$parameter_class_value_site(S,porigin_site)
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if pmethoddesc.STATIC
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $class_value_review_ready(S,n) = false -- otherwise
dec $class_value_review_pause(pstate,nat,nat) : pstate
def $class_value_review_pause(S,n_mode,n) = S -- if $class_value_review_ready(S,n_mode)
def $class_value_review_pause(S,n_mode,n) = $class_value_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$class_value_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $class_value_review_pause(S,n_mode,n) = S -- otherwise
dec $class_value_review_output_item(pevent) : ptbytes
def $class_value_review_output_item(OUTPUT ptbytes) = ptbytes
def $class_value_review_output_item(pevent) = eps -- otherwise
dec $class_value_review_output(pevent*) : ptbytes
def $class_value_review_output(eps) = eps
def $class_value_review_output(pevent :: pevent_tail*) = $class_value_review_output_item(pevent) ++ $class_value_review_output(pevent_tail*)
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET']


def bound():
    return ['S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$class_method_origin(S_bind.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', 'pmethoddesc.STATIC',
        'pcallcontext.CALLSITE = (porigin_site)',
        '$parameter_class_value_site(S_bind,porigin_site)',
        '$parameter_class_value_current(S_bind,pfunction)',
        'pcallcontext.TARGET = SCOPED_TARGET porigin_called pfunction.ORIGIN porigin_called eps (KNOWN pvalue_selector)',
        '$string_bytes(pvalue_selector) = (ptbytes_selector)',
        '$scoped_call_selected(S_bind,pcallcontext.TARGET,porigin_site)',
        'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext.CALLED_CLASS = (porigin_called)',
        'pcallcontext.RECEIVER = eps', '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S_bind.CURRENT) = eps',
        '$default_cache_owner(S_bind) = (CACHE_SHARED)',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE', '~preceivebirth.RAW_ENTRY',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_receive_recipient(S_bind,pfunction,pdefault)',
        '$default_current_cache(S_bind,pdefault.ORIGIN) = eps',
        'S_bind.RESULT = KNOWN (PARRAY n_value)',
        '$default_bind_task_valid(S_bind,pfunction.ORIGIN,0)',
        '$call_descriptors_valid(S_bind)']


def finish(group):
    case = json.loads((SOURCE / 'cases.json').read_text())[SELECTIONS[group].stem]
    expected = json.dumps(base64.b64encode(case['stdout'].encode()).decode())
    return ['S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$class_value_review_output(S_done.EVENTS) = $base64(' + expected + ')',
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_value',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
        'S_history = S_done[.ENV = eps][.GLOBALTABLE = eps][.STORE = eps][.ARRAYS = eps][.OBJECTS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.PUBLICATION = 0])']


def scope(fixture, path):
    return start(fixture, path) + [
        'S_bind = $class_value_review_pause(S_start[.COMPLETION = NORMAL],0,20000)',
        '$class_value_review_ready(S_bind,0)'] + bound() + [
        'pmethoddesc.OWNER =/= porigin_called',
        'S_bind.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("selector209")) = (n_global)',
        'S_bind.STORE[n_global] = DEFINED PNULL',
        '$class_value_review_output(S_bind.EVENTS) = $ptascii("H|")',
        'S_bad_name = S_bind[.CURRENT = (pcallcontext[.NAME = $ptascii("other")])]',
        '~$parameter_class_value_current(S_bad_name,pfunction)',
        '~$default_receive_recipient(S_bad_name,pfunction,pdefault)',
        'S_bad_scope = S_bind[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_called)])]',
        '~$parameter_class_value_current(S_bad_scope,pfunction)',
        'S_bad_selector = S_bind[.CURRENT = (pcallcontext[.TARGET = SCOPED_TARGET porigin_called pfunction.ORIGIN porigin_called eps (KNOWN PNULL)])]',
        '~$parameter_class_value_current(S_bad_selector,pfunction)',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        'S_warm = $class_value_review_pause(S_one,1,20000)',
        '$class_value_review_ready(S_warm,1)', 'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        'pcallcontext_warm.TARGET = pcallcontext.TARGET',
        '$parameter_class_value_current(S_warm,pfunction)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        'S_warm.PARAMETERRECEIVES = S_one.PARAMETERRECEIVES',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_value',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        'S_base = $class_value_review_pause(S_warm,2,20000)',
        '$class_value_review_ready(S_base,2)', 'S_base.CURRENT = (pcallcontext_base)',
        'pcallcontext_base.TARGET = SCOPED_TARGET pmethoddesc.OWNER pfunction.ORIGIN pmethoddesc.OWNER eps poperand_base',
        '$parameter_class_value_current(S_base,pfunction)',
        '$default_current_cache(S_base,pdefault.ORIGIN) = (pdefaultcache)',
        '$parameter_receive_owner(S_base.CURRENT) = eps',
        'preceivebirth_closed.CAUSE.CALLS = (pfunction.ORIGIN,porigin_site_option?,porigin_owner_option?,porigin_called_option?) :: pdeclcalls_tail',
        'porigin_site_option? = pcallcontext.CALLSITE',
        'porigin_owner_option? = pcallcontext.LEXICAL_CLASS',
        'porigin_called_option? = pcallcontext.CALLED_CLASS',
        'porigin_wrong_owner? = pcallcontext.CALLED_CLASS',
        'preceivebirth_bad = preceivebirth_closed[.CAUSE.CALLS = (pfunction.ORIGIN,porigin_site_option?,porigin_wrong_owner?,porigin_called_option?) :: pdeclcalls_tail]',
        '~$parameter_receive_cache_entry(S_base,preceivebirth_bad)'] + finish('scope')


def retirement(fixture, path):
    return start(fixture, path) + [
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],20000)',
        '$dep_ready(S_warn.TODO)',
        'S_warn.GLOBALTABLE = (psymboltable_warn)',
        '$lookup(psymboltable_warn.ENV,$ptascii("selector209")) = (n_global)',
        'S_warn.STORE[n_global] = DEFINED (POBJECT n_source)',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_source) = 1',
        '$call_context_roots(S_warn.CURRENT) = eps',
        'S_bind = $class_value_review_pause(S_warn,0,20000)',
        '$class_value_review_ready(S_bind,0)'] + bound() + [
        'S_bind.STORE[n_global] = DEFINED PNULL',
        '~((HOBJECT n_source) <- S_bind.ALLOCATIONS)',
        '$class_value_review_output(S_bind.EVENTS) = $ptascii("H|D|W|")',
        'S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        'S_warm = $class_value_review_pause(S_one,3,20000)',
        '$class_value_review_ready(S_warm,3)', 'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        '~$parameter_class_value_current(S_warm,pfunction)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_value',
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

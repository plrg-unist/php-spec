#!/usr/bin/env python3
"""Check nullsafe static-source retirement and cold/warm typed defaults."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_nullsafe_default_review'
SELECTIONS = {'retirement': SOURCE / 'static-source-retirement.php',
    'reject': SOURCE / 'typed-cache.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''
dec $nullsafe_review_ready(pstate,nat) : bool
def $nullsafe_review_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = STATIC_METHOD_TARGET porigin_class pcallcontext.FUNCTION
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $nullsafe_review_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n pcallcontext.FUNCTION
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $nullsafe_review_ready(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n pcallcontext.FUNCTION
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $nullsafe_review_ready(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = STATIC_METHOD_TARGET porigin_class pcallcontext.FUNCTION
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if ~$parameter_nullsafe_site(S,porigin_site)
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $nullsafe_review_ready(S,n) = false -- otherwise
dec $nullsafe_review_pause(pstate,nat,nat) : pstate
def $nullsafe_review_pause(S,n_mode,n) = S -- if $nullsafe_review_ready(S,n_mode)
def $nullsafe_review_pause(S,n_mode,n) = $nullsafe_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$nullsafe_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $nullsafe_review_pause(S,n_mode,n) = S -- otherwise
dec $nullsafe_review_output_item(pevent) : ptbytes
def $nullsafe_review_output_item(OUTPUT ptbytes) = ptbytes
def $nullsafe_review_output_item(pevent) = eps -- otherwise
dec $nullsafe_review_output(pevent*) : ptbytes
def $nullsafe_review_output(eps) = eps
def $nullsafe_review_output(pevent :: pevent_tail*) = $nullsafe_review_output_item(pevent) ++ $nullsafe_review_output(pevent_tail*)
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET']


def bound():
    return ['S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$class_method_origin(S_bind.CLASSES,pfunction.ORIGIN) = (pmethoddesc)',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        'pcallcontext.CALLSITE = (porigin_site)',
        '$parameter_nullsafe_site(S_bind,porigin_site)',
        '$parameter_nullsafe_current(S_bind,pfunction)',
        '$method_call_selected(S_bind,pcallcontext.TARGET,pcallcontext.CALLSITE)',
        'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext.INSTANCE = eps', 'pcallcontext.WRAPPER = eps',
        'pcallcontext.CACHE = eps', '$default_cache_owner(S_bind) = (CACHE_SHARED)',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE', '~preceivebirth.RAW_ENTRY',
        'preceivebirth.ENTRY = eps', 'preceivebirth.API_ENTRY = eps',
        'preceivebirth.SHUTDOWN_ENTRY = eps', 'preceivebirth.TICK_ENTRY = eps',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        '~$parameter_receive_raw_witness_valid(S_bind,preceivebirth[.RAW_ENTRY = true])',
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
        '$nullsafe_review_output(S_done.EVENTS) = $base64(' + value + ')',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$machine_roots(S_done[.PARAMETERRECEIVES = eps]) = $machine_roots(S_done)',
        'S_history = S_done[.ENV = eps][.GLOBALTABLE = eps][.STORE = eps][.ARRAYS = eps][.OBJECTS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_history,preceivebirth_closed[.PUBLICATION = 0])']


def retirement(fixture, path):
    return start(fixture, path) + [
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],20000)',
        '$dep_ready(S_warn.TODO)',
        'S_warn.GLOBALTABLE = (psymboltable_warn)',
        '$lookup(psymboltable_warn.ENV,$ptascii("receiver208")) = (n_global)',
        'S_warn.STORE[n_global] = DEFINED (POBJECT n_source)',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_source) = 1',
        '$call_context_roots(S_warn.CURRENT) = eps',
        'S_bind = $nullsafe_review_pause(S_warn,0,20000)',
        '$nullsafe_review_ready(S_bind,0)'] + bound() + [
        'pmethoddesc.STATIC', 'pcallcontext.RECEIVER = eps',
        '$target_nodes(pcallcontext.TARGET) = eps',
        'S_bind.STORE[n_global] = DEFINED PNULL',
        '~((HOBJECT n_source) <- S_bind.ALLOCATIONS)',
        '$nullsafe_review_output(S_bind.EVENTS) = $ptascii("H|D|W|")',
        'S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', '~preceivebirth_closed.RAW_ENTRY',
        'S_warm = $nullsafe_review_pause(S_one,3,20000)',
        '$nullsafe_review_ready(S_warm,3)', 'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        '~$parameter_nullsafe_current(S_warm,pfunction)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_value',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        '$call_descriptors_valid(S_warm)'] + finish('retirement') + [
        '$drive(S_one,30000) = S_done', '$drive(S_bind,30000) = S_done']


def reject(fixture, path):
    return start(fixture, path) + [
        'S_bind = $nullsafe_review_pause(S_start[.COMPLETION = NORMAL],1,20000)',
        '$nullsafe_review_ready(S_bind,1)'] + bound() + [
        '~pmethoddesc.STATIC', 'pcallcontext.RECEIVER = (n_receiver)',
        '$call_context_roots(S_bind.CURRENT) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 2',
        '$typed_parameter_conversion(S_bind,pfunction.SIGNATURE.PARAMETERS[0],PARRAY n_value) = TYPEREJECT',
        '$parameter_default_error_candidate(S_bind,pfunction,0,PARRAY n_value)',
        'PhpStep: S_bind ~> S_reject',
        'S_reject.COMPLETION = THROWN "TypeError" preqbytes_reject z_reject',
        'S_reject.CONSTCONTEXT = eps',
        '$parameter_receive_birth(S_reject,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', '~preceivebirth_closed.RAW_ENTRY',
        '$lookup(S_reject.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_formal)',
        'S_reject.STORE[n_formal] = DEFINED (PARRAY n_value)',
        '(HCELL n_formal) <- $machine_roots(S_reject)',
        '$default_current_cache(S_reject,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_value',
        'S_throw_raw = $drive_steps(S_bind,1)', 'S_throw_raw.COMPLETION = BUDGET',
        'S_throw = S_throw_raw[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_SEARCH n_error) :: eps',
        '$heap_valid($heap_graph(S_throw))', '$call_descriptors_valid(S_throw)',
        'S_warm = $nullsafe_review_pause(S_throw,2,20000)',
        '$nullsafe_review_ready(S_warm,2)', 'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        'pcallcontext_warm.CALLSITE =/= pcallcontext.CALLSITE',
        '$parameter_nullsafe_current(S_warm,pfunction)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        'S_warm.PARAMETERRECEIVES = S_throw.PARAMETERRECEIVES',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        'S_bad = S_warm[.CURRENT = (pcallcontext_warm[.NAME = $ptascii("other")])]',
        '~$default_receive_recipient(S_bad,pfunction,pdefault)',
        'PhpStep: S_warm ~> S_warm_reject',
        'S_warm_reject.COMPLETION = THROWN "TypeError" preqbytes_warm z_warm',
        '$lookup(S_warm_reject.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_formal_warm)',
        'S_warm_reject.STORE[n_formal_warm] = DEFINED (PARRAY n_value)',
        'S_warm_reject.PARAMETERRECEIVES = S_warm.PARAMETERRECEIVES'] + finish('reject')


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

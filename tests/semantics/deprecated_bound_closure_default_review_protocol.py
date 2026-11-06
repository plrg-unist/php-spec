#!/usr/bin/env python3
"""Check one actual bound default receive through source retirement and resumption."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_bound_closure_default_review/cleared-bound-capture.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = ['U = ' + checked['fixture'],
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET', 'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.COMPLETION = NORMAL', 'S_warn.CURRENT = (pcallcontext)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        'pcallcontext.INSTANCE = (n_bound)', 'pcallcontext.TARGET = CLOSURE_TARGET n_bound',
        '$closure_binding_at(S_warn.CLOSUREBINDINGS,n_bound) = (pclosurebinding)',
        'S_warn.CLOSUREBINDINGS = [pclosurebinding]', 'pclosurebinding.SOURCE = n_source',
        'pclosurebinding.LEXICAL = eps /\\ pclosurebinding.CALLED = eps /\\ pclosurebinding.RECEIVER = eps',
        '$closure_binding_source_valid(S_warn,pclosurebinding)', '$closure_binding_api_site(S_warn,pclosurebinding.SITE)',
        '$parameter_closure_binding(S_warn,n_bound)', '$parameter_closure_current(S_warn,pfunction)',
        '$closure_cache_at(S_warn.CLOSURECACHES,n_source) = (pclosurecache_source)',
        'pclosurecache_source.CACHE = (CACHE_SHARED)', 'pclosurecache_source.SCOPE = (BIND_UNSCOPED)',
        '$closure_cache_at(S_warn.CLOSURECACHES,n_bound) = (pclosurecache_bound)',
        'pclosurecache_bound.CACHE = (CACHE_SHARED)', 'pclosurecache_bound.SCOPE = (BIND_UNSCOPED)',
        '~((HOBJECT n_source) <- S_warn.ALLOCATIONS)', '~((HOBJECT n_source) <- $machine_roots(S_warn))',
        '(HOBJECT n_bound) <- $machine_roots(S_warn)',
        'S_warn.OBJECTS[n_bound] = REALCLOSURE pfunction.ORIGIN ([DIRECT (POBJECT n_held)]) eps',
        'hgraph = $heap_graph(S_warn)', '(HOBJECT n_held) <- $heap_reach([HOBJECT n_bound],eps,hgraph.EDGES)',
        '~((HOBJECT n_source) <- $node_children(S_warn,HOBJECT n_bound))',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)', '$default_receive_recipient(S_warn,pfunction,pdefault)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_owner)',
        'S_missing = S_warn[.CLOSURECACHES = $bound_review_without_stamp(S_warn.CLOSURECACHES,n_source)]',
        '$closure_cache_at(S_missing.CLOSURECACHES,n_bound) = (pclosurecache_bound)',
        '~$parameter_closure_binding(S_missing,n_bound)', '~$parameter_closure_selected(S_missing,pfunction)',
        'S_bind = $parameter_test_pause(S_warn,0,10000)', 'S_bind.COMPLETION = NORMAL',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps', 'S_bind.RESULT = KNOWN (PARRAY n_default)',
        '$parameter_closure_current(S_bind,pfunction)', '$call_descriptors_valid(S_bind)',
        '(HOBJECT n_bound) <- $machine_roots(S_bind)',
        'S_budget = $drive_steps(S_bind,0)', 'S_budget.COMPLETION = BUDGET',
        'S_after = $drive_steps(S_budget[.COMPLETION = NORMAL],1)', 'S_after.COMPLETION = BUDGET',
        '$default_cache_at(S_after.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)', 'pdefaultcache.VALUE = PARRAY n_default',
        '$lookup(S_after.ENV,$ptascii("value")) = (n_formal)', 'S_after.STORE[n_formal] = DEFINED (PARRAY n_default)',
        '(HCELL n_formal) <- $machine_roots(S_after)', '(HARRAY n_default) <- $default_cache_roots(S_after.DEFAULTCACHE)',
        '$parameter_receive_birth(S_after,n_owner) = (preceivebirth_closed)', '~preceivebirth_closed.ACTIVE',
        '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
        'S_full = $drive(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
        'S_done = $drive(S_after[.COMPLETION = NORMAL],10000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = S_full.EVENTS', 'S_done.DEFAULTCACHE = S_full.DEFAULTCACHE',
        'S_done.PARAMETERRECEIVES = S_full.PARAMETERRECEIVES', 'S_done.EXITSTATUS = 0', '$call_descriptors_valid(S_done)',
        '~((HOBJECT n_held) <- S_done.ALLOCATIONS)', '~((HOBJECT n_bound) <- S_done.ALLOCATIONS)']
    for mutation in ('.SOURCE = n_bound', '.SOURCE = n_held', '.SITE = pfunction.ORIGIN', '.LEXICAL = (pfunction.ORIGIN)', '.CALLED = (pfunction.ORIGIN)', '.RECEIVER = (n_held)'):
        checks += ['~$parameter_closure_binding(S_warn[.CLOSUREBINDINGS = [pclosurebinding[' + mutation + ']]],n_bound)']
    extra = '''
dec $bound_review_without_stamp(pclosurecache*,nat) : pclosurecache*
def $bound_review_without_stamp(eps,n) = eps
def $bound_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = $bound_review_without_stamp(pclosurecache_tail*,n) -- if pclosurecache.OBJECT = n
def $bound_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = pclosurecache :: $bound_review_without_stamp(pclosurecache_tail*,n) -- if pclosurecache.OBJECT =/= n
'''
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + extra + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, *modules, *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}; head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()

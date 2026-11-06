#!/usr/bin/env python3
"""Check private cache birth keys, value roots and actual quiet/HANDLE storage drop."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_private_closure_default_review'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

EXTRA = r'''
dec $private_review_without_stamp(pclosurecache*,nat) : pclosurecache*
def $private_review_without_stamp(eps,n) = eps
def $private_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = $private_review_without_stamp(pclosurecache_tail*,n) -- if pclosurecache.OBJECT = n
def $private_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = pclosurecache :: $private_review_without_stamp(pclosurecache_tail*,n) -- if pclosurecache.OBJECT =/= n
dec $private_review_ready(pstate,nat,nat,nat,porigin) : bool
def $private_review_ready(S,0,n_owner,n_child,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_child)
  -- if $destructor_method(S,n_child) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
  -- if ~((HOBJECT n_owner) <- S.ALLOCATIONS)
def $private_review_ready(S,1,n_owner,n_child,porigin) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_HANDLE n_owner) :: pdestructionjob*
def $private_review_ready(S,2,n_owner,n_child,porigin) = true
  -- if $private_default_cache_at(S.PRIVATEDEFAULTCACHE,n_owner,porigin) = eps
  -- if ~((HOBJECT n_owner) <- S.ALLOCATIONS)
def $private_review_ready(S,n_mode,n_owner,n_child,porigin) = false -- otherwise
dec $private_review_pause(pstate,nat,nat,nat,porigin,nat) : pstate
def $private_review_pause(S,n_mode,n_owner,n_child,porigin,n) = S -- if $private_review_ready(S,n_mode,n_owner,n_child,porigin)
def $private_review_pause(S,n_mode,n_owner,n_child,porigin,n) = $private_review_pause(S_next[.COMPLETION = NORMAL],n_mode,n_owner,n_child,porigin,$nabs($(n - 1)))
  -- if ~$private_review_ready(S,n_mode,n_owner,n_child,porigin)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $private_review_pause(S,n_mode,n_owner,n_child,porigin,n) = S -- otherwise
'''


def prepare_lifetime(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for tag, name in (('capture', 'cleared-private-capture.php'), ('quiet', 'private-quiet-cache-drop.php')):
            path = SOURCE / name
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            checks += ['U_' + tag + ' = ' + checked['fixture'],
                'S_start_' + tag + ' = $php_run(U_' + tag + ',0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
                'S_start_' + tag + '.COMPLETION = BUDGET',
                'S_warn_' + tag + ' = $dep_pause(S_start_' + tag + '[.COMPLETION = NORMAL],10000)',
                'S_warn_' + tag + '.COMPLETION = NORMAL',
                'S_warn_' + tag + '.CURRENT = (pcallcontext_' + tag + ')',
                'pcallcontext_' + tag + '.INSTANCE = (n_owner_' + tag + ')',
                '$receiving_function(S_warn_' + tag + ',pcallcontext_' + tag + '.FUNCTION) = (pfunction_' + tag + ')',
                '$default_at(pfunction_' + tag + '.DEFAULTS,0) = (pdefault_' + tag + ')',
                '$default_cache_owner(S_warn_' + tag + ') = (CACHE_PRIVATE n_owner_' + tag + ')',
                '$deprecated_parameter_recipient(S_warn_' + tag + ',pfunction_' + tag + ')',
                '$parameter_receive_owner(S_warn_' + tag + '.CURRENT) = (n_receive_' + tag + ')',
                '$parameter_receive_birth(S_warn_' + tag + ',n_receive_' + tag + ') = (preceivebirth_' + tag + ')',
                'preceivebirth_' + tag + '.CACHE_OWNER = (CACHE_PRIVATE n_owner_' + tag + ')',
                '$default_cache_birth_valid(S_warn_' + tag + ',preceivebirth_' + tag + ')',
                'S_bind_' + tag + ' = $parameter_test_pause(S_warn_' + tag + ',0,10000)',
                'S_bind_' + tag + '.COMPLETION = NORMAL',
                'S_bind_' + tag + '.TODO = (DEFAULT_BIND pfunction_' + tag + '.ORIGIN 0) :: eps',
                'S_bind_' + tag + '.RESULT = KNOWN (PARRAY n_array_' + tag + ')',
                'S_budget_' + tag + ' = $drive_steps(S_bind_' + tag + ',0)',
                'S_budget_' + tag + '.COMPLETION = BUDGET',
                'S_cache_' + tag + ' = $drive_steps(S_budget_' + tag + '[.COMPLETION = NORMAL],1)',
                'S_cache_' + tag + '.COMPLETION = BUDGET',
                'S_cache_' + tag + '.PRIVATEDEFAULTCACHE = [pprivatecache_' + tag + ']',
                'pprivatecache_' + tag + '.OWNER = n_owner_' + tag,
                'pprivatecache_' + tag + '.ENTRY.ORIGIN = pdefault_' + tag + '.ORIGIN',
                'pprivatecache_' + tag + '.ENTRY.VALUE = PARRAY n_array_' + tag,
                'pprivatecache_' + tag + '.ENTRY.CLASS = PVARRAY true eps',
                'S_cache_' + tag + '.ARRAYS[n_array_' + tag + '].ITEMS = eps',
                '$private_default_cache_roots(S_cache_' + tag + '.PRIVATEDEFAULTCACHE) = [HARRAY n_array_' + tag + ']',
                '$private_default_caches_valid(S_cache_' + tag + ',S_cache_' + tag + '.PRIVATEDEFAULTCACHE)',
                'S_cache_' + tag + '.DEFAULTCACHE = eps',
                '$lookup(S_cache_' + tag + '.ENV,$ptascii("value")) = (n_formal_' + tag + ')',
                'S_cache_' + tag + '.STORE[n_formal_' + tag + '] = DEFINED (PARRAY n_array_' + tag + ')',
                '(HCELL n_formal_' + tag + ') <- $machine_roots(S_cache_' + tag + ')',
                '$call_descriptors_valid(S_cache_' + tag + ')',
                '$heap_valid($heap_graph(S_cache_' + tag + '))']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks += [
        'S_warn_capture.OBJECTS[n_owner_capture] = REALCLOSURE pfunction_capture.ORIGIN ([DIRECT (POBJECT n_child)]) eps',
        '$closure_binding_at(S_warn_capture.CLOSUREBINDINGS,n_owner_capture) = (pclosurebinding)',
        'pclosurebinding.SOURCE = n_source', 'n_source =/= n_owner_capture',
        '~((HOBJECT n_source) <- S_warn_capture.ALLOCATIONS)',
        '$private_default_cache_at(S_cache_capture.PRIVATEDEFAULTCACHE,n_source,pdefault_capture.ORIGIN) = eps',
        'S_unknown = S_cache_capture[.CLOSURECACHES = $private_review_without_stamp(S_cache_capture.CLOSURECACHES,n_owner_capture)]',
        '$closure_cache_first(S_unknown.CLOSURECACHES,pfunction_capture.ORIGIN) =/= eps',
        '$default_cache_owner(S_unknown) = eps',
        '~$private_default_caches_valid(S_unknown,S_unknown.PRIVATEDEFAULTCACHE)',
        'S_false_birth = S_warn_capture[.PARAMETERRECEIVES = [preceivebirth_capture[.CACHE_OWNER = (CACHE_SHARED)]]]',
        '~$parameter_receive_context_valid(S_false_birth,S_false_birth.CURRENT)',
        '~$private_default_caches_valid(S_cache_capture,[pprivatecache_capture,pprivatecache_capture])',
        '~$private_default_caches_valid(S_cache_capture,[pprivatecache_capture[.OWNER = n_child]])',
        '~$private_default_caches_valid(S_cache_capture,[pprivatecache_capture[.ENTRY.CLASS = PVARRAY false eps]])',
        'S_child = $private_review_pause(S_cache_capture[.COMPLETION = NORMAL],0,n_owner_capture,n_child,pdefault_capture.ORIGIN,10000)',
        'S_child.COMPLETION = NORMAL',
        '$private_review_ready(S_child,0,n_owner_capture,n_child,pdefault_capture.ORIGIN)',
        '~((HOBJECT n_owner_capture) <- S_child.ALLOCATIONS)',
        '~((HOBJECT n_owner_capture) <- $machine_roots(S_child))',
        '$gc_retired_valid(S_child,n_owner_capture)',
        '$private_default_cache_at(S_child.PRIVATEDEFAULTCACHE,n_owner_capture,pdefault_capture.ORIGIN) = (pprivatecache_capture.ENTRY)',
        '$private_default_caches_valid(S_child,S_child.PRIVATEDEFAULTCACHE)',
        '$private_default_cache_roots(S_child.PRIVATEDEFAULTCACHE) = [HARRAY n_array_capture]',
        '$parameter_receive_birth(S_child,n_receive_capture) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.CACHE_OWNER = (CACHE_PRIVATE n_owner_capture)',
        '$default_cache_birth_valid(S_child,preceivebirth_closed)', '$call_descriptors_valid(S_child)',
        'S_handle = $private_review_pause(S_child,1,n_owner_capture,n_child,pdefault_capture.ORIGIN,10000)',
        'S_handle.COMPLETION = NORMAL',
        'S_handle.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_handle*',
        'pdestructionrelease.JOBS = (DESTRUCTION_HANDLE n_owner_capture) :: pdestructionjob_handle*',
        '$destructor_release_valid(S_handle,pdestructionrelease)',
        '$gc_retired_valid(S_handle,n_owner_capture)',
        '$private_default_caches_valid(S_handle,S_handle.PRIVATEDEFAULTCACHE)',
        'S_drop = $drive_steps(S_handle,1)', 'S_drop.COMPLETION = BUDGET',
        'S_drop.PRIVATEDEFAULTCACHE = eps',
        'S_drop.DEFAULTCACHE = S_handle.DEFAULTCACHE',
        'S_drop.CLASSCONSTANTCACHE = S_handle.CLASSCONSTANTCACHE',
        '$closure_cache_at(S_drop.CLOSURECACHES,n_owner_capture) = (pclosurecache_retired)',
        'pclosurecache_retired.CACHE = (CACHE_PRIVATE n_owner_capture)',
        '~$private_default_caches_valid(S_drop,S_handle.PRIVATEDEFAULTCACHE)',
        '$parameter_receive_birth(S_drop,n_receive_capture) = (preceivebirth_closed)',
        'S_done_capture = $drive_steps(S_drop[.COMPLETION = NORMAL],10000)',
        'S_done_capture.COMPLETION = NORMAL', '$call_descriptors_valid(S_done_capture)',
        'S_full_capture = $drive_steps(S_bind_capture,10000)',
        'S_full_capture.COMPLETION = NORMAL',
        'S_done_capture.EVENTS = S_full_capture.EVENTS',
        'S_done_capture.PRIVATEDEFAULTCACHE = S_full_capture.PRIVATEDEFAULTCACHE',
        'S_quiet = $private_review_pause(S_cache_quiet[.COMPLETION = NORMAL],2,n_owner_quiet,0,pdefault_quiet.ORIGIN,10000)',
        'S_quiet.COMPLETION = NORMAL',
        '$private_review_ready(S_quiet,2,n_owner_quiet,0,pdefault_quiet.ORIGIN)',
        'S_quiet.PRIVATEDEFAULTCACHE = eps',
        '~$gc_retired_valid(S_quiet,n_owner_quiet)',
        '$default_cache_birth_valid(S_quiet,preceivebirth_quiet)',
        '$closure_cache_at(S_quiet.CLOSURECACHES,n_owner_quiet) = (pclosurecache_quiet)',
        'pclosurecache_quiet.CACHE = (CACHE_PRIVATE n_owner_quiet)',
        '$call_descriptors_valid(S_quiet)',
        'S_done_quiet = $drive_steps(S_quiet,10000)', 'S_done_quiet.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_done_quiet)']
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


REENTRY = ('private-owned-reentry-empty', 'private-owned-other-cache', 'private-owned-retired-other-cache')


def prepare_reentry(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for tag, name in zip(('same', 'other', 'retired'), REENTRY):
            path = SOURCE.parent / 'deprecated_global_constant' / (name + '.php')
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            local = [
                'U = ' + checked['fixture'],
                'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
                'S_start.COMPLETION = BUDGET',
                'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
                'S_warn.COMPLETION = NORMAL',
                '$parameter_receive_owner(S_warn.CURRENT) = (n_parent)',
                'S_bind = $parameter_test_pause(S_warn,0,10000)', 'S_bind.COMPLETION = NORMAL',
                'S_bind.TODO = (DEFAULT_BIND porigin 0) :: eps',
                'S_bind.CURRENT = (pcallcontext)', 'pcallcontext.INSTANCE = (n_outer)',
                '$parameter_receive_birth(S_bind,n_parent) = (preceivebirth_parent)',
                'preceivebirth_parent.ACTIVE',
                'preceivebirth_parent.CACHE_OWNER = (CACHE_PRIVATE n_outer)',
                '$parameter_receive_latest(S_bind.PARAMETERRECEIVES,(n_parent),1,eps) = (n_child)',
                '$parameter_receive_birth(S_bind,n_child) = (preceivebirth_child)',
                '~preceivebirth_child.ACTIVE', 'preceivebirth_child.PARENT = (n_parent)',
                'preceivebirth_child.FUNCTION = preceivebirth_parent.FUNCTION',
                'preceivebirth_child.ORIGIN = preceivebirth_parent.ORIGIN',
                'preceivebirth_child.CACHE_OWNER = (CACHE_PRIVATE n_inner)',
                '$parameter_receive_source_valid(S_bind,preceivebirth_child)',
                '$default_cache_birth_valid(S_bind,preceivebirth_child)',
                '$receiving_function(S_bind,porigin) = (pfunction)',
                '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
                '$default_pending_cache_valid(S_bind,pdefault)', '$call_descriptors_valid(S_bind)',
            ]
            if tag == 'same':
                local += ['n_inner = n_outer',
                    '$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_parent,preceivebirth_child)',
                    '$default_current_cache(S_bind,pdefault.ORIGIN) = (pdefaultcache)',
                    'pdefaultcache.VALUE = PINT 9',
                    'preceivebirth_wrong = preceivebirth_child[.CACHE_OWNER = (CACHE_SHARED)]',
                    '$parameter_receive_source_valid(S_bind,preceivebirth_wrong)',
                    '$default_cache_birth_valid(S_bind,preceivebirth_wrong)',
                    '~$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_parent,preceivebirth_wrong)',
                    '~$parameter_receive_cache_child(S_bind,preceivebirth_parent[.CACHE_OWNER = eps],n_parent,preceivebirth_child)',
                    '~$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_parent,preceivebirth_child[.CACHE_OWNER = eps])']
            else:
                local += ['n_inner =/= n_outer',
                    '~$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_parent,preceivebirth_child)',
                    '$default_current_cache(S_bind,pdefault.ORIGIN) = eps']
                if tag == 'other':
                    local += ['(HOBJECT n_inner) <- S_bind.ALLOCATIONS',
                        '$private_default_cache_at(S_bind.PRIVATEDEFAULTCACHE,n_inner,pdefault.ORIGIN) = (pdefaultcache)',
                        'pdefaultcache.VALUE = PINT 9',
                        'S_forged = S_bind[.PRIVATEDEFAULTCACHE = {OWNER n_outer,ENTRY pdefaultcache} :: S_bind.PRIVATEDEFAULTCACHE]',
                        '$private_default_caches_valid(S_forged,S_forged.PRIVATEDEFAULTCACHE)',
                        '~$default_pending_cache_valid(S_forged,pdefault)']
                else:
                    local += ['~((HOBJECT n_inner) <- S_bind.ALLOCATIONS)',
                        '~$gc_retired_valid(S_bind,n_inner)',
                        '$private_default_cache_at(S_bind.PRIVATEDEFAULTCACHE,n_inner,pdefault.ORIGIN) = eps',
                        '$closure_cache_at(S_bind.CLOSURECACHES,n_inner) = (pclosurecache)',
                        'pclosurecache.CACHE = (CACHE_PRIVATE n_inner)']
            local += ['S_bind.RESULT = KNOWN (PARRAY n_array)',
                'S_after = $drive_steps(S_bind,1)', 'S_after.COMPLETION = BUDGET',
                '$private_default_cache_at(S_after.PRIVATEDEFAULTCACHE,n_outer,pdefault.ORIGIN) = (pdefaultcache_outer)',
                'pdefaultcache_outer.VALUE = PARRAY n_array', 'pdefaultcache_outer.CLASS = PVARRAY true eps',
                '$private_default_caches_valid(S_after,S_after.PRIVATEDEFAULTCACHE)',
                '$call_descriptors_valid(S_after)', 'S_after.DEFAULTCACHE = eps']
            # Give each source's fixture variables distinct names in one checked main.
            import re
            checks += [re.sub(r'\b(?:U|S_[a-z_]+|pcallcontext|preceivebirth_[a-z_]+|n_[a-z_]+|pfunction|pdefault|pdefaultcache(?:_[a-z_]+)?|pclosurecache|porigin)\b', lambda m: m.group() + '_' + tag, check) for check in local]
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', choices=('lifetime', 'reentry'), default='lifetime')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    sources = [SOURCE / 'cleared-private-capture.php', SOURCE / 'private-quiet-cache-drop.php'] if args.group == 'lifetime' else [SOURCE.parent / 'deprecated_global_constant' / (name + '.php') for name in REENTRY]
    paths = [Path(__file__), *sources, *modules, *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}; head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare_lifetime(out) if args.group == 'lifetime' else prepare_reentry(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Check actual scoped recipients and capture/static/cache/This storage order."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess

from deprecated_parameter_default_protocol import PREFIX
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_scoped_closure_default_review'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTIONS = {
    'frontier': ('capture-static-before-this',),
    'reentry': ('this-destructor-reenters-private-copy',),
    'receiver_free': ('receiver-free-private-clone', 'inherited-receiver-free-scope', 'receiver-free-private-capture'),
}

EXTRA = r'''
dec $scoped_review_without_stamp(pclosurecache*,nat) : pclosurecache*
def $scoped_review_without_stamp(eps,n) = eps
def $scoped_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = $scoped_review_without_stamp(pclosurecache_tail*,n)
  -- if pclosurecache.OBJECT = n
def $scoped_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = pclosurecache :: $scoped_review_without_stamp(pclosurecache_tail*,n)
  -- if pclosurecache.OBJECT =/= n
dec $scoped_review_ready(pstate,nat,nat,nat,porigin) : bool
def $scoped_review_ready(S,0,n_owner,n_object,porigin) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_PRIVATE_CACHE n_owner) :: pdestructionjob*
def $scoped_review_ready(S,1,n_owner,n_object,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_object)
  -- if $destructor_method(S,n_object) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $scoped_review_ready(S,2,n_owner,n_object,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_static)
  -- if $(n_static < |S.OBJECTS|)
  -- if S.OBJECTS[n_static] = INSTANCE porigin_static
  -- if $class_at(S.CLASSES,porigin_static) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Static192")
  -- if $destructor_method(S,n_static) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $scoped_review_ready(S,3,n_owner,n_object,porigin) = true
  -- if ~((HOBJECT n_owner) <- S.ALLOCATIONS)
  -- if ~$gc_retired_valid(S,n_owner)
  -- if $private_default_cache_at(S.PRIVATEDEFAULTCACHE,n_object,porigin) =/= eps
def $scoped_review_ready(S,4,n_owner,n_object,porigin) = true
  -- if ~((HOBJECT n_owner) <- S.ALLOCATIONS)
  -- if ~$gc_retired_valid(S,n_owner)
  -- if $private_default_cache_at(S.PRIVATEDEFAULTCACHE,n_owner,porigin) = eps
def $scoped_review_ready(S,n_mode,n_owner,n_object,porigin) = false -- otherwise
dec $scoped_review_pause(pstate,nat,nat,nat,porigin,nat) : pstate
def $scoped_review_pause(S,n_mode,n_owner,n_object,porigin,n) = S
  -- if $scoped_review_ready(S,n_mode,n_owner,n_object,porigin)
def $scoped_review_pause(S,n_mode,n_owner,n_object,porigin,n) = $scoped_review_pause(S_next[.COMPLETION = NORMAL],n_mode,n_owner,n_object,porigin,$nabs($(n - 1)))
  -- if ~$scoped_review_ready(S,n_mode,n_owner,n_object,porigin)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $scoped_review_pause(S,n_mode,n_owner,n_object,porigin,n) = S -- otherwise
'''


def scoped(checks, tag):
    pattern = r'\b(?:U|S_[a-z_]+|n_[a-z_]+|pcallcontext(?:_[a-z_]+)?|pfunction|pdefault|pprivatecache|pclosurecache(?:_[a-z_]+)?|pclosurebinding|pclosurescope|preceivebirth(?:_[a-z_]+)?|pdestructionrelease|pdestructionjob_[a-z_]+|ptask_[a-z_]+)\b'
    return [re.sub(pattern, lambda match: match.group() + '_' + tag, check) for check in checks]


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)', 'S_warn.COMPLETION = NORMAL',
        'S_warn.CURRENT = (pcallcontext)', 'pcallcontext.INSTANCE = (n_owner)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_owner', 'pcallcontext.CACHE = eps',
        'pcallcontext.LEXICAL_CLASS =/= eps',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        '$parameter_scoped_current(S_warn,pfunction)', '$parameter_scoped_record(S_warn,n_owner)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        '$default_cache_birth_valid(S_warn,preceivebirth)',
        'S_missing = S_warn[.CLOSURECACHES = $scoped_review_without_stamp(S_warn.CLOSURECACHES,n_owner)]',
        '$default_cache_owner(S_missing) = eps', '~$parameter_scoped_current(S_missing,pfunction)',
        '~$parameter_scoped_current(S_warn[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])],pfunction)',
        '~$parameter_scoped_current(S_warn[.CURRENT = (pcallcontext[.RECEIVER = (n_owner)])],pfunction)']


def private_start(fixture, path):
    return start(fixture, path) + [
        '$default_cache_owner(S_warn) = (CACHE_PRIVATE n_owner)',
        'preceivebirth.CACHE_OWNER = (CACHE_PRIVATE n_owner)',
        '$closure_binding_at(S_warn.CLOSUREBINDINGS,n_owner) = (pclosurebinding)',
        'pclosurebinding.SOURCE = n_source', '~((HOBJECT n_source) <- S_warn.ALLOCATIONS)',
        'pcallcontext.LEXICAL_CLASS = pclosurebinding.LEXICAL',
        'pcallcontext.CALLED_CLASS = pclosurebinding.CALLED',
        'pcallcontext.RECEIVER = pclosurebinding.RECEIVER',
        '$scoped_private_cache_owner(S_warn,n_owner)',
        'S_bind = $parameter_test_pause(S_warn,0,10000)', 'S_bind.COMPLETION = NORMAL',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)']


def cache_checks():
    return ['S_cache.COMPLETION = BUDGET', 'S_cache.PRIVATEDEFAULTCACHE = [pprivatecache]',
        'pprivatecache.OWNER = n_owner', 'pprivatecache.ENTRY.ORIGIN = pdefault.ORIGIN',
        'pprivatecache.ENTRY.VALUE = PARRAY n_array', 'pprivatecache.ENTRY.CLASS = PVARRAY true eps',
        '$private_default_caches_valid(S_cache,S_cache.PRIVATEDEFAULTCACHE)',
        '$private_default_cache_roots(S_cache.PRIVATEDEFAULTCACHE) = [HARRAY n_array]',
        '$lookup(S_cache.ENV,$ptascii("value")) = (n_formal)',
        'S_cache.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '(HCELL n_formal) <- $machine_roots(S_cache)', '$call_descriptors_valid(S_cache)',
        '~$private_default_caches_valid(S_cache,[pprivatecache,pprivatecache])']


def frontier(fixture, path):
    checks = private_start(fixture, path) + [
        'pcallcontext.RECEIVER = (n_this)', 'pcallcontext.LEXICAL_CLASS =/= pcallcontext.CALLED_CLASS',
        '~$parameter_scoped_current(S_warn[.CURRENT = (pcallcontext[.LEXICAL_CLASS = pcallcontext.CALLED_CLASS])],pfunction)',
        '(HOBJECT n_owner) <- $machine_roots(S_warn)',
        '(HOBJECT n_this) <- $node_children(S_warn,HOBJECT n_owner)',
        'S_warn.OBJECTS[n_owner] = REALCLOSURE pfunction.ORIGIN ([DIRECT (POBJECT n_capture)]) pstaticcell_initial*',
        '(HOBJECT n_capture) <- $node_children(S_warn,HOBJECT n_owner)',
        'S_budget = $drive_steps(S_bind,0)', 'S_budget.COMPLETION = BUDGET',
        'S_cache = $drive_steps(S_budget[.COMPLETION = NORMAL],1)'] + cache_checks() + [
        'S_capture = $scoped_review_pause(S_cache[.COMPLETION = NORMAL],1,n_owner,n_capture,pdefault.ORIGIN,10000)',
        'S_capture.COMPLETION = NORMAL', '$scoped_review_ready(S_capture,1,n_owner,n_capture,pdefault.ORIGIN)',
        '~((HOBJECT n_owner) <- S_capture.ALLOCATIONS)', '~((HOBJECT n_owner) <- $machine_roots(S_capture))',
        '$gc_retired_valid(S_capture,n_owner)',
        '$scoped_cache_releases(S_capture,S_capture.DESTRUCTION.RELEASES,n_owner)',
        '$private_default_caches_valid(S_capture,S_capture.PRIVATEDEFAULTCACHE)',
        '$private_default_cache_at(S_capture.PRIVATEDEFAULTCACHE,n_owner,pdefault.ORIGIN) = (pprivatecache.ENTRY)',
        'S_static = $scoped_review_pause(S_capture,2,n_owner,0,pdefault.ORIGIN,10000)',
        'S_static.COMPLETION = NORMAL', '$scoped_review_ready(S_static,2,n_owner,0,pdefault.ORIGIN)',
        '$private_default_caches_valid(S_static,S_static.PRIVATEDEFAULTCACHE)',
        '(HOBJECT n_this) <- S_static.ALLOCATIONS',
        'S_marker = $scoped_review_pause(S_static,0,n_owner,0,pdefault.ORIGIN,10000)',
        'S_marker.COMPLETION = NORMAL',
        'S_marker.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_marker*',
        'pdestructionrelease.JOBS = (DESTRUCTION_PRIVATE_CACHE n_owner) :: (DESTRUCTION_VALUE (HOBJECT n_this)) :: (DESTRUCTION_HANDLE n_owner) :: pdestructionjob_tail*',
        '$destructor_release_valid(S_marker,pdestructionrelease)',
        '$destruction_job_nodes([DESTRUCTION_PRIVATE_CACHE n_owner]) = eps',
        '$gc_temporary_nodes([DESTRUCTION_PRIVATE_CACHE n_owner]) = eps',
        '$private_default_caches_valid(S_marker,S_marker.PRIVATEDEFAULTCACHE)',
        'S_drop = $drive_steps(S_marker,1)', 'S_drop.COMPLETION = BUDGET',
        'S_drop.PRIVATEDEFAULTCACHE = eps', '$gc_retired_valid(S_drop,n_owner)',
        '~$private_default_cache_retired(S_drop,n_owner)',
        '~$private_default_caches_valid(S_drop,[pprivatecache])',
        'S_drop.DEFAULTCACHE = S_marker.DEFAULTCACHE', 'S_drop.CALLDEFAULTCACHE = S_marker.CALLDEFAULTCACHE',
        'S_drop.CLASSCONSTANTCACHE = S_marker.CLASSCONSTANTCACHE',
        'S_this = $scoped_review_pause(S_drop[.COMPLETION = NORMAL],1,n_owner,n_this,pdefault.ORIGIN,10000)',
        'S_this.COMPLETION = NORMAL', '$scoped_review_ready(S_this,1,n_owner,n_this,pdefault.ORIGIN)',
        'S_this.PRIVATEDEFAULTCACHE = eps', '$gc_retired_valid(S_this,n_owner)',
        '~$private_default_caches_valid(S_this,[pprivatecache])',
        '$parameter_receive_birth(S_this,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', '$default_cache_birth_valid(S_this,preceivebirth_closed)',
        '$call_descriptors_valid(S_this)',
        'S_done = $drive_steps(S_this,10000)', 'S_done.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_done)', 'S_done.PRIVATEDEFAULTCACHE = eps',
        'S_full = $drive_steps(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
        'S_done.EVENTS = S_full.EVENTS', 'S_done.PRIVATEDEFAULTCACHE = S_full.PRIVATEDEFAULTCACHE']
    return checks


def reentry(fixture, path):
    return private_start(fixture, path) + ['pcallcontext.RECEIVER = (n_this)',
        'S_cache = $drive_steps(S_bind,1)'] + cache_checks() + [
        'S_this = $scoped_review_pause(S_cache[.COMPLETION = NORMAL],1,n_owner,n_this,pdefault.ORIGIN,10000)',
        'S_this.COMPLETION = NORMAL', '$scoped_review_ready(S_this,1,n_owner,n_this,pdefault.ORIGIN)',
        '$gc_retired_valid(S_this,n_owner)', '~$private_default_cache_retired(S_this,n_owner)',
        '$private_default_cache_at(S_this.PRIVATEDEFAULTCACHE,n_owner,pdefault.ORIGIN) = eps',
        '~$private_default_caches_valid(S_this,[pprivatecache])',
        'S_inner = $dep_pause(S_this,10000)', 'S_inner.COMPLETION = NORMAL',
        'S_inner.CURRENT = (pcallcontext_inner)', 'pcallcontext_inner.INSTANCE = (n_other)', 'n_other =/= n_owner',
        '$parameter_scoped_current(S_inner,pfunction)', '$default_cache_owner(S_inner) = (CACHE_PRIVATE n_other)',
        '$closure_binding_at(S_inner.CLOSUREBINDINGS,n_other) = (pclosurebinding_other)',
        'pclosurebinding_other.SOURCE = n_owner', '~((HOBJECT n_owner) <- S_inner.ALLOCATIONS)',
        '~((HOBJECT n_owner) <- $machine_roots(S_inner))',
        '$closure_cache_at(S_inner.CLOSURECACHES,n_other) = (pclosurecache_other)',
        'pclosurecache_other.CACHE = (CACHE_PRIVATE n_other)',
        '$default_current_cache(S_inner,pdefault.ORIGIN) = eps',
        '$gc_retired_valid(S_inner,n_owner)', '~$private_default_caches_valid(S_inner,[pprivatecache])',
        '$parameter_receive_birth(S_inner,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', '$default_cache_birth_valid(S_inner,preceivebirth_closed)',
        'S_inner_bind = $parameter_test_pause(S_inner,0,10000)', 'S_inner_bind.COMPLETION = NORMAL',
        'S_inner_after = $drive_steps(S_inner_bind,1)', 'S_inner_after.COMPLETION = BUDGET',
        '$private_default_cache_at(S_inner_after.PRIVATEDEFAULTCACHE,n_other,pdefault.ORIGIN) = (pdefaultcache_other)',
        'pdefaultcache_other.VALUE = pprivatecache.ENTRY.VALUE',
        '$private_default_cache_at(S_inner_after.PRIVATEDEFAULTCACHE,n_owner,pdefault.ORIGIN) = eps',
        '$private_default_caches_valid(S_inner_after,S_inner_after.PRIVATEDEFAULTCACHE)',
        'S_old_gone = $scoped_review_pause(S_inner_after[.COMPLETION = NORMAL],3,n_owner,n_other,pdefault.ORIGIN,10000)',
        'S_old_gone.COMPLETION = NORMAL', '$scoped_review_ready(S_old_gone,3,n_owner,n_other,pdefault.ORIGIN)',
        '$private_default_cache_at(S_old_gone.PRIVATEDEFAULTCACHE,n_other,pdefault.ORIGIN) = (pdefaultcache_other)',
        '$call_descriptors_valid(S_old_gone)',
        'S_done = $drive_steps(S_old_gone,10000)', 'S_done.COMPLETION = NORMAL',
        'S_done.PRIVATEDEFAULTCACHE = eps', '$call_descriptors_valid(S_done)']


def receiver_free(fixture, path):
    if path.stem == 'inherited-receiver-free-scope':
        return start(fixture, path) + ['pcallcontext.RECEIVER = eps',
            'pcallcontext.LEXICAL_CLASS =/= pcallcontext.CALLED_CLASS',
            '$default_cache_owner(S_warn) = (CACHE_SHARED)',
            '$closure_scope_at(S_warn.CLOSURESCOPES,n_owner) = (pclosurescope)',
            'pclosurescope.RECEIVER = eps', 'pclosurescope.CALLED =/= pclosurescope.LEXICAL',
            '$closure_scope_row_valid(S_warn,pclosurescope)',
            '~$parameter_scoped_current(S_warn[.CURRENT = (pcallcontext[.CALLED_CLASS = pcallcontext.LEXICAL_CLASS])],pfunction)',
            '~$parameter_scoped_current(S_warn[.CLOSURESCOPES = eps],pfunction)',
            'S_done = $drive_steps(S_warn,10000)', 'S_done.COMPLETION = NORMAL',
            '$default_cache_at(S_done.DEFAULTCACHE,pdefault.ORIGIN) =/= eps',
            'S_done.PRIVATEDEFAULTCACHE = eps', '$call_descriptors_valid(S_done)']
    if path.stem == 'receiver-free-private-capture':
        return private_start(fixture, path) + ['pcallcontext.RECEIVER = eps',
            'S_warn.OBJECTS[n_owner] = REALCLOSURE pfunction.ORIGIN ([DIRECT (POBJECT n_capture)]) eps',
            'S_cache = $drive_steps(S_bind,1)'] + cache_checks() + [
            'S_capture = $scoped_review_pause(S_cache[.COMPLETION = NORMAL],1,n_owner,n_capture,pdefault.ORIGIN,10000)',
            'S_capture.COMPLETION = NORMAL', '$scoped_review_ready(S_capture,1,n_owner,n_capture,pdefault.ORIGIN)',
            '$gc_retired_valid(S_capture,n_owner)',
            '$private_default_caches_valid(S_capture,S_capture.PRIVATEDEFAULTCACHE)',
            'S_marker = $scoped_review_pause(S_capture,0,n_owner,0,pdefault.ORIGIN,10000)',
            'S_marker.COMPLETION = NORMAL',
            'S_marker.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_marker*',
            'pdestructionrelease.JOBS = (DESTRUCTION_PRIVATE_CACHE n_owner) :: (DESTRUCTION_HANDLE n_owner) :: pdestructionjob_tail*',
            '$destructor_release_valid(S_marker,pdestructionrelease)',
            'S_drop = $drive_steps(S_marker,1)', 'S_drop.COMPLETION = BUDGET',
            'S_drop.PRIVATEDEFAULTCACHE = eps', '$gc_retired_valid(S_drop,n_owner)',
            '~$private_default_cache_retired(S_drop,n_owner)',
            '~$private_default_caches_valid(S_drop,[pprivatecache])',
            '$parameter_receive_birth(S_drop,n_receive) = (preceivebirth_closed)',
            '$default_cache_birth_valid(S_drop,preceivebirth_closed)',
            'S_done = $drive_steps(S_drop[.COMPLETION = NORMAL],10000)',
            'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)']
    return private_start(fixture, path) + ['pcallcontext.RECEIVER = eps',
        'pcallcontext.CALLED_CLASS = pcallcontext.LEXICAL_CLASS',
        '$node_children(S_warn,HOBJECT n_owner) = eps',
        'S_cache = $drive_steps(S_bind,1)'] + cache_checks() + [
        'S_quiet = $scoped_review_pause(S_cache[.COMPLETION = NORMAL],4,n_owner,0,pdefault.ORIGIN,10000)',
        'S_quiet.COMPLETION = NORMAL', '$scoped_review_ready(S_quiet,4,n_owner,0,pdefault.ORIGIN)',
        '~$private_default_caches_valid(S_quiet,[pprivatecache])',
        '$lookup(S_quiet.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_quiet.STORE[n_copy_cell] = DEFINED (POBJECT n_copy)',
        '$node_children(S_quiet,HOBJECT n_copy) = eps',
        '$private_default_cache_at(S_quiet.PRIVATEDEFAULTCACHE,n_copy,pdefault.ORIGIN) = eps',
        'S_copy_warn = $dep_pause(S_quiet,10000)', 'S_copy_warn.COMPLETION = NORMAL',
        '$default_cache_owner(S_copy_warn) = (CACHE_PRIVATE n_copy)',
        '$default_current_cache(S_copy_warn,pdefault.ORIGIN) = eps',
        'S_copy_bind = $parameter_test_pause(S_copy_warn,0,10000)', 'S_copy_bind.COMPLETION = NORMAL',
        'S_copy_after = $drive_steps(S_copy_bind,1)', 'S_copy_after.COMPLETION = BUDGET',
        '$private_default_cache_at(S_copy_after.PRIVATEDEFAULTCACHE,n_copy,pdefault.ORIGIN) = (pdefaultcache_copy)',
        'pdefaultcache_copy.VALUE = pprivatecache.ENTRY.VALUE',
        '$private_default_caches_valid(S_copy_after,S_copy_after.PRIVATEDEFAULTCACHE)',
        'S_copy_drop = $scoped_review_pause(S_copy_after[.COMPLETION = NORMAL],4,n_copy,0,pdefault.ORIGIN,10000)',
        'S_copy_drop.COMPLETION = NORMAL', '$scoped_review_ready(S_copy_drop,4,n_copy,0,pdefault.ORIGIN)',
        '~$private_default_cache_retired(S_copy_drop,n_copy)',
        '~$private_default_caches_valid(S_copy_drop,[{OWNER n_copy,ENTRY pdefaultcache_copy}])',
        'S_done = $drive_steps(S_copy_drop,10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)']


def prepare(out, group):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for index, name in enumerate(SELECTIONS[group]):
            path = SOURCE / (name + '.php')
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            local = {'frontier': frontier, 'reentry': reentry, 'receiver_free': receiver_free}[group](checked['fixture'], path)
            checks += scoped(local, 'case' + str(index))
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', choices=tuple(SELECTIONS), default='frontier')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *(SOURCE / (name + '.php') for name in SELECTIONS[args.group]), *modules, *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}; head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, args.group)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()

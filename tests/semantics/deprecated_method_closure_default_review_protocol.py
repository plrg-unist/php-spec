#!/usr/bin/env python3
"""Check captured method authority, borrowed statics and private cache death."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_method_closure_default_review'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTIONS = {
    'frontier': ('this-destructor-enters-other-private-fcc',),
    'statics': ('statics-borrowed-through-last-fcc',),
    'history': ('shared-source-and-receiver-retire', 'method-fcc-cold-clone'),
    'shared_child': ('retired-shared-child-cache',),
}

EXTRA = r'''
dec $fcc_review_without_stamp(pclosurecache*,nat) : pclosurecache*
def $fcc_review_without_stamp(eps,n) = eps
def $fcc_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = $fcc_review_without_stamp(pclosurecache_tail*,n)
  -- if pclosurecache.OBJECT = n
def $fcc_review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = pclosurecache :: $fcc_review_without_stamp(pclosurecache_tail*,n)
  -- if pclosurecache.OBJECT =/= n
dec $fcc_review_ready(pstate,nat,nat,nat,porigin) : bool
def $fcc_review_ready(S,0,n_owner,n_object,porigin) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_PRIVATE_CACHE n_owner) :: pdestructionjob*
def $fcc_review_ready(S,1,n_owner,n_object,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_object)
  -- if $destructor_method(S,n_object) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $fcc_review_ready(S,2,n_owner,n_object,porigin) = true
  -- if $lookup(S.ENV,$ptascii("copy")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_copy)
  -- if (HOBJECT n_owner) <- S.ALLOCATIONS
  -- if S.STATICS = [pstaticcell]
  -- if S.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_static)
def $fcc_review_ready(S,3,n_owner,n_object,porigin) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n_current)
  -- if n_current =/= n_owner
  -- if pcallcontext.FUNCTION = porigin
  -- if ~((HOBJECT n_owner) <- S.ALLOCATIONS)
  -- if ~$gc_retired_valid(S,n_owner)
def $fcc_review_ready(S,n_mode,n_owner,n_object,porigin) = false -- otherwise
dec $fcc_review_pause(pstate,nat,nat,nat,porigin,nat) : pstate
def $fcc_review_pause(S,n_mode,n_owner,n_object,porigin,n) = S
  -- if $fcc_review_ready(S,n_mode,n_owner,n_object,porigin)
def $fcc_review_pause(S,n_mode,n_owner,n_object,porigin,n) = $fcc_review_pause(S_next[.COMPLETION = NORMAL],n_mode,n_owner,n_object,porigin,$nabs($(n - 1)))
  -- if ~$fcc_review_ready(S,n_mode,n_owner,n_object,porigin)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $fcc_review_pause(S,n_mode,n_owner,n_object,porigin,n) = S -- otherwise
'''


def start(fixture, path, private=True):
    owner = 'CACHE_PRIVATE n_owner' if private else 'CACHE_SHARED'
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.COMPLETION = NORMAL', 'S_warn.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_owner', 'pcallcontext.INSTANCE = (n_owner)',
        'pcallcontext.CACHE = eps', 'pcallcontext.RECEIVER = (n_this)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$deprecated_parameter_recipient(S_warn,pfunction)',
        '$default_receive_recipient(S_warn,pfunction,pdefault)',
        '$default_cache_owner(S_warn) = (' + owner + ')',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        'S_warn.PARAMETERRECEIVES = [preceivebirth]', 'n_receive = 1',
        'preceivebirth.ACTIVE', 'preceivebirth.ENTRY = (n_owner)',
        'preceivebirth.CACHE_OWNER = (' + owner + ')',
        '$parameter_receive_deprecated_entry(S_warn,preceivebirth)',
        '$parameter_receive_cache_entry(S_warn,preceivebirth)',
        '$default_cache_birth_valid(S_warn,preceivebirth)',
        '$parameter_receive_context_valid(S_warn,S_warn.CURRENT)',
        '$closure_cache_at(S_warn.CLOSURECACHES,n_owner) = (pclosurecache)',
        'pclosurecache.FUNCTION = pfunction.ORIGIN', 'pclosurecache.CACHE = (' + owner + ')',
        '$closure_scope_at(S_warn.CLOSURESCOPES,n_owner) = (pclosurescope)',
        '$closure_scope_row_valid(S_warn,pclosurescope)',
        'pcallcontext.LEXICAL_CLASS = (pclosurescope.LEXICAL)',
        'pcallcontext.CALLED_CLASS = (pclosurescope.CALLED)',
        'pclosurescope.RECEIVER = (n_this)',
        '$node_children(S_warn,HOBJECT n_owner) = [HOBJECT n_this]',
        '(HOBJECT n_owner) <- $machine_roots(S_warn)',
        '~((HOBJECT n_this) <- $machine_roots(S_warn))',
        'S_missing = S_warn[.CLOSURECACHES = $fcc_review_without_stamp(S_warn.CLOSURECACHES,n_owner)]',
        '$default_cache_owner(S_missing) = eps',
        '~$deprecated_parameter_recipient(S_missing,pfunction)',
        '~$deprecated_parameter_recipient(S_warn[.CURRENT = (pcallcontext[.INSTANCE = eps])],pfunction)',
        '~$deprecated_parameter_recipient(S_warn[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])],pfunction)',
        '~$deprecated_parameter_recipient(S_warn[.CURRENT = (pcallcontext[.RECEIVER = (n_owner)])],pfunction)',
        '~$parameter_receive_deprecated_entry(S_warn,preceivebirth[.ENTRY = eps])',
        'S_bad = S_warn[.PARAMETERRECEIVES = [preceivebirth[.ENTRY = eps]]]',
        '~$parameter_receive_context_valid(S_bad,S_bad.CURRENT)',
        '$call_descriptors_valid(S_warn)',
        'S_bind = $parameter_test_pause(S_warn,0,10000)', 'S_bind.COMPLETION = NORMAL',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)']
    return checks


def private_cache():
    return ['S_cache.COMPLETION = BUDGET',
        '$private_default_cache_at(S_cache.PRIVATEDEFAULTCACHE,n_owner,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array', 'pdefaultcache.CLASS = PVARRAY true eps',
        '$private_default_caches_valid(S_cache,S_cache.PRIVATEDEFAULTCACHE)',
        '$lookup(S_cache.ENV,$ptascii("v")) = (n_formal)',
        'S_cache.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '(HCELL n_formal) <- $machine_roots(S_cache)',
        '$call_descriptors_valid(S_cache)']


def marker():
    return ['S_marker.COMPLETION = NORMAL',
        'S_marker.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_marker*',
        'pdestructionrelease.JOBS = (DESTRUCTION_PRIVATE_CACHE n_owner) :: (DESTRUCTION_VALUE (HOBJECT n_this)) :: (DESTRUCTION_HANDLE n_owner) :: pdestructionjob_tail*',
        '$destructor_release_valid(S_marker,pdestructionrelease)',
        '$private_default_caches_valid(S_marker,S_marker.PRIVATEDEFAULTCACHE)',
        '$gc_retired_valid(S_marker,n_owner)',
        '~((HOBJECT n_owner) <- S_marker.ALLOCATIONS)',
        '$private_default_cache_at(S_marker.PRIVATEDEFAULTCACHE,n_owner,pdefault.ORIGIN) = (pdefaultcache)',
        '$destruction_job_nodes([DESTRUCTION_PRIVATE_CACHE n_owner]) = eps',
        '$gc_temporary_nodes([DESTRUCTION_PRIVATE_CACHE n_owner]) = eps',
        'S_drop = $drive_steps(S_marker,1)', 'S_drop.COMPLETION = BUDGET',
        '$private_default_cache_at(S_drop.PRIVATEDEFAULTCACHE,n_owner,pdefault.ORIGIN) = eps',
        '$gc_retired_valid(S_drop,n_owner)', '~$private_default_cache_retired(S_drop,n_owner)',
        '~$private_default_caches_valid(S_drop,[{OWNER n_owner,ENTRY pdefaultcache}])',
        'S_drop.DEFAULTCACHE = S_marker.DEFAULTCACHE',
        'S_drop.CALLDEFAULTCACHE = S_marker.CALLDEFAULTCACHE',
        'S_drop.CLASSCONSTANTCACHE = S_marker.CLASSCONSTANTCACHE']


def frontier(fixture, path):
    return start(fixture, path) + [
        'S_budget = $drive_steps(S_bind,0)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.PRIVATEDEFAULTCACHE = eps',
        'S_cache = $drive_steps(S_budget[.COMPLETION = NORMAL],1)'] + private_cache() + [
        'S_marker = $fcc_review_pause(S_cache[.COMPLETION = NORMAL],0,n_owner,0,pdefault.ORIGIN,10000)'] + marker() + [
        'S_this = $fcc_review_pause(S_drop[.COMPLETION = NORMAL],1,n_owner,n_this,pdefault.ORIGIN,10000)',
        'S_this.COMPLETION = NORMAL', '$fcc_review_ready(S_this,1,n_owner,n_this,pdefault.ORIGIN)',
        '$gc_retired_valid(S_this,n_owner)',
        '~$private_default_caches_valid(S_this,[{OWNER n_owner,ENTRY pdefaultcache}])',
        '$parameter_receive_birth(S_this,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.ENTRY = (n_owner)',
        '$parameter_receive_deprecated_entry(S_this,preceivebirth_closed)',
        '$default_cache_birth_valid(S_this,preceivebirth_closed)',
        'S_inner = $dep_pause(S_this,10000)', 'S_inner.COMPLETION = NORMAL',
        'S_inner.CURRENT = (pcallcontext_inner)', 'pcallcontext_inner.INSTANCE = (n_other)',
        'pcallcontext_inner.TARGET = CLOSURE_TARGET n_other', 'n_other =/= n_owner',
        '$deprecated_parameter_recipient(S_inner,pfunction)',
        '$default_cache_owner(S_inner) = (CACHE_PRIVATE n_other)',
        '$parameter_receive_owner(S_inner.CURRENT) = (n_receive_inner)',
        '$parameter_receive_birth(S_inner,n_receive_inner) = (preceivebirth_inner)',
        'preceivebirth_inner.ENTRY = (n_other)',
        'preceivebirth_inner.CACHE_OWNER = (CACHE_PRIVATE n_other)',
        '$default_current_cache(S_inner,pdefault.ORIGIN) = eps',
        '$private_default_cache_at(S_inner.PRIVATEDEFAULTCACHE,n_owner,pdefault.ORIGIN) = eps',
        'S_inner_bind = $parameter_test_pause(S_inner,0,10000)',
        'S_inner_bind.COMPLETION = NORMAL', 'S_inner_after = $drive_steps(S_inner_bind,1)',
        'S_inner_after.COMPLETION = BUDGET',
        '$private_default_cache_at(S_inner_after.PRIVATEDEFAULTCACHE,n_other,pdefault.ORIGIN) = (pdefaultcache_other)',
        'pdefaultcache_other.VALUE = pdefaultcache.VALUE',
        '$private_default_caches_valid(S_inner_after,S_inner_after.PRIVATEDEFAULTCACHE)',
        '~$private_default_caches_valid(S_inner_after,[{OWNER n_owner,ENTRY pdefaultcache}])',
        'S_done = $drive_steps(S_inner_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', 'S_done.PRIVATEDEFAULTCACHE = eps',
        '$call_descriptors_valid(S_done)',
        'S_full = $drive_steps(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
        'S_done.EVENTS = S_full.EVENTS', 'S_done.PRIVATEDEFAULTCACHE = S_full.PRIVATEDEFAULTCACHE']


def statics(fixture, path):
    return start(fixture, path) + ['S_cache = $drive_steps(S_bind,1)'] + private_cache() + [
        'S_live = $fcc_review_pause(S_cache[.COMPLETION = NORMAL],2,n_owner,0,pdefault.ORIGIN,10000)',
        'S_live.COMPLETION = NORMAL', '$fcc_review_ready(S_live,2,n_owner,0,pdefault.ORIGIN)',
        'S_live.STATICS = [pstaticcell]',
        'S_live.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_static)',
        '(HCELL pstaticcell.CELL) <- $machine_roots(S_live)',
        '$node_children(S_live,HOBJECT n_owner) = [HOBJECT n_this]',
        '~((HOBJECT n_static) <- $node_children(S_live,HOBJECT n_owner))',
        '$lookup(S_live.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_live.STORE[n_copy_cell] = DEFINED (POBJECT n_copy)',
        '$node_children(S_live,HOBJECT n_copy) = [HOBJECT n_this]',
        '$closure_cache_at(S_live.CLOSURECACHES,n_copy) = (pclosurecache_copy)',
        'pclosurecache_copy.SOURCE = (n_owner)', 'pclosurecache_copy.CACHE = (CACHE_PRIVATE n_copy)',
        '$private_default_cache_at(S_live.PRIVATEDEFAULTCACHE,n_copy,pdefault.ORIGIN) = eps',
        'S_marker = $fcc_review_pause(S_live,0,n_owner,0,pdefault.ORIGIN,10000)'] + marker() + [
        'S_drop.STATICS = S_live.STATICS',
        'S_drop.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_static)',
        'S_this = $fcc_review_pause(S_drop[.COMPLETION = NORMAL],1,n_copy,n_this,pdefault.ORIGIN,10000)',
        'S_this.COMPLETION = NORMAL', '$fcc_review_ready(S_this,1,n_copy,n_this,pdefault.ORIGIN)',
        '~((HOBJECT n_owner) <- S_this.ALLOCATIONS)',
        '~((HOBJECT n_copy) <- S_this.ALLOCATIONS)',
        '(HOBJECT n_static) <- S_this.ALLOCATIONS',
        'S_this.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_static)',
        '(HCELL pstaticcell.CELL) <- $machine_roots(S_this)',
        'S_this.PRIVATEDEFAULTCACHE = eps',
        '$parameter_receive_birth(S_this,n_receive) = (preceivebirth_closed)',
        '$parameter_receive_deprecated_entry(S_this,preceivebirth_closed)',
        '$default_cache_birth_valid(S_this,preceivebirth_closed)',
        'S_done = $drive_steps(S_this,10000)', 'S_done.COMPLETION = NORMAL',
        'S_done.STORE[pstaticcell.CELL] = DEFINED PNULL',
        '~((HOBJECT n_static) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)']


def history(fixture, path):
    return start(fixture, path, False) + [
        'S_cache = $drive_steps(S_bind,1)', 'S_cache.COMPLETION = BUDGET',
        '$default_cache_at(S_cache.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        'S_hit = $fcc_review_pause(S_cache[.COMPLETION = NORMAL],3,n_owner,0,pfunction.ORIGIN,10000)',
        'S_hit.COMPLETION = NORMAL', '$fcc_review_ready(S_hit,3,n_owner,0,pfunction.ORIGIN)',
        'S_hit.CURRENT = (pcallcontext_hit)', 'pcallcontext_hit.INSTANCE = (n_next)',
        'pcallcontext_hit.TARGET = CLOSURE_TARGET n_next', 'n_next =/= n_owner',
        '~((HOBJECT n_owner) <- S_hit.ALLOCATIONS)',
        '~((HOBJECT n_this) <- S_hit.ALLOCATIONS)',
        '~((HOBJECT n_owner) <- $machine_roots(S_hit))',
        '~((HOBJECT n_this) <- $machine_roots(S_hit))',
        '$parameter_receive_birth(S_hit,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.ENTRY = (n_owner)',
        '$parameter_receive_deprecated_entry(S_hit,preceivebirth_closed)',
        '$parameter_receive_cache_entry(S_hit,preceivebirth_closed)',
        '$default_cache_birth_valid(S_hit,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_hit,preceivebirth_closed[.ENTRY = eps])',
        '~$default_cache_birth_valid(S_hit,preceivebirth_closed[.CACHE_OWNER = (CACHE_PRIVATE n_owner)])',
        '$default_cache_owner(S_hit) = (CACHE_SHARED)',
        '$default_current_cache(S_hit,pdefault.ORIGIN) = (pdefaultcache)',
        '$default_receive_recipient(S_hit,pfunction,pdefault)',
        '$deprecated_parameter_recipient(S_hit,pfunction)',
        '$call_descriptors_valid(S_hit)',
        'S_done = $drive_steps(S_hit,10000)', 'S_done.COMPLETION = NORMAL',
        'S_done.DEFAULTCACHE = S_hit.DEFAULTCACHE', 'S_done.PARAMETERRECEIVES = S_hit.PARAMETERRECEIVES',
        '~((HOBJECT n_next) <- S_done.ALLOCATIONS)',
        '$parameter_receive_deprecated_entry(S_done,preceivebirth_closed)',
        '$call_descriptors_valid(S_done)']


def shared_identity(fixture, path):
    return start(fixture, path, False) + [
        '$lookup($global_table_view(S_warn).ENV,$ptascii("early")) = (n_early_cell)',
        'S_warn.STORE[n_early_cell] = DEFINED (POBJECT n_early)', 'n_early =/= n_owner',
        '$closure_cache_at(S_warn.CLOSURECACHES,n_early) = (pclosurecache_early)',
        'pclosurecache_early.FUNCTION = pfunction.ORIGIN',
        'pclosurecache_early.CACHE = (CACHE_SHARED)',
        '$node_children(S_warn,HOBJECT n_early) = [HOBJECT n_this]',
        'S_swapped = S_warn[.PARAMETERRECEIVES = [preceivebirth[.ENTRY = (n_early)]]]',
        '~$parameter_receive_context_valid(S_swapped,S_swapped.CURRENT)',
        '~$call_descriptors_valid(S_swapped)',
        'S_swapped_current = S_warn[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET n_early][.INSTANCE = (n_early)])]',
        '~$parameter_receive_context_valid(S_swapped_current,S_swapped_current.CURRENT)',
        'S_done = $drive_steps(S_bind,10000)', 'S_done.COMPLETION = NORMAL',
        '$parameter_receive_birth(S_done,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.ENTRY = (n_owner)',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$default_cache_birth_valid(S_done,preceivebirth_closed)',
        '$call_descriptors_valid(S_done)']


def shared_child(fixture, path):
    return start(fixture, path, False) + [
        '$lookup($global_table_view(S_warn).ENV,$ptascii("other")) = (n_child_cell)',
        'S_warn.STORE[n_child_cell] = DEFINED (POBJECT n_child)', 'n_child =/= n_owner',
        '$closure_scope_at(S_warn.CLOSURESCOPES,n_child) = (pclosurescope_child)',
        'pclosurescope_child.RECEIVER = (n_child_this)', 'n_child_this =/= n_this',
        '$parameter_receive_latest(S_bind.PARAMETERRECEIVES,(n_receive),1,eps) = (n_child_receive)',
        '$parameter_receive_birth(S_bind,n_child_receive) = (preceivebirth_child)',
        '~preceivebirth_child.ACTIVE', 'preceivebirth_child.PARENT = (n_receive)',
        'preceivebirth_child.ENTRY = (n_child)',
        'preceivebirth_child.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth_child.FUNCTION = preceivebirth.FUNCTION',
        'preceivebirth_child.ORIGIN = preceivebirth.ORIGIN',
        '~((HOBJECT n_child) <- S_bind.ALLOCATIONS)',
        '~((HOBJECT n_child_this) <- S_bind.ALLOCATIONS)',
        '~((HOBJECT n_child) <- $machine_roots(S_bind))',
        '~((HOBJECT n_child_this) <- $machine_roots(S_bind))',
        '~$gc_retired_valid(S_bind,n_child)',
        '$method_fcc_witness(S_bind,preceivebirth_child)',
        '$parameter_receive_source_valid(S_bind,preceivebirth_child)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth_child)',
        '$parameter_receive_cache_child(S_bind,preceivebirth,n_receive,preceivebirth_child)',
        '$default_current_cache(S_bind,pdefault.ORIGIN) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PINT 9',
        '$default_pending_cache_valid(S_bind,pdefault)', '$call_descriptors_valid(S_bind)',
        'preceivebirth_missing = preceivebirth_child[.ENTRY = eps]',
        '$parameter_receive_source_valid(S_bind,preceivebirth_missing)',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth_missing)',
        '~$parameter_receive_cache_child(S_bind,preceivebirth,n_receive,preceivebirth_missing)',
        'S_missing_child = S_bind[.PARAMETERRECEIVES = [preceivebirth,preceivebirth_missing]]',
        '~$default_pending_cache_valid(S_missing_child,pdefault)',
        'S_after = $drive_steps(S_bind,1)', 'S_after.COMPLETION = BUDGET',
        '$default_cache_at(S_after.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)']


def source_path(name):
    if name == 'method-fcc-cold-clone':
        return ROOT / 'tests/semantics/deprecated_global_constant' / (name + '.php')
    return SOURCE / (name + '.php')


def scoped(checks, tag):
    pattern = r'\b(?:U|S_[a-z_]+|n_[a-z_]+|pcallcontext(?:_[a-z_]+)?|pfunction|pdefault|pdefaultcache(?:_[a-z_]+)?|pclosurecache(?:_[a-z_]+)?|pclosurescope|pstaticcell|preceivebirth(?:_[a-z_]+)?|pdestructionrelease|pdestructionjob_[a-z_]+|ptask_[a-z_]+)\b'
    return [re.sub(pattern, lambda match: match.group() + '_' + tag, check) for check in checks]


def prepare(out, group):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for index, name in enumerate(SELECTIONS[group]):
            path = source_path(name)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            case = shared_identity if name == 'method-fcc-cold-clone' else {'frontier': frontier, 'statics': statics, 'history': history, 'shared_child': shared_child}[group]
            checks += scoped(case(checked['fixture'], path), 'case' + str(index))
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
    paths = [Path(__file__), *(source_path(name) for name in SELECTIONS[args.group]), *modules, *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
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

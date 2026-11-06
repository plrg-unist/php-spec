#!/usr/bin/env python3
"""Check actual invocation owners and local/cache/API cleanup boundaries."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_closure_call_default_review'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
LIFETIME = ('cleared-call-capture', 'local-reentry-before-context-drop', 'local-throw-before-context-drop')
REENTRY = ROOT / 'tests/semantics/deprecated_global_constant/call-owned-reentry-empty.php'

EXTRA = r'''
dec $call_review_ready(pstate,nat,nat,nat,porigin) : bool
def $call_review_ready(S,0,n_call,n_object,porigin) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_CALL_CACHE n_call) :: pdestructionjob*
def $call_review_ready(S,1,n_call,n_object,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_object)
  -- if $destructor_method(S,n_object) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $call_review_ready(S,2,n_call,n_object,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CACHE = (CACHE_CALL n_inner)
  -- if n_inner =/= n_call
  -- if $call_default_cache_at(S.CALLDEFAULTCACHE,n_inner,porigin) =/= eps
def $call_review_ready(S,3,n_call,n_object,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_local)
  -- if $(n_local < |S.OBJECTS|)
  -- if S.OBJECTS[n_local] = INSTANCE porigin_local
  -- if $class_at(S.CLASSES,porigin_local) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Local191")
  -- if $destructor_method(S,n_local) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $call_review_ready(S,n_mode,n_call,n_object,porigin) = false -- otherwise
dec $call_review_pause(pstate,nat,nat,nat,porigin,nat) : pstate
def $call_review_pause(S,n_mode,n_call,n_object,porigin,n) = S
  -- if $call_review_ready(S,n_mode,n_call,n_object,porigin)
def $call_review_pause(S,n_mode,n_call,n_object,porigin,n) = $call_review_pause(S_next[.COMPLETION = NORMAL],n_mode,n_call,n_object,porigin,$nabs($(n - 1)))
  -- if ~$call_review_ready(S,n_mode,n_call,n_object,porigin)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $call_review_pause(S,n_mode,n_call,n_object,porigin,n) = S -- otherwise
'''


def scoped(checks, tag):
    pattern = r'\b(?:U|S_[a-z_]+|n_[a-z_]+|porigin|pcallcontext(?:_[a-z_]+)?|pfunction|pdefault|pcallparamcache|pdefaultcache(?:_[a-z_]+)?|pclosurecallcache|preceivebirth(?:_[a-z_]+)?|pdestructionrelease|pdestructionjob_[a-z_]+|ptask_[a-z_]+)\b'
    return [re.sub(pattern, lambda match: match.group() + '_' + tag, check) for check in checks]


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.COMPLETION = NORMAL', 'S_warn.CURRENT = (pcallcontext)',
        'pcallcontext.INSTANCE = (n_source)', 'pcallcontext.RECEIVER = (n_receiver)',
        'pcallcontext.CACHE = (CACHE_CALL n_call)',
        '$closure_call_context_cache_valid(S_warn,pcallcontext)',
        '$default_cache_owner(S_warn) = (CACHE_CALL n_call)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        '$parameter_call_current(S_warn,pfunction)',
        '$deprecated_parameter_recipient(S_warn,pfunction)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        'preceivebirth.CACHE_OWNER = (CACHE_CALL n_call)',
        '$default_cache_birth_valid(S_warn,preceivebirth)']


def lifetime(fixture, path, tag):
    checks = start(fixture, path) + [
        'S_warn.OBJECTS[n_source] = REALCLOSURE pfunction.ORIGIN ([DIRECT (POBJECT n_capture)]) eps',
        '(HOBJECT n_source) <- $machine_roots(S_warn)', '(HOBJECT n_receiver) <- $machine_roots(S_warn)',
        '(HOBJECT n_capture) <- $node_children(S_warn,HOBJECT n_source)',
        'S_bind = $parameter_test_pause(S_warn,0,10000)', 'S_bind.COMPLETION = NORMAL',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)']
    if tag == 'clear':
        checks += ['S_budget = $drive_steps(S_bind,0)', 'S_budget.COMPLETION = BUDGET',
            'S_cache = $drive_steps(S_budget[.COMPLETION = NORMAL],1)']
    else:
        checks += ['S_cache = $drive_steps(S_bind,1)']
    checks += ['S_cache.COMPLETION = BUDGET', 'S_cache.CALLDEFAULTCACHE = [pcallparamcache]',
        'pcallparamcache.INVOCATION = n_call', 'pcallparamcache.ENTRY.ORIGIN = pdefault.ORIGIN',
        'pcallparamcache.ENTRY.VALUE = PARRAY n_array', 'pcallparamcache.ENTRY.CLASS = PVARRAY true eps',
        '$call_default_cache_roots(S_cache.CALLDEFAULTCACHE) = [HARRAY n_array]',
        '$call_default_caches_valid(S_cache,S_cache.CALLDEFAULTCACHE)',
        '$lookup(S_cache.ENV,$ptascii("value")) = (n_formal)',
        'S_cache.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '(HCELL n_formal) <- $machine_roots(S_cache)', '$call_descriptors_valid(S_cache)',
        '~$call_default_caches_valid(S_cache,[pcallparamcache,pcallparamcache])',
        '~$call_default_caches_valid(S_cache,[pcallparamcache[.INVOCATION = |S_cache.CLOSURECALLCACHES|]])',
        '~$call_default_caches_valid(S_cache,[pcallparamcache[.ENTRY.CLASS = PVARRAY false eps]])',
        'S_missing = S_warn[.CLOSURECALLCACHES = eps]', '$default_cache_owner(S_missing) = eps',
        '~$parameter_call_current(S_missing,pfunction)',
        'S_false_birth = S_warn[.PARAMETERRECEIVES = [preceivebirth[.CACHE_OWNER = (CACHE_SHARED)]]]',
        '~$parameter_receive_context_valid(S_false_birth,S_false_birth.CURRENT)']
    if tag != 'clear':
        checks += ['S_local = $call_review_pause(S_cache[.COMPLETION = NORMAL],3,n_call,0,pdefault.ORIGIN,10000)',
            'S_local.COMPLETION = NORMAL', '$call_review_ready(S_local,3,n_call,0,pdefault.ORIGIN)',
            '$call_default_marker(S_local.DESTRUCTION.RELEASES[0].JOBS,n_call)',
            '$call_default_caches_valid(S_local,S_local.CALLDEFAULTCACHE)',
            '$call_default_cache_at(S_local.CALLDEFAULTCACHE,n_call,pdefault.ORIGIN) = (pcallparamcache.ENTRY)',
            '$call_descriptors_valid(S_local)']
        origin = 'S_local'
    else:
        origin = 'S_cache[.COMPLETION = NORMAL]'
    checks += ['S_marker = $call_review_pause(' + origin + ',0,n_call,0,pdefault.ORIGIN,10000)',
        'S_marker.COMPLETION = NORMAL',
        'S_marker.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_marker*',
        'pdestructionrelease.JOBS = (DESTRUCTION_CALL_CACHE n_call) :: pdestructionjob_context*',
        'pdestructionjob_context* = [DESTRUCTION_VALUE (HOBJECT n_receiver),DESTRUCTION_VALUE (HOBJECT n_source)]',
        '$destructor_release_valid(S_marker,pdestructionrelease)',
        '~$call_default_context(S_marker,S_marker.CURRENT,n_call)',
        '~$call_default_frames(S_marker,S_marker.FRAMES,n_call)',
        '$call_default_caches_valid(S_marker,S_marker.CALLDEFAULTCACHE)',
        '$destruction_job_nodes([DESTRUCTION_CALL_CACHE n_call]) = eps',
        '$gc_temporary_nodes([DESTRUCTION_CALL_CACHE n_call]) = eps',
        'n_absent = |S_marker.CLOSURECALLCACHES|',
        '~$destructor_jobs_valid(S_marker,[DESTRUCTION_CALL_CACHE n_absent])',
        'S_drop = $drive_steps(S_marker,1)', 'S_drop.COMPLETION = BUDGET',
        'S_drop.CALLDEFAULTCACHE = eps', 'S_drop.DEFAULTCACHE = S_marker.DEFAULTCACHE',
        'S_drop.PRIVATEDEFAULTCACHE = S_marker.PRIVATEDEFAULTCACHE',
        'S_drop.CLASSCONSTANTCACHE = S_marker.CLASSCONSTANTCACHE',
        '(HOBJECT n_source) <- S_drop.ALLOCATIONS', '(HOBJECT n_receiver) <- S_drop.ALLOCATIONS',
        '(HOBJECT n_source) <- $machine_roots(S_drop)', '(HOBJECT n_receiver) <- $machine_roots(S_drop)',
        '~$call_default_live(S_drop,n_call)',
        '~$call_default_caches_valid(S_drop,[pcallparamcache])',
        'S_receiver = $call_review_pause(S_drop[.COMPLETION = NORMAL],1,n_call,n_receiver,pdefault.ORIGIN,10000)',
        'S_receiver.COMPLETION = NORMAL', '$call_review_ready(S_receiver,1,n_call,n_receiver,pdefault.ORIGIN)',
        'S_receiver.CALLDEFAULTCACHE = eps', '(HOBJECT n_source) <- S_receiver.ALLOCATIONS',
        'S_capture = $call_review_pause(S_receiver,1,n_call,n_capture,pdefault.ORIGIN,10000)',
        'S_capture.COMPLETION = NORMAL', '$call_review_ready(S_capture,1,n_call,n_capture,pdefault.ORIGIN)',
        'S_capture.CALLDEFAULTCACHE = eps', '~((HOBJECT n_source) <- S_capture.ALLOCATIONS)',
        '$call_descriptors_valid(S_capture)',
        'S_done = $drive_steps(S_capture,10000)', 'S_done.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_done)', 'S_done.CALLDEFAULTCACHE = eps',
        '$parameter_receive_birth(S_done,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.CACHE_OWNER = (CACHE_CALL n_call)',
        '$default_cache_birth_valid(S_done,preceivebirth_closed)',
        '~$call_default_caches_valid(S_done,[pcallparamcache])']
    if tag == 'clear':
        checks += ['S_full = $drive_steps(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
            'S_done.EVENTS = S_full.EVENTS', 'S_done.CALLDEFAULTCACHE = S_full.CALLDEFAULTCACHE']
    return scoped(checks, tag)


def reentry(fixture, path):
    return start(fixture, path) + [
        'S_inner = $call_review_pause(S_warn,2,n_call,0,pdefault.ORIGIN,10000)',
        'S_inner.COMPLETION = NORMAL', '$call_review_ready(S_inner,2,n_call,0,pdefault.ORIGIN)',
        'S_inner.CURRENT = (pcallcontext_inner)', 'pcallcontext_inner.CACHE = (CACHE_CALL n_inner)',
        'n_call =/= n_inner',
        'S_inner.CLOSURECALLCACHES[n_call] = S_inner.CLOSURECALLCACHES[n_inner]',
        '$call_default_cache_at(S_inner.CALLDEFAULTCACHE,n_inner,pdefault.ORIGIN) = (pdefaultcache_inner)',
        'pdefaultcache_inner.VALUE = PINT 9', '$call_default_live(S_inner,n_call)',
        '$call_default_frames(S_inner,S_inner.FRAMES,n_call)', '$call_default_context(S_inner,S_inner.CURRENT,n_inner)',
        '$call_default_caches_valid(S_inner,S_inner.CALLDEFAULTCACHE)',
        'S_bind = $parameter_test_pause(S_inner,0,10000)', 'S_bind.COMPLETION = NORMAL',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth_parent)',
        '$parameter_receive_latest(S_bind.PARAMETERRECEIVES,(n_receive),1,eps) = (n_child)',
        '$parameter_receive_birth(S_bind,n_child) = (preceivebirth_child)',
        'preceivebirth_parent.CACHE_OWNER = (CACHE_CALL n_call)',
        'preceivebirth_child.CACHE_OWNER = (CACHE_CALL n_inner)', '~preceivebirth_child.ACTIVE',
        'preceivebirth_child.FUNCTION = preceivebirth_parent.FUNCTION',
        'preceivebirth_child.ORIGIN = preceivebirth_parent.ORIGIN',
        '$parameter_receive_source_valid(S_bind,preceivebirth_child)',
        '$default_cache_birth_valid(S_bind,preceivebirth_child)',
        '~$parameter_receive_cache_child(S_bind,preceivebirth_parent,n_receive,preceivebirth_child)',
        '$call_default_cache_at(S_bind.CALLDEFAULTCACHE,n_inner,pdefault.ORIGIN) = eps',
        '$default_current_cache(S_bind,pdefault.ORIGIN) = eps',
        'S_forged = S_bind[.CALLDEFAULTCACHE = [{INVOCATION n_call,ENTRY pdefaultcache_inner}]]',
        '$call_default_caches_valid(S_forged,S_forged.CALLDEFAULTCACHE)',
        '~$default_pending_cache_valid(S_forged,pdefault)',
        'S_after = $drive_steps(S_bind,1)', 'S_after.COMPLETION = BUDGET',
        '$call_default_cache_at(S_after.CALLDEFAULTCACHE,n_call,pdefault.ORIGIN) = (pdefaultcache_outer)',
        'pdefaultcache_outer.CLASS = PVARRAY true eps',
        '$call_default_caches_valid(S_after,S_after.CALLDEFAULTCACHE)',
        'S_done = $drive_steps(S_after[.COMPLETION = NORMAL],10000)', 'S_done.COMPLETION = NORMAL',
        'S_done.CALLDEFAULTCACHE = eps',
        '$closure_call_cache_record_valid(S_done,n_call,S_done.CLOSURECALLCACHES[n_call])',
        '~$call_default_live(S_done,n_call)',
        '~$call_default_caches_valid(S_done,[{INVOCATION n_call,ENTRY pdefaultcache_outer}])',
        '$call_descriptors_valid(S_done)']


def prepare(out, group):
    paths = [SOURCE / (name + '.php') for name in LIFETIME] if group == 'lifetime' else [REENTRY]
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for tag, path in zip(('clear', 'local', 'throw'), paths):
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            checks += lifetime(checked['fixture'], path, tag) if group == 'lifetime' else reentry(checked['fixture'], path)
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', choices=('lifetime', 'reentry'), default='lifetime')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    sources = [SOURCE / (name + '.php') for name in LIFETIME] if args.group == 'lifetime' else [REENTRY]
    paths = [Path(__file__), *sources, *modules, *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
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

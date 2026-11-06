#!/usr/bin/env python3
"""Check allocated constructor receivers, formal caches, promotion and exit flags."""
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
PEER = ROOT / 'tests/semantics/deprecated_constructor_default_review'
AUTHOR = ROOT / 'tests/semantics/deprecated_constructor_default'
SELECTIONS = {
    'frontier': (PEER / 'promoted-local-cleanup.php',),
    'history': (AUTHOR / 'body-throw-cache.php',),
    'exit': (PEER / 'body-exit-promotion.php', AUTHOR / 'handler-exit-shutdown.php',
        AUTHOR / 'cold-warm-alias.php'),
}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

EXTRA = r'''
dec $ctor_review_ready(pstate,nat,nat,porigin) : bool
def $ctor_review_ready(S,0,n,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_local)
  -- if $destructor_method(S,n_local) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
  -- if $class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Local198")
def $ctor_review_ready(S,1,n,porigin) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail*
def $ctor_review_ready(S,2,n,porigin) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_next)
  -- if n_next =/= n
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $ctor_review_ready(S,3,n,porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $origin_node(S.SOURCES,porigin_site) = (NExprMethodCall expression phpType20 (SEQUENCE phpType7*) metadata)
def $ctor_review_ready(S,4,n,porigin) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
def $ctor_review_ready(S,n_mode,n,porigin) = false -- otherwise
dec $ctor_review_pause(pstate,nat,nat,porigin,nat) : pstate
def $ctor_review_pause(S,n_mode,n_object,porigin,n) = S
  -- if $ctor_review_ready(S,n_mode,n_object,porigin)
def $ctor_review_pause(S,n_mode,n_object,porigin,n) = $ctor_review_pause(S_next[.COMPLETION = NORMAL],n_mode,n_object,porigin,$nabs($(n - 1)))
  -- if ~$ctor_review_ready(S,n_mode,n_object,porigin)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $ctor_review_pause(S,n_mode,n_object,porigin,n) = S -- otherwise
dec $ctor_review_output_item(pevent) : ptbytes
def $ctor_review_output_item(OUTPUT ptbytes) = ptbytes
def $ctor_review_output_item(pevent) = eps -- otherwise
dec $ctor_review_output(pevent*) : ptbytes
def $ctor_review_output(eps) = eps
def $ctor_review_output(pevent :: pevent_tail*) = $ctor_review_output_item(pevent) ++ $ctor_review_output(pevent_tail*)
'''


def start(fixture, path, tag=''):
    suffix = '_' + tag if tag else ''
    s, warn = 'S_start' + suffix, 'S_warn' + suffix
    call, fn, birth = 'pcallcontext' + suffix, 'pfunction' + suffix, 'preceivebirth' + suffix
    receiver, owner = 'n_ctor' + suffix, 'n_receive' + suffix
    checks = ['U' + suffix + ' = ' + fixture,
        s + ' = $php_run(U' + suffix + ',0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        s + '.COMPLETION = BUDGET', warn + ' = $dep_pause(' + s + '[.COMPLETION = NORMAL],10000)',
        warn + '.COMPLETION = NORMAL', warn + '.CURRENT = (' + call + ')',
        '$receiving_function(' + warn + ',' + call + '.FUNCTION) = (' + fn + ')',
        call + '.TARGET = METHOD_TARGET ' + receiver + ' ' + fn + '.ORIGIN',
        call + '.RECEIVER = (' + receiver + ')', call + '.INSTANCE = eps', call + '.CACHE = eps',
        '(' + 'HOBJECT ' + receiver + ') <- ' + warn + '.ALLOCATIONS',
        '$parameter_constructor_current(' + warn + ',' + fn + ')',
        '$parameter_receive_owner(' + warn + '.CURRENT) = (' + owner + ')',
        '$parameter_receive_birth(' + warn + ',' + owner + ') = (' + birth + ')',
        birth + '.ACTIVE', birth + '.CACHE_OWNER = (CACHE_SHARED)', birth + '.ENTRY = eps',
        '$parameter_receive_cache_entry(' + warn + ',' + birth + ')',
        '$call_descriptors_valid(' + warn + ')']
    return checks


def frontier(fixture, path):
    checks = start(fixture, path)
    checks += [
        'S_warn.FRAMES = pframe_caller :: pframe_tail*',
        'pframe_caller.TODO = (CTOR_RESULT n_ctor) :: ptask_caller_tail*',
        '$task_nodes(CTOR_RESULT n_ctor) = [HOBJECT n_ctor]',
        '$call_context_roots(S_warn.CURRENT) = [HOBJECT n_ctor]',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_ctor) = 2',
        '$machine_roots(S_warn[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warn)',
        '~$parameter_constructor_current(S_warn[.CURRENT = (pcallcontext[.RECEIVER = eps])],pfunction)',
        '~$parameter_constructor_current(S_warn[.FRAMES = pframe_caller[.TODO = ptask_caller_tail*] :: pframe_tail*],pfunction)',
        'S_local = $ctor_review_pause(S_warn,0,n_ctor,pfunction.ORIGIN,10000)',
        '$ctor_review_ready(S_local,0,n_ctor,pfunction.ORIGIN)',
        '(HOBJECT n_ctor) <- S_local.ALLOCATIONS',
        '$heap_owners($heap_graph(S_local),HOBJECT n_ctor) = 2',
        'S_local.DEFAULTCACHE = eps',
        '$objectprops_at(S_local.OBJECTPROPS,n_ctor) = ([ppropertyslot_local])',
        'ppropertyslot_local.STATE = PROP_INITIAL',
        '$heap_valid($heap_graph(S_local))',
        'S_bind = $parameter_test_pause(S_local,0,10000)',
        'S_bind.TODO = (DEFAULT_BIND pfunction.ORIGIN 0) :: eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$parameter_constructor_current(S_bind,pfunction)',
        '$call_descriptors_valid(S_bind)',
        'S_zero = $drive(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'S_one_raw = $drive(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$default_cache_at(S_one.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$lookup(S_one.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_formal)',
        'S_one.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', '$parameter_receive_owner(S_one.CURRENT) = eps',
        '$objectprops_at(S_one.OBJECTPROPS,n_ctor) = ([ppropertyslot_local])',
        '$call_descriptors_valid(S_one)',
        'S_promote = $ctor_review_pause(S_one,1,n_ctor,pfunction.ORIGIN,10000)',
        '$ctor_review_ready(S_promote,1,n_ctor,pfunction.ORIGIN)',
        '$promotion_descriptor(S_promote,pfunction,0) = (ppropertydesc)',
        '$objectprops_at(S_promote.OBJECTPROPS,n_ctor) = (ppropertyslot_rows_before*)',
        '$property_slot_at(ppropertyslot_rows_before*,ppropertydesc.KEY) = (ppropertyslot_before)',
        'ppropertyslot_before.STATE = PROP_INITIAL',
        '$lookup(S_promote.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_formal)',
        'S_promote.STORE[n_formal] = DEFINED (PARRAY n_array)',
        'S_promoted_raw = $drive_steps(S_promote,1)', 'S_promoted_raw.COMPLETION = BUDGET',
        'S_promoted = S_promoted_raw[.COMPLETION = NORMAL]',
        '$objectprops_at(S_promoted.OBJECTPROPS,n_ctor) = (ppropertyslot_rows_after*)',
        '$property_slot_at(ppropertyslot_rows_after*,ppropertydesc.KEY) = (ppropertyslot_after)',
        'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
        '$heap_owners($heap_graph(S_promoted),HARRAY n_array) = $($heap_owners($heap_graph(S_promote),HARRAY n_array) + 1)',
        'S_promoted.INSTANCEDEFAULTS = S_promote.INSTANCEDEFAULTS',
        '$call_descriptors_valid(S_promoted)',
        'S_cached = $ctor_review_pause(S_promoted,2,n_ctor,pfunction.ORIGIN,10000)',
        '$ctor_review_ready(S_cached,2,n_ctor,pfunction.ORIGIN)',
        'S_cached.CURRENT = (pcallcontext_cached)', 'pcallcontext_cached.RECEIVER = (n_second)',
        'n_second =/= n_ctor', '(HOBJECT n_ctor) <- S_cached.ALLOCATIONS',
        '$object_class_origin(S_cached,n_second) = $object_class_origin(S_cached,n_ctor)',
        '$parameter_constructor_current(S_cached,pfunction)',
        '$parameter_receive_owner(S_cached.CURRENT) = eps',
        'S_cached.PARAMETERRECEIVES = S_one.PARAMETERRECEIVES',
        'S_wrong_receiver = S_cached[.CURRENT = (pcallcontext_cached[.TARGET = METHOD_TARGET n_ctor pfunction.ORIGIN][.RECEIVER = (n_ctor)])]',
        '~$parameter_constructor_current(S_wrong_receiver,pfunction)',
        '~$default_receive_recipient(S_wrong_receiver,pfunction,pdefault)',
        'S_done = $drive(S_bind,20000)', 'S_done.COMPLETION = NORMAL',
        '$drive(S_one,20000) = S_done',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("H|L|C|7|E|C|E|8|R|R|")',
    ]
    return checks


def history(fixture, path):
    checks = start(fixture, path)
    checks += [
        'S_cached = $ctor_review_pause(S_warn,2,n_ctor,pfunction.ORIGIN,10000)',
        '$ctor_review_ready(S_cached,2,n_ctor,pfunction.ORIGIN)',
        'S_cached.CURRENT = (pcallcontext_cached)', 'pcallcontext_cached.RECEIVER = (n_second)',
        'n_second =/= n_ctor', '~((HOBJECT n_ctor) <- S_cached.ALLOCATIONS)',
        '(HOBJECT n_second) <- S_cached.ALLOCATIONS',
        '$parameter_constructor_current(S_cached,pfunction)',
        '$parameter_receive_owner(S_cached.CURRENT) = eps',
        '$parameter_receive_birth(S_cached,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE', 'preceivebirth_closed.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth_closed.ENTRY = eps',
        '$parameter_receive_cache_entry(S_cached,preceivebirth_closed)',
        '$machine_roots(S_cached[.PARAMETERRECEIVES = eps]) = $machine_roots(S_cached)',
        'n_after_ctor = $(n_ctor + 1)',
        'n_object_tail = $nabs($(|S_cached.OBJECTS| - n_after_ctor))',
        'S_poison_retired = S_cached[.OBJECTS = S_cached.OBJECTS[0:n_ctor] ++ [STDINSTANCE] ++ S_cached.OBJECTS[n_after_ctor:n_object_tail]]',
        '$parameter_receive_cache_entry(S_poison_retired,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_cached,preceivebirth_closed[.CALLSITE = eps])',
        '~$parameter_receive_cache_entry(S_cached,preceivebirth_closed[.PUBLICATION = 0])',
        '~$parameter_receive_cache_entry(S_cached,preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.CALLS = eps]])',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_cache_at(S_cached.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$heap_valid($heap_graph(S_cached))', '$call_descriptors_valid(S_cached)',
        'S_done = $drive(S_cached,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("H|C|K|C|K|Z|")',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
    ]
    return checks


def exit_checks(fixtures, paths):
    checks = start(fixtures[0], paths[0], 'body')
    checks += [
        'S_exit = $ctor_review_pause(S_warn_body,4,n_ctor_body,pfunction_body.ORIGIN,10000)',
        '$ctor_review_ready(S_exit,4,n_ctor_body,pfunction_body.ORIGIN)',
        'S_exit.TODO = (EXIT_INVOKE pexitcall) :: ptask_exit_tail*',
        '$exit_invoke_valid(S_exit,pexitcall)',
        '$parameter_constructor_current(S_exit,pfunction_body)',
        '~$closure_call_copy_exit_pending(S_exit)', '$closure_call_copy_cleanup_exit(S_exit) = eps',
        '~$deprecated_handler_exit_ready(S_exit)',
        '~(n_ctor_body <- S_exit.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_exit),HOBJECT n_ctor_body) = 3',
        'S_exit_step_raw = $drive_steps(S_exit,1)', 'S_exit_step_raw.COMPLETION = BUDGET',
        'S_exit_step = S_exit_step_raw[.COMPLETION = NORMAL]',
        'S_exit_step.TODO = (EXIT_UNWIND 7) :: eps',
        'n_ctor_body <- S_exit_step.DESTRUCTION.CALLED',
        '(HOBJECT n_ctor_body) <- S_exit_step.ALLOCATIONS',
        '$heap_owners($heap_graph(S_exit_step),HOBJECT n_ctor_body) = 3',
        'S_exit_step.FRAMES = S_exit.FRAMES', 'S_exit_step.CURRENT = S_exit.CURRENT',
        'S_done_body = $drive_steps(S_exit_step,20000)',
        'S_done_body.COMPLETION = EXITED 7',
        '$ctor_review_output(S_done_body.EVENTS) = $ptascii("H|C|E|S|E|Z|")',
    ]
    checks += start(fixtures[1], paths[1], 'handler')
    checks += [
        '~(n_ctor_handler <- S_warn_handler.DESTRUCTION.CALLED)',
        'S_marker = $dep_exit_pause(S_warn_handler,10000)',
        'S_marker.TODO = (DEPRECATED_HANDLER_EXIT pdestructioncleanup z_status ptask_saved*) :: ptask_marker_tail*',
        'z_status = 7', 'n_ctor_handler <- S_marker.DESTRUCTION.CALLED',
        '(HOBJECT n_ctor_handler) <- S_marker.ALLOCATIONS',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_ctor_handler) = 2',
        'S_marker.DEFAULTCACHE = eps',
        '$constant_context_valid(S_marker)', '$call_descriptors_valid(S_marker)',
        'S_done_handler = $drive(S_marker,20000)', 'S_done_handler.COMPLETION = EXITED 7',
        '$ctor_review_output(S_done_handler.EVENTS) = $ptascii("H|S|C|9|D|Z|")',
    ]
    checks += start(fixtures[2], paths[2], 'explicit')
    checks += [
        'S_explicit = $ctor_review_pause(S_warn_explicit,3,n_ctor_explicit,pfunction_explicit.ORIGIN,10000)',
        '$ctor_review_ready(S_explicit,3,n_ctor_explicit,pfunction_explicit.ORIGIN)',
        'S_explicit.CURRENT = (pcallcontext_explicit_call)',
        'pcallcontext_explicit_call.RECEIVER = (n_explicit)',
        '~$parameter_constructor_current(S_explicit,pfunction_explicit)',
        '~(n_explicit <- S_explicit.DESTRUCTION.CALLED)',
        '$deprecated_handler_exit_scope(S_explicit,S_explicit) = S_explicit',
        '$closure_call_copy_exit_scope(S_explicit,S_explicit) = S_explicit',
        'S_done_explicit = $drive_steps(S_explicit,20000)',
        'S_done_explicit.COMPLETION = NORMAL',
        '$ctor_review_output(S_done_explicit.EVENTS) = $ptascii("H|1|2|3|")',
    ]
    return checks


def prepare(out, group):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    fixtures = []
    try:
        for path in SELECTIONS[group]:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']; fixtures.append(checked['fixture'])
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = exit_checks(fixtures, SELECTIONS[group]) if group == 'exit' else globals()[group](fixtures[0], SELECTIONS[group][0])
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *SELECTIONS[args.group], *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
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

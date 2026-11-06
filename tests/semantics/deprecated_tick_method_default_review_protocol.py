#!/usr/bin/env python3
"""Check tick calling-row owners and rejected extra defaults."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_tick_method_default_review'
SELECTIONS = {'owners': SOURCE / 'calling-row-owners.php',
    'reject': SOURCE / 'type-cache.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

SELECTED = r'''

dec $tick_review_ready(pstate,nat) : bool
def $tick_review_ready(S,0) = true
  -- if S.TODO = (DEFAULT_BIND porigin n_index) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if $tick_context_kind(S,pcallcontext)
def $tick_review_ready(S,1) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin n_index) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if $tick_context_kind(S,pcallcontext)
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,n_index) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $tick_review_ready(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (TICK_RESULT ptickdispatch) :: ptask_tail*
def $tick_review_ready(S,n) = false -- otherwise
dec $tick_review_pause(pstate,nat,nat) : pstate
def $tick_review_pause(S,n_mode,n) = S -- if $tick_review_ready(S,n_mode)
def $tick_review_pause(S,n_mode,n) = $tick_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$tick_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $tick_review_pause(S,n_mode,n) = S -- otherwise
'''


def start(fixture, path, index):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],10000)',
        'S_warn.CURRENT = (pcallcontext)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        'pcallcontext.TARGET = CALLBACK_BORROWED_TARGET pcalltarget',
        '$tick_context_valid(S_warn,pcallcontext)',
        '$tick_context_call(pcallcontext,S_warn.CURRENT,S_warn.FRAMES) = (ptickdispatch)',
        '$tick_selected(S_warn,ptickdispatch) = (ptickentry)',
        'ptickentry.ENTRY.TARGET = pcalltarget',
        'pcallcontext.CALLSITE = (ptickdispatch.SITE)',
        'pcallcontext.LINE = ptickdispatch.MARKER.LINE',
        'pcallcontext.ARGC = |ptickdispatch.SENT|',
        'pcallcontext.ARGC = |ptickentry.ENTRY.ARGS|',
        'pcallcontext.ARGC = ' + str(index),
        '$parameter_tick_current(S_warn,pfunction) = (ptickreceive)',
        'ptickreceive.ID = ptickentry.ID',
        'ptickreceive.REGISTRATION = ptickentry.ENTRY.CALL.SITE',
        'ptickreceive.LINE = ptickentry.ENTRY.CALL.LINE',
        'ptickreceive.MARKER = ptickdispatch.MARKER',
        'ptickreceive.TARGET = pcalltarget',
        'pcallcontext.RECEIVER = (n_receiver)',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S_warn.CURRENT) = eps',
        '$task_nodes(TICK_RESULT ptickdispatch) = eps',
        '$parameter_default_recipient(S_warn,pfunction)',
        '$default_at(pfunction.DEFAULTS,' + str(index) + ') = (pdefault)',
        '$default_receive_recipient(S_warn,pfunction,pdefault)',
        '$parameter_receive_owner(S_warn.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_warn,n_receive) = (preceivebirth)',
        'preceivebirth.ACTIVE', 'preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
        'preceivebirth.TICK_ENTRY = (ptickreceive)',
        'preceivebirth.ENTRY = eps', 'preceivebirth.CONSTRUCTOR_ENTRY = eps',
        'preceivebirth.SHUTDOWN_ENTRY = eps', 'preceivebirth.API_ENTRY = eps',
        '$parameter_receive_cache_entry(S_warn,preceivebirth)',
        '~$parameter_receive_cache_entry(S_warn,preceivebirth[.TICK_ENTRY = eps])',
        '$machine_roots(S_warn[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warn)',
        '$call_descriptors_valid(S_warn)']


def owners(fixture, path):
    checks = start(fixture, path, 1)
    checks += [
        'ptickentry.ENTRY.ARGS = [POBJECT n_payload]',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_receiver) = 3',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_payload) = 3',
        'S_bind = $tick_review_pause(S_warn,0,10000)', '$tick_review_ready(S_bind,0)',
        'S_bind.CURRENT = (pcallcontext_bind)',
        '$parameter_tick_current(S_bind,pfunction) = (ptickreceive)',
        '$tick_entry_at(S_bind.TICKENTRIES,ptickreceive.ID) = (ptickentry)',
        '$tick_is_calling(S_bind,ptickreceive.ID)',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_bind),HOBJECT n_payload) = 2',
        '(HOBJECT n_receiver) <- S_bind.ALLOCATIONS', '(HOBJECT n_payload) <- S_bind.ALLOCATIONS',
        '$ctor_review_output(S_bind.EVENTS) = $ptascii("A|H|K|W|")',
        '$call_context_roots(S_bind.CURRENT) = eps',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = eps',
        '$call_descriptors_valid(S_bind)',
        'S_zero = $drive(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'S_one_raw = $drive(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_one,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$default_cache_at(S_one.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$lookup(S_one.ENV,pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_formal)',
        'S_one.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '$call_descriptors_valid(S_one)',
        'S_result = $tick_review_pause(S_one,2,10000)', '$tick_review_ready(S_result,2)',
        '$ctor_review_output(S_result.EVENTS) = $ptascii("A|H|K|W|B|7|E|L|")',
        '$heap_owners($heap_graph(S_result),HOBJECT n_payload) = 1',
        '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 2',
        '$tick_entry_at(S_result.TICKENTRIES,ptickreceive.ID) = (ptickentry)',
        '$parameter_receive_cache_entry(S_result,preceivebirth_closed)',
        'S_done = $drive(S_bind,20000)', 'S_done.COMPLETION = NORMAL',
        '$drive(S_one,20000) = S_done',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("A|H|K|W|B|7|E|L|R|P|D|Z|")',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)', '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        '$tick_entry_at(S_done.TICKENTRIES,ptickreceive.ID) = eps',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        'S_erased = S_done[.OBJECTS = eps][.ARRAYS = eps][.TICKENTRIES = eps]',
        '$parameter_receive_cache_entry(S_erased,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_erased,preceivebirth_closed[.TICK_ENTRY = eps])',
        '~$parameter_receive_cache_entry(S_erased,preceivebirth_closed[.PUBLICATION = 0])',
        '~$parameter_receive_tick_witness_valid(S_erased,preceivebirth_closed[.TICK_ENTRY = (ptickreceive[.ID = S_erased.TICKSEQ])])',
        '~$parameter_receive_tick_witness_valid(S_erased,preceivebirth_closed[.TICK_ENTRY = (ptickreceive[.REGISTRATION = preceivebirth.ORIGIN])])',
        '~$parameter_receive_tick_witness_valid(S_erased,preceivebirth_closed[.TICK_ENTRY = (ptickreceive[.MARKER.LINE = $(ptickreceive.MARKER.LINE + 1)])])',
        '~$parameter_receive_tick_witness_valid(S_erased,preceivebirth_closed[.TICK_ENTRY = (ptickreceive[.TARGET = pfunction.ORIGIN])])',
    ]
    return checks


def reject(fixture, path):
    checks = start(fixture, path, 0)
    checks += [
        'ptickentry.ENTRY.ARGS = eps',
        'S_bind = $tick_review_pause(S_warn,0,10000)', '$tick_review_ready(S_bind,0)',
        'S_bind.RESULT = KNOWN (PARRAY n_array)',
        '$default_cache_at(S_bind.DEFAULTCACHE,pdefault.ORIGIN) = eps',
        '$typed_parameter_conversion(S_bind,pfunction.SIGNATURE.PARAMETERS[0],PARRAY n_array) = TYPEREJECT',
        '$parameter_default_error_candidate(S_bind,pfunction,0,PARRAY n_array)',
        'PhpStep: S_bind ~> S_reject',
        'S_reject.COMPLETION = THROWN "TypeError" preqbytes_reject z_reject',
        '$parameter_receive_birth(S_reject,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$default_cache_at(S_reject.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_array',
        '$lookup(S_reject.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_formal)',
        'S_reject.STORE[n_formal] = DEFINED (PARRAY n_array)',
        '$parameter_receive_cache_entry(S_reject,preceivebirth_closed)',
        'S_throw_raw = $drive_steps(S_bind,1)', 'S_throw_raw.COMPLETION = BUDGET',
        'S_throw = S_throw_raw[.COMPLETION = NORMAL]',
        'S_warm = $tick_review_pause(S_throw,1,10000)', '$tick_review_ready(S_warm,1)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        '$tick_context_call(pcallcontext_warm,S_warm.CURRENT,S_warm.FRAMES) = (ptickdispatch_warm)',
        'ptickdispatch_warm.SITE =/= ptickdispatch.SITE',
        'pcallcontext_warm.CALLSITE = (ptickdispatch_warm.SITE)',
        'pcallcontext_warm.LINE = ptickdispatch_warm.MARKER.LINE',
        'pcallcontext_warm.ARGC = 0', 'pcallcontext_warm.RECEIVER = (n_receiver)',
        '$parameter_tick_current(S_warm,pfunction) = (ptickreceive_warm)',
        'ptickreceive_warm.ID = ptickreceive.ID',
        'ptickreceive_warm.MARKER =/= ptickreceive.MARKER',
        '$default_cache_owner(S_warm) = (CACHE_SHARED)',
        '$default_cache_at(S_warm.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        'S_wrong_marker = S_warm[.CURRENT = (pcallcontext_warm[.CALLSITE = pcallcontext.CALLSITE][.LINE = pcallcontext.LINE])]',
        '$parameter_tick_current(S_wrong_marker,pfunction) = eps',
        '~$default_receive_recipient(S_wrong_marker,pfunction,pdefault)',
        '$call_descriptors_valid(S_warm)',
        'PhpStep: S_warm ~> S_warm_reject',
        'S_warm_reject.COMPLETION = THROWN "TypeError" preqbytes_warm z_warm',
        'S_warm_reject.PARAMETERRECEIVES = S_warm.PARAMETERRECEIVES',
        '$lookup(S_warm_reject.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_formal_warm)',
        'S_warm_reject.STORE[n_formal_warm] = DEFINED (PARRAY n_array)',
        'S_done = $drive(S_warm,20000)', 'S_done.COMPLETION = NORMAL',
        '$ctor_review_output(S_done.EVENTS) = $ptascii("A|H|T|Q|T|D|Z|")',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
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
        'tests/semantics/profile.json',
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

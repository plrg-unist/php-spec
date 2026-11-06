#!/usr/bin/env python3
"""Check tick marker selection and closed method-default cache history."""
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
SELECTIONS = {'marker_history': ROOT / 'tests/semantics/deprecated_tick_method_default/inherited-static-markers.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTED = r'''
dec $tick_scope_ready(pstate,nat) : bool
def $tick_scope_ready(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $tick_context_valid(S,pcallcontext)
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 0) :: eps
def $tick_scope_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $tick_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (ptickdispatch)
  -- if $tick_selected(S,ptickdispatch) = (ptickentry)
  -- if ptickentry.ID = 1
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
def $tick_scope_ready(S,n) = false -- otherwise
dec $tick_scope_pause(pstate,nat,nat) : pstate
def $tick_scope_pause(S,n_mode,n) = S -- if $tick_scope_ready(S,n_mode)
def $tick_scope_pause(S,n_mode,n) = $tick_scope_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$tick_scope_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $tick_scope_pause(S,n_mode,n) = S -- otherwise
dec $tick_scope_output_item(pevent) : ptbytes
def $tick_scope_output_item(OUTPUT ptbytes) = ptbytes
def $tick_scope_output_item(pevent) = eps -- otherwise
dec $tick_scope_output(pevent*) : ptbytes
def $tick_scope_output(eps) = eps
def $tick_scope_output(pevent :: pevent_tail*) = $tick_scope_output_item(pevent) ++ $tick_scope_output(pevent_tail*)
'''


def marker_history(fixture, path):
    expected = json.loads((path.parent / 'cases.json').read_text())[path.stem]['stdout'].encode()
    return [
        'U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_bind = $tick_scope_pause(S_start[.COMPLETION = NORMAL],0,20000)',
        '$tick_scope_ready(S_bind,0)',
        'S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        '$parameter_tick_current(S_bind,pfunction) = (ptickreceive)',
        'ptickreceive.ID = 0',
        '$tick_context_call(pcallcontext,S_bind.CURRENT,S_bind.FRAMES) = (ptickdispatch)',
        '$tick_selected(S_bind,ptickdispatch) = (ptickentry)',
        'ptickentry.ID = ptickreceive.ID',
        'ptickentry.ENTRY.TARGET = ptickreceive.TARGET',
        'pcallcontext.CALLSITE = (ptickdispatch.SITE)',
        'ptickreceive.REGISTRATION =/= ptickdispatch.SITE',
        'ptickreceive.LINE = ptickentry.ENTRY.CALL.LINE',
        'ptickreceive.MARKER = ptickdispatch.MARKER',
        '$tick_marker_valid(S_bind,ptickdispatch.SITE,ptickreceive.MARKER)',
        '$parameter_shutdown_target(S_bind,ptickreceive.TARGET) = ((pmethoddesc,porigin_requested,porigin_called,n_receiver_option?))',
        'pmethoddesc.STATIC', 'n_receiver_option? = eps',
        'pmethoddesc.OWNER =/= porigin_called',
        'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext.CALLED_CLASS = (porigin_called)',
        '$call_context_roots(S_bind.CURRENT) = eps',
        '$parameter_receive_owner(S_bind.CURRENT) = (n_receive)',
        '$parameter_receive_birth(S_bind,n_receive) = (preceivebirth)',
        'preceivebirth.TICK_ENTRY = (ptickreceive)',
        '$parameter_receive_source_valid(S_bind,preceivebirth)',
        '$parameter_receive_cache_entry(S_bind,preceivebirth)',
        '$machine_roots(S_bind[.PARAMETERRECEIVES = eps]) = $machine_roots(S_bind)',
        '$default_bind_task_valid(S_bind,pfunction.ORIGIN,0)',
        '$call_descriptors_valid(S_bind)',
        '$parameter_tick_current(S_bind[.CURRENT = (pcallcontext[.CALLSITE = (ptickreceive.REGISTRATION)])],pfunction) = eps',
        '~$parameter_receive_cache_entry(S_bind,preceivebirth[.TICK_ENTRY = eps])',
        '~$parameter_receive_tick_witness_valid(S_bind,preceivebirth[.TICK_ENTRY = (ptickreceive[.REGISTRATION = ptickdispatch.SITE])])',
        '~$parameter_receive_tick_witness_valid(S_bind,preceivebirth[.TICK_ENTRY = (ptickreceive[.TARGET = OUTPUT_BORROWED_TARGET ptickreceive.TARGET])])',
        '~$parameter_receive_tick_witness_valid(S_bind,preceivebirth[.TICK_ENTRY = (ptickreceive[.MARKER = ptickreceive.MARKER[.LINE = $(ptickreceive.MARKER.LINE + 1)]])])',
        '~$parameter_receive_tick_witness_valid(S_bind,preceivebirth[.PUBLICATION = 0])',
        'S_one = $drive_steps(S_bind,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_after,n_receive) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_after,preceivebirth_closed)',
        'S_warm = $tick_scope_pause(S_after,1,20000)', '$tick_scope_ready(S_warm,1)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        'pcallcontext_warm.CALLED_CLASS = (pmethoddesc.OWNER)',
        '$parameter_tick_current(S_warm,pfunction) = (ptickreceive_warm)',
        'ptickreceive_warm.ID = 1',
        'ptickreceive_warm.REGISTRATION =/= ptickreceive.REGISTRATION',
        '$tick_entry_at(S_warm.TICKENTRIES,0) = eps',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_cache', 'S_warm.ARRAYS[n_cache].ITEMS = eps',
        '$default_receive_recipient(S_warm,pfunction,pdefault)',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_warm,preceivebirth_closed[.TICK_ENTRY = (ptickreceive_warm)])',
        '$call_descriptors_valid(S_warm)',
        'S_history = S_warm[.TICKENTRIES = eps][.OBJECTS = eps][.ARRAYS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '$machine_roots(S_warm[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warm)',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        'S_done.PARAMETERSEQ = S_warm.PARAMETERSEQ',
        'S_done.TICKENTRIES = eps',
        '$parameter_receive_cache_entry(S_done,preceivebirth_closed)',
        '$tick_scope_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(expected).decode()) + ')',
    ]


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
    paths = [Path(__file__), SELECTIONS[args.group], *modules, *(ROOT / path for path in (
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

#!/usr/bin/env python3
"""Check selected autoload scopes and shifted default-warning publication cuts."""
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
SELECTIONS = {'scope_cut': ROOT / 'tests/semantics/deprecated_autoload_method_default/inherited-static-lookup-explicit.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTED = r'''
dec $autoload_scope_ready(pstate,nat) : bool
def $autoload_scope_ready(S,0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
def $autoload_scope_ready(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = AUTOLOAD_BORROWED_TARGET pcalltarget
  -- if S.TODO = (DEFAULT_BIND pcallcontext.FUNCTION 1) :: eps
def $autoload_scope_ready(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = AUTOLOAD_BORROWED_TARGET pcalltarget
  -- if pcallcontext.CALLSITE = eps
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 1) :: eps
def $autoload_scope_ready(S,n) = false -- otherwise
dec $autoload_scope_pause(pstate,nat,nat) : pstate
def $autoload_scope_pause(S,n_mode,n) = S -- if $autoload_scope_ready(S,n_mode)
def $autoload_scope_pause(S,n_mode,n) = $autoload_scope_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$autoload_scope_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $autoload_scope_pause(S,n_mode,n) = S -- otherwise
dec $autoload_scope_output_item(pevent) : ptbytes
def $autoload_scope_output_item(OUTPUT ptbytes) = ptbytes
def $autoload_scope_output_item(pevent) = eps -- otherwise
dec $autoload_scope_output(pevent*) : ptbytes
def $autoload_scope_output(eps) = eps
def $autoload_scope_output(pevent :: pevent_tail*) = $autoload_scope_output_item(pevent) ++ $autoload_scope_output(pevent_tail*)
'''


def scope_cut(fixture, path):
    expected = json.loads((path.parent / 'cases.json').read_text())[path.stem]['stdout'].encode()
    return [
        'U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_cut = $autoload_scope_pause(S_start[.COMPLETION = NORMAL],0,20000)',
        '$autoload_scope_ready(S_cut,0)',
        'S_cut.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$parameter_receive_define_registration(S_cut,pconfigcall) = [preceivecut]',
        '$parameter_receive_birth(S_cut,preceivecut.OWNER) = (preceivebirth)',
        'preceivebirth.ACTIVE', 'preceivecut.INDEX = 1',
        '$declaration_autoload_at(preceivebirth.CAUSE.AUTOLOAD,0) = ((pautoloadcall,pautoloadentry))',
        'preceivebirth.CAUSE.AUTOLOAD = [(0,pautoloadcall,pautoloadentry)]',
        'preceivecut.CAUSE.AUTOLOAD = [(1,pautoloadcall,pautoloadentry)]',
        '$parameter_receive_cut_autoload(preceivecut,preceivebirth)',
        '$parameter_receive_cut_source(S_cut,preceivecut)',
        '~$parameter_receive_cut_source(S_cut,preceivecut[.CAUSE = preceivecut.CAUSE[.AUTOLOAD = eps]])',
        '~$parameter_receive_cut_source(S_cut,preceivecut[.CAUSE = preceivecut.CAUSE[.AUTOLOAD = preceivebirth.CAUSE.AUTOLOAD]])',
        '~$parameter_receive_cut_autoload(preceivecut[.CAUSE = preceivecut.CAUSE[.AUTOLOAD = [(1,pautoloadcall[.NAME = $ptascii("Wrong204")],pautoloadentry)]]],preceivebirth)',
        '$parameter_receive_cache_entry(S_cut,preceivebirth)',
        '$autoload_method_entry(S_cut,pautoloadentry) = ((pmethoddesc,porigin_requested,porigin_called,n_receiver_option?))',
        'pmethoddesc.STATIC', 'n_receiver_option? = eps',
        'pmethoddesc.OWNER =/= porigin_called', 'porigin_requested = porigin_called',
        'pautoloadcall.MODE = AUTO_LOOKUP',
        'preceivebirth.CALLSITE = (pautoloadcall.SITE)',
        'pautoloadcall.KEY = $ptlc(pautoloadcall.NAME)',
        '$machine_roots(S_cut[.PARAMETERRECEIVES = eps]) = $machine_roots(S_cut)',
        'S_bind = $autoload_scope_pause(S_cut,1,20000)', '$autoload_scope_ready(S_bind,1)',
        'S_bind.CURRENT = (pcallcontext)',
        '$receiving_function(S_bind,pcallcontext.FUNCTION) = (pfunction)',
        'pfunction = pmethoddesc.FUNCTION',
        'pcallcontext.TARGET = AUTOLOAD_BORROWED_TARGET pcalltarget',
        'pautoloadentry.TARGET = AUTO_TARGET pcalltarget',
        '$target_function(S_bind,pcallcontext.TARGET) = (pfunction)',
        '$target_lexical_class(S_bind,pcallcontext.TARGET) = (pmethoddesc.OWNER)',
        '$target_called_class(S_bind,pcallcontext.TARGET) = (porigin_called)',
        '$parameter_autoload_current(S_bind,pfunction)',
        '$default_bind_task_valid(S_bind,pfunction.ORIGIN,1)',
        '$call_descriptors_valid(S_bind)',
        'S_one = $drive_steps(S_bind,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]',
        '$parameter_receive_birth(S_after,preceivecut.OWNER) = (preceivebirth_closed)',
        '~preceivebirth_closed.ACTIVE',
        '$parameter_receive_cache_entry(S_after,preceivebirth_closed)',
        'S_warm = $autoload_scope_pause(S_after,2,20000)', '$autoload_scope_ready(S_warm,2)',
        'S_warm.CURRENT = (pcallcontext_warm)',
        '$autoload_context_call(pcallcontext_warm,S_warm.CURRENT,S_warm.FRAMES) = ((pautoloadcall_warm,pautoloadentry_warm,poperand_warm))',
        'pautoloadcall_warm.MODE = AUTO_EXPLICIT pconfigcall_warm',
        'pcallcontext_warm.LINE = $(-1)', 'pcallcontext_warm.ARGC = 1',
        'pcallcontext_warm.FUNCTION = pfunction.ORIGIN',
        'pcallcontext_warm.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_warm.CALLED_CLASS = (pmethoddesc.OWNER)',
        'pautoloadentry_warm.BIRTH =/= pautoloadentry.BIRTH',
        '$parameter_receive_owner(S_warm.CURRENT) = eps',
        '$default_cache_owner(S_warm) = (CACHE_SHARED)',
        '$parameter_autoload_current(S_warm,pfunction)',
        '$default_at(pfunction.DEFAULTS,1) = (pdefault)',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_cache', 'S_warm.ARRAYS[n_cache].ITEMS = eps',
        '$parameter_receive_cache_entry(S_warm,preceivebirth_closed)',
        '~$parameter_receive_cache_entry(S_warm,preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.AUTOLOAD = [(1,pautoloadcall,pautoloadentry)]]])',
        '~$parameter_receive_cache_entry(S_warm,preceivebirth_closed[.CAUSE = preceivebirth_closed.CAUSE[.AUTOLOAD = [(0,pautoloadcall,pautoloadentry_warm)]]])',
        'S_history = S_warm[.AUTOLOAD.ENTRIES = eps][.AUTOLOAD.BIRTHS = eps][.OBJECTS = eps][.ARRAYS = eps]',
        '$parameter_receive_cache_entry(S_history,preceivebirth_closed)',
        '$machine_roots(S_warm[.PARAMETERRECEIVES = eps]) = $machine_roots(S_warm)',
        '$call_descriptors_valid(S_warm)',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        'S_done.PARAMETERSEQ = S_warm.PARAMETERSEQ',
        '$autoload_scope_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(expected).decode()) + ')',
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

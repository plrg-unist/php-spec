#!/usr/bin/env python3
"""Reach computed cache replacement and its actual cleanup/publication fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_class_constant_owned_review_protocol import EXTRA, start
from deprecated_global_constant_protocol import PREFIX, nodes
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/class_constant_replacement_review'
SELECTIONS = {'image': 'earlier-array-prefix', 'pending': 'pending-new-closure'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

EXTRA += r'''
dec $computed_drop_ready(pstate) : bool
def $computed_drop_ready(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_drop)
  -- if S.OBJECTS[n_drop] = INSTANCE porigin_drop
  -- if $class_at(S.CLASSES,porigin_drop) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Drop195")
  -- if $destructor_method(S,n_drop) = (pmethoddesc)
  -- if pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
def $computed_drop_ready(S) = false -- otherwise
dec $computed_drop_pause(pstate,nat) : pstate
def $computed_drop_pause(S,n) = S -- if $computed_drop_ready(S)
def $computed_drop_pause(S,n) = $computed_drop_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$computed_drop_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $computed_drop_pause(S,n) = S -- otherwise
'''


def binder(entered='S_warn'):
    return ['S_bind = $class_owned_parent_pause(' + entered + ',pclassconstantcontext,10000)',
        'S_bind.COMPLETION = NORMAL',
        'S_bind.TODO = (CLASS_CONST_BIND pclassconstantcontext.DECL) :: ptask_bind*',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        '$class_constant_pending_cache(S_bind,pclassconstantcontext)',
        '$call_descriptors_valid(S_bind)',
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_old)',
        'pdefaultcache_old.VALUE = PARRAY n_old',
        'S_bind.RESULT = KNOWN (PARRAY n_new)', 'n_old =/= n_new',
        '(HARRAY n_old) <- S_bind.ALLOCATIONS', '(HARRAY n_new) <- S_bind.ALLOCATIONS',
        '$heap_owners($heap_graph(S_bind),HARRAY n_old) = 1',
        '$heap_owners($heap_graph(S_bind),HARRAY n_new) = 1']


def staged(budget=False):
    zero = ['S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero.CLASSCONSTANTWRITES = eps',
        'S_zero.CLASSCONSTANTCACHE = S_bind.CLASSCONSTANTCACHE',
        'S_zero.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        'S_stage = $drive_steps(S_zero[.COMPLETION = NORMAL],1)'] if budget else [
        'S_stage = $drive_steps(S_bind,1)']
    return zero + ['S_stage.COMPLETION = BUDGET',
        '|S_stage.CLASSCONSTANTWRITES| = 1',
        'S_stage.RESULT = KNOWN PNULL',
        'S_stage.CLASSCONSTANTCACHE = S_bind.CLASSCONSTANTCACHE',
        'S_stage.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        '$heap_owners($heap_graph(S_stage),HARRAY n_old) = 1',
        '~((HARRAY n_old) <- $class_constant_machine_roots(S_stage))',
        '$heap_owners($heap_graph(S_stage),HARRAY n_new) = 1',
        '(HARRAY n_new) <- $tasks_nodes(S_stage.TODO)',
        '$class_constant_history_valid(S_stage)', '$call_descriptors_valid(S_stage)']


def finished(compare=False):
    checks = ['S_done = $drive_steps(S_stage[.COMPLETION = NORMAL],10000)',
        'S_done.COMPLETION = NORMAL', 'S_done.CLASSCONSTANTWRITES = eps',
        '$call_descriptors_valid(S_done)',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_new)',
        'pdefaultcache_new.VALUE = PARRAY n_new',
        '~((HARRAY n_old) <- S_done.ALLOCATIONS)', '(HARRAY n_new) <- S_done.ALLOCATIONS',
        '$class_constant_history_valid(S_done)',
        '$owned_class_last_write(S_done.CLASSCONSTANTHISTORY,pclassconstantcontext.DECL) = (pclassconstantevent)',
        '$constant_callable_cache_event(pclassconstantevent) = ((pclassconstantcontext.DECL,n_prefix))',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)']
    return checks + (['S_full = $drive_steps(S_bind,10000)', 'S_full.COMPLETION = NORMAL',
        'S_done.EVENTS = S_full.EVENTS',
        'S_done.CLASSCONSTANTCACHE = S_full.CLASSCONSTANTCACHE',
        'S_done.CLASSCONSTANTHISTORY = S_full.CLASSCONSTANTHISTORY'] if compare else [])


def image(fixture, path, response):
    return start(fixture, path) + [
        'S_wait = $drive_steps(S_warn,10000)', 'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')', 'S_entered.COMPLETION = NORMAL'
    ] + binder('S_entered') + [
        'S_bind.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]'
    ] + staged() + finished() + [
        '$class_constant_compile_entry(S_done,1) = (S_projection)',
        '$default_cache_at(S_projection.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_projection)',
        'pdefaultcache_projection.VALUE = PARRAY n_projection',
        'S_projection.ARRAYS[n_projection].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$constant_value_class_valid(S_projection,pdefaultcache_projection.VALUE,pdefaultcache_projection.CLASS)',
        '$constant_callable_foldable(pdefaultcache_projection.CLASS)',
        'S_projection.ARRAYS[n_projection].NEXT = S_bind.ARRAYS[n_old].NEXT',
        'S_projection.ARRAYS[n_projection].POSITIONS = S_bind.ARRAYS[n_old].POSITIONS',
        'S_projection.ARRAYS[n_projection].SERIAL = S_bind.ARRAYS[n_old].SERIAL']


def pending(fixture, path):
    return start(fixture, path) + binder() + [
        'S_bind.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old_closure)),ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'S_bind.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new_closure)),ENTRY (KINT 1) (DIRECT (PARRAY n_empty))]',
        'n_old_closure =/= n_new_closure'
    ] + staged(budget=True) + [
        'S_drop = $computed_drop_pause(S_stage[.COMPLETION = NORMAL],10000)',
        'S_drop.COMPLETION = NORMAL', '$computed_drop_ready(S_drop)',
        '|S_drop.CLASSCONSTANTWRITES| = 1',
        '~((HARRAY n_old) <- S_drop.ALLOCATIONS)',
        '~((HOBJECT n_old_closure) <- S_drop.ALLOCATIONS)',
        '(HARRAY n_new) <- S_drop.ALLOCATIONS',
        '(HOBJECT n_new_closure) <- S_drop.ALLOCATIONS',
        '$heap_owners($heap_graph(S_drop),HARRAY n_new) = 1',
        '$heap_owners($heap_graph(S_drop),HOBJECT n_new_closure) = 1',
        '$class_constant_state_valid(S_drop)', '$gc_state_valid(S_drop)',
        '$destruction_state_valid(S_drop)', '$constant_context_valid(S_drop)'
    ] + finished(compare=True) + [
        '|S_done.CLASSCONSTANTCACHE| = 2',
        '~((HOBJECT n_old_closure) <- S_done.ALLOCATIONS)',
        '(HOBJECT n_new_closure) <- S_done.ALLOCATIONS']


def prepare(out, group):
    path = SOURCE / (SELECTIONS[group] + '.php')
    frontend = Worker(types.frontend_command(), out / 'frontend', seconds=30)
    adapter = Worker([str(types.ADAPTER)], out / 'adapter', seconds=45)
    try:
        parsed = frontend.request({'op': 'parse', 'id': '0', 'path': base64.b64encode(bytes(path)).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        if group == 'image':
            code, = [base64.b64decode(node['fields'][0]['bytes']) for node, _ in nodes(parsed['ast']['program'])
                if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'const SNAP195 =')]
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
            assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
            checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
            response = 'SOURCE_ACCEPT 1 ($ptascii(' + json.dumps(code.decode()) + ')) ' + checked_eval['fixture']
            (out / 'eval-source.php').write_bytes(code)
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = image(checked['fixture'], path, response) if group == 'image' else pending(checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', choices=tuple(SELECTIONS), required=True)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE / (SELECTIONS[args.group] + '.php'), *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'tests/semantics/deprecated_class_constant_owned_review_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', '.tools/php/bin/php',
        '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
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

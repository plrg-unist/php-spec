#!/usr/bin/env python3
"""Check real named array-leaf COW and every ancestor of a quiet object leaf."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
from direct_stdclass_reference_notice_review_cases import CASES

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $dol_output(pevent*) : ptbytes
def $dol_output(eps) = eps
def $dol_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $dol_output(pevent*)
dec $dol_stage(pstate, nat) : bool
def $dol_stage(S, 0) = $named_reference_notice_pending(S)
def $dol_stage(S, 1) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask*
def $dol_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $dol_output(S.EVENTS) = $ptascii("1:7;")
def $dol_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if $dol_output(S.EVENTS) = $ptascii("1:7;9:77:1:0;9:13:99;")
  -- if $lookup(S.ENV, $ptascii("copy")) = eps
  -- if $lookup(S.ENV, $ptascii("outside")) = (n_outside)
  -- if S.STORE[n_outside] = DEFINED (POBJECT n)
  -- if $heap_owners($heap_graph(S), HOBJECT n) = 1
def $dol_stage(S, n) = false -- otherwise
dec $dol_seek(pstate, nat, nat) : pstate
def $dol_seek(S, n_stage, n) = S
  -- if $dol_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $dol_seek(S, n_stage, n) = $dol_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$dol_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $dol_seek(S, n_stage, n) = S -- otherwise
'''

REACHED = r'''
S_pre = $dol_seek(S_initial, 0, 1024)[.COMPLETION = NORMAL]
$dol_stage(S_pre, 0)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("held")) = (n_held)
$lookup(S_pre.ENV, $ptascii("weak")) = (n_weak_cell)
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.STORE[n_held] = DEFINED (POBJECT n_old)
S_pre.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_old))]
$node_children(S_pre, HARRAY n_root) = [HOBJECT n_old]
$node_children(S_pre, HOBJECT n_old) = eps
S_pre.OBJECTS[n_weak] = WEAKREFERENCE (n_old)
$weakref_get(S_pre, n_weak) = POBJECT n_old
$objectprops_record_at(S_pre.OBJECTPROPS, n_old) = (pobjectprops_old)
pobjectprops_old.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_object_ancestors(S_pre, [n_root])
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after = {SLOTS ([NAMED_SENT (REFERENCE n_private)]), NAMED eps}
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$node_children(S_notice, HARRAY n_root) = [HOBJECT n_old]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HARRAY n_root) = 3
$heap_owners(H_notice, HOBJECT n_old) = 2
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = S_pre.HELD
$named_reference_notice_operand(S_notice, REFERENCE n_private)
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_resume = $dol_seek(S_notice, 1, 1024)[.COMPLETION = NORMAL]
$dol_stage(S_resume, 1)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("source")) = (n_source)
$lookup(S_resume.ENV, $ptascii("held")) = eps
S_resume.STORE[n_source] = DEFINED (PARRAY n_replacement)
n_replacement =/= n_root
S_resume.ARRAYS[n_replacement].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_new))]
n_new =/= n_old
$objectprops_at(S_resume.OBJECTPROPS, n_new) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 77)))}])
$objectprops_at(S_resume.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 7)))}])
S_resume.STORE[n_private] = DEFINED (PARRAY n_root)
S_resume.STORE[n_copy] = DEFINED (PARRAY n_root)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_private) = 1
$heap_owners(H_resume, HARRAY n_root) = 2
$heap_owners(H_resume, HOBJECT n_old) = 1
$heap_owners(H_resume, HOBJECT n_new) = 1
$error_call_valid(S_resume, perrorcall) /\ $call_descriptors_valid(S_resume)
$heap_valid(H_resume)
S_returned = $dol_seek(S_resume, 2, 1024)[.COMPLETION = NORMAL]
$dol_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root /\ n_copied =/= n_replacement
S_returned.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_old)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 99))]
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
$node_children(S_returned, HARRAY n_root) = [HOBJECT n_old]
$node_children(S_returned, HARRAY n_copied) = [HOBJECT n_old]
$objectprops_at(S_returned.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 9)))}])
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HOBJECT n_old) = 2
$heap_owners(H_returned, HOBJECT n_new) = 1
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_outside = $dol_seek(S_returned, 3, 1024)[.COMPLETION = NORMAL]
$dol_stage(S_outside, 3)
$lookup(S_outside.ENV, $ptascii("outside")) = (n_outside)
S_outside.STORE[n_outside] = DEFINED (POBJECT n_old)
S_outside.STORE[n_private] = DEFINED (PARRAY n_copied)
S_outside.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (PINT 13)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 99))]
$node_children(S_outside, HARRAY n_copied) = eps
$weakref_get(S_outside, n_weak) = POBJECT n_old
H_outside = $heap_graph(S_outside)
$heap_owners(H_outside, HOBJECT n_old) = 1
$heap_owners(H_outside, HARRAY n_root) = 0
~((HARRAY n_root) <- S_outside.ALLOCATIONS)
$call_descriptors_valid(S_outside) /\ $heap_valid(H_outside)
S_full = $drive(S_outside, 1024)
S_full.COMPLETION = NORMAL
$dol_output(S_full.EVENTS) = $ptascii("1:7;9:77:1:0;9:13:99;1;1;")
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
$lookup(S_full.ENV, $ptascii("outside")) = eps
$lookup(S_full.ENV, $ptascii("copy")) = eps
$weakref_get(S_full, n_weak) = PNULL
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_private) = 1
$heap_owners(H_full, HOBJECT n_old) = 0
~((HOBJECT n_old) <- S_full.ALLOCATIONS)
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid(H_full)
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_notice, 1)
S_split = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_split = S_direct
'''.strip().splitlines()

DERIVED = r'''
~$named_reference_notice_entries(S_pre, S_pre.ARRAYS[n_root].ITEMS)
S_alias_object = $reference_cell(S_pre[.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (ALIAS n_held)]], n_held)
~$named_reference_notice_array(S_alias_object, PARRAY n_root)
S_bad_object = S_pre[.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT (|S_pre.OBJECTS|)))]]
~$named_reference_notice_array(S_bad_object, PARRAY n_root)
S_object_unit = S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HOBJECT n_old]]
~$named_reference_notice_array(S_object_unit, PARRAY n_root)
S_object_table = S_pre[.OBJECTTABLES = [{OBJECT n_old, TABLE n_root}]]
~$named_reference_notice_array(S_object_table, PARRAY n_root)
S_owning_slot = S_pre[.OBJECTPROPS = [pobjectprops_old[.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (POBJECT n_old)))}]]]]
~$named_reference_notice_array(S_owning_slot, PARRAY n_root)
n_leaf = |S_pre.ARRAYS|
parray_leaf = $array_insert($array_insert($array_empty(), KINT 0, DIRECT (POBJECT n_old)), KINT 1, DIRECT (POBJECT n_old))
S_leaf = $allocate_array(S_pre, parray_leaf)
S_leaf.RESULT = KNOWN (PARRAY n_leaf)
n_mid = |S_leaf.ARRAYS|
S_mid = $allocate_array(S_leaf, $array_insert($array_empty(), KINT 0, DIRECT (PARRAY n_leaf)))
S_mid.RESULT = KNOWN (PARRAY n_mid)
S_chain = S_mid[.ARRAYS[n_root] = $array_insert($array_empty(), KINT 0, DIRECT (PARRAY n_mid))][.RESULT = S_pre.RESULT]
$named_reference_notice_array(S_chain, PARRAY n_root)
$named_reference_notice_object_ancestors(S_chain, [n_leaf, n_mid, n_root])
$node_children(S_chain, HARRAY n_leaf) = [HOBJECT n_old, HOBJECT n_old]
$heap_owners($heap_graph(S_chain), HOBJECT n_old) = 3
S_dag = S_chain[.ARRAYS[n_root] = $array_insert(S_chain.ARRAYS[n_root], KINT 1, DIRECT (PARRAY n_mid))]
$named_reference_notice_array(S_dag, PARRAY n_root)
$heap_owners($heap_graph(S_dag), HARRAY n_mid) = 2
$heap_owners($heap_graph(S_dag), HARRAY n_leaf) = 1
$heap_owners($heap_graph(S_dag), HOBJECT n_old) = 3
S_array_alias = $reference_cell(S_chain[.STORE[n_held] = DEFINED (PARRAY n_mid)][.ARRAYS[n_root] = $array_insert($array_empty(), KINT 0, ALIAS n_held)], n_held)
$named_reference_notice_array(S_array_alias, PARRAY n_root)
$node_children(S_array_alias, HCELL n_held) = [HARRAY n_mid]
$heap_owners($heap_graph(S_array_alias), HOBJECT n_old) = 2
S_cycle = S_chain[.ARRAYS[n_leaf] = $array_insert($array_empty(), KINT 0, DIRECT (PARRAY n_root))]
~$named_reference_notice_array(S_cycle, PARRAY n_root)
S_alias_cycle = S_array_alias[.STORE[n_held] = DEFINED (PARRAY n_root)]
~$named_reference_notice_array(S_alias_cycle, PARRAY n_root)
S_pre.POOLS = ppool :: ppool_tail*
'''.strip().splitlines()

for label, node in (('root', 'n_root'), ('middle', 'n_mid'), ('leaf', 'n_leaf')):
    for history, field in (('retained', 'LITERALARRAYRETAINED'), ('debt', 'LITERALARRAYDEBTS')):
        name = 'S_' + label + '_' + history
        DERIVED += [f'{name} = S_chain[.{field} = S_chain.{field} ++ [{node}]]',
                    f'~$named_reference_notice_array({name}, PARRAY n_root)']
    DERIVED += [
        f'S_{label}_unit = S_chain[.NATIVEEXCESS = S_chain.NATIVEEXCESS ++ [HARRAY {node}]]',
        f'~$named_reference_notice_array(S_{label}_unit, PARRAY n_root)',
        f'S_{label}_dead = S_chain[.ALLOCATIONS = $call_remove_owner(S_chain.ALLOCATIONS, HARRAY {node})]',
        f'~$named_reference_notice_array(S_{label}_dead, PARRAY n_root)',
        f'S_{label}_pool = S_chain[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY {node})]] :: ppool_tail*]',
        f'~$named_reference_notice_array(S_{label}_pool, PARRAY n_root)',
    ]

DERIVED += r'''
S_empty_immutable = S_chain[.ARRAYS[n_mid] = $array_empty()][.GC.IMMUTABLE = S_chain.GC.IMMUTABLE ++ [n_mid]]
~$named_reference_notice_object_ancestors(S_empty_immutable, [n_leaf, n_mid, n_root])
~$named_reference_notice_object_ancestors(S_chain, [n_leaf, (|S_chain.ARRAYS|), n_root])
S_plain = S_chain[.ARRAYS[n_leaf] = $array_insert($array_empty(), KINT 0, DIRECT (PINT 5))]
S_old_root = S_plain[.LITERALARRAYRETAINED = [n_root]][.LITERALARRAYDEBTS = [n_root]][.NATIVEEXCESS = [HARRAY n_root]]
$named_reference_notice_array(S_old_root, PARRAY n_root)
S_old_scalar = S_pre[.ARRAYS[n_root] = $array_insert($array_empty(), KINT 0, DIRECT (PINT 5))][.LITERALARRAYRETAINED = [n_root]][.LITERALARRAYDEBTS = [n_root]][.NATIVEEXCESS = [HARRAY n_root]]
$named_reference_notice_array(S_old_scalar, PARRAY n_root)
S_root_debt = S_pre[.LITERALARRAYDEBTS = S_pre.LITERALARRAYDEBTS ++ [n_root]]
~$named_reference_notice_pending(S_root_debt)
S_rejected = $drive(S_root_debt, 1)
S_rejected.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    native_path = args.native_provenance.resolve()
    native = json.loads(native_path.read_bytes())
    source = Path(native['command'][-1])
    assert native['passed'] and native['mode'] == 'native-only'
    assert source.read_bytes() == CASES[native['id']]
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='direct-stdclass-reference-review-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), native_path, source,
        ROOT / 'tests/semantics/direct_stdclass_reference_notice_review_cases.py',
        ROOT / 'tests/semantics/direct_stdclass_reference_notice_review_cases.json',
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
    else:
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
            base64.b64encode(os.fsencode(source)).decode()) + ')'
        checks = [initial] + REACHED + DERIVED
        fixture = directory / 'state.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + check + '\n' for check in checks))
        prepared = {'revision': revision, 'inputs': before, 'source': str(source),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'conditions': len(checks), 'reached_conditions': len(REACHED) + 1,
            'derived_conditions': len(DERIVED), 'heap_bindings': 6,
            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
        (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture = directory / 'state.watsup'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 480)
    stable = before == fingerprints() and hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable,
        module_count=len(modules), mode='AL/cache=false/det=true',
        process=process, passed=passed, source_agreements=0)
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('named DIRECT object-leaf ownership/ancestor refusals/budget', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

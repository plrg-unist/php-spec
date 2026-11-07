#!/usr/bin/env python3
"""Check a named property-only type source, COW aliases, rejection and live-source refusals."""
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
from typed_alias_stdclass_reference_notice_review_cases import CASES

ROOT = Path(__file__).resolve().parents[2]

PREFIX = r'''
dec $tsn_output(pevent*) : ptbytes
def $tsn_output(eps) = eps
def $tsn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $tsn_output(pevent*)
dec $tsn_stage(pstate, nat) : bool
def $tsn_stage(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if $tsn_output(S.EVENTS) = $ptascii("A;")
def $tsn_stage(S, 1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask*
  -- if $tsn_output(S.EVENTS) = $ptascii("A;H;")
def $tsn_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $tsn_output(S.EVENTS) = $ptascii("A;H;F;")
def $tsn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $tsn_output(S.EVENTS) = $ptascii("A;H;F;1:1:1:5;")
def $tsn_stage(S, n) = false -- otherwise
dec $tsn_seek(pstate, nat, nat) : pstate
def $tsn_seek(S, n_stage, n) = S
  -- if $tsn_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $tsn_seek(S, n_stage, n) = $tsn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$tsn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tsn_seek(S, n_stage, n) = $tsn_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$tsn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $tsn_seek(S, n_stage, n) = S -- otherwise
'''

PRE = r'''
S_pre = $tsn_seek(S_initial, 0, 768)[.COMPLETION = NORMAL]
$tsn_stage(S_pre, 0)
$named_reference_notice_pending(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("holder")) = (n_holder_cell)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cell)
$lookup(S_pre.ENV, $ptascii("replacement")) = (n_new_cell)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
S_pre.STORE[n_holder_cell] = DEFINED (POBJECT n_holder)
S_pre.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cell] = DEFINED (POBJECT n_new)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
n_old =/= n_new /\ n_holder =/= n_old /\ n_holder =/= n_new
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_holder ($ptascii("p")) ppropertyid]
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_holder ($ptascii("p")) ppropertyid)
$propref_descriptor(S_pre, OBJECT_PROP_SOURCE n_holder ($ptascii("p")) ppropertyid) = (ppropertydesc)
ppropertydesc.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
$ptlc(ptbytes_type) = $ptascii("stdclass")
S_pre.OBJECTS[n_holder] = INSTANCE porigin_holder
S_pre.CLASSES = [pclassdesc]
pclassdesc.ORIGIN = porigin_holder /\ pclassdesc.PROPERTIES = [ppropertydesc]
$objectprops_record_at(S_pre.OBJECTPROPS, n_holder) = (pobjectprops_holder)
pobjectprops_holder.SLOTS = [{DECL (ppropertyid), NAME ($ptascii("p")), STATE (PROP_VALUE (ALIAS n_leaf))}]
$node_children(S_pre, HOBJECT n_holder) = [HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_operand(S_pre, REFERENCE n_leaf)
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 3
$heap_owners(H_pre, HOBJECT n_holder) = 1
$heap_owners(H_pre, HOBJECT n_old) = 2
$heap_owners(H_pre, HOBJECT n_new) = 1
(HOBJECT n_holder) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

OWNERSHIP = r'''
n_private = |S_pre.STORE|
S_one = $drive(S_pre, 1)
S_one.COMPLETION = BUDGET
S_notice = S_one[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after = {SLOTS ([NAMED_SENT (REFERENCE n_private)]), NAMED eps}
$propref_at(S_notice.PROPREFS, n_leaf) = (ppropref)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
S_resume = $tsn_seek(S_notice, 1, 768)[.COMPLETION = NORMAL]
$tsn_stage(S_resume, 1)
$lookup(S_resume.ENV, $ptascii("leaf")) = eps
$propref_at(S_resume.PROPREFS, n_leaf) = (ppropref)
$objectprops_record_at(S_resume.OBJECTPROPS, n_holder) = (pobjectprops_holder)
S_resume.STORE[n_leaf] = DEFINED (POBJECT n_new)
$node_children(S_resume, HCELL n_leaf) = [HOBJECT n_new]
$duplicate_item(S_resume, n_root, ALIAS n_leaf) = ALIAS n_leaf
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HARRAY n_root) = 3
$heap_owners(H_resume, HCELL n_private) = 1
$heap_owners(H_resume, HCELL n_leaf) = 2
$heap_owners(H_resume, HOBJECT n_holder) = 1
$heap_owners(H_resume, HOBJECT n_new) = 2
$heap_owners(H_resume, HOBJECT n_old) = 1
$proprefs_valid(S_resume) /\ $call_descriptors_valid(S_resume) /\ $heap_valid(H_resume)
S_returned = $tsn_seek(S_resume, 2, 768)[.COMPLETION = NORMAL]
$tsn_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
$propref_at(S_returned.PROPREFS, n_leaf) = (ppropref)
$objectprops_record_at(S_returned.OBJECTPROPS, n_holder) = (pobjectprops_holder)
S_returned.STORE[n_leaf] = DEFINED (POBJECT n_new)
$node_children(S_returned, HARRAY n_copied) = [HCELL n_leaf]
$node_children(S_returned, HCELL n_leaf) = [HOBJECT n_new]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HARRAY n_root) = 2
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_leaf) = 3
$heap_owners(H_returned, HOBJECT n_holder) = 1
$heap_owners(H_returned, HOBJECT n_new) = 2
$heap_owners(H_returned, HOBJECT n_old) = 1
$proprefs_valid(S_returned) /\ $call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_zero = $drive(S_returned, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_returned
S_split = $drive($drive(S_returned, 1)[.COMPLETION = NORMAL], 1)
S_split = $drive(S_returned, 2)
S_reject = $tsn_seek(S_returned, 3, 768)[.COMPLETION = NORMAL]
$tsn_stage(S_reject, 3)
$propref_at(S_reject.PROPREFS, n_leaf) = (ppropref)
S_reject.STORE[n_leaf] = DEFINED (POBJECT n_new)
$objectprops_record_at(S_reject.OBJECTPROPS, n_holder) = (pobjectprops_holder)
S_reject.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_reject.ARRAYS[n_copied].ITEMS = S_returned.ARRAYS[n_copied].ITEMS
$node_children(S_reject, HCELL n_leaf) = [HOBJECT n_new]
'''.strip().splitlines()

SOURCES = r'''
S_unroot = S_pre[.ENV = $unbind(S_pre.ENV, $ptascii("holder"))]
$propref_source_valid(S_unroot, n_leaf, OBJECT_PROP_SOURCE n_holder ($ptascii("p")) ppropertyid)
(HCELL n_leaf) <- $heap_prune($heap_graph(S_unroot)).NODES
~((HOBJECT n_holder) <- $heap_prune($heap_graph(S_unroot)).NODES)
~$named_reference_notice_array(S_unroot, PARRAY n_root)
S_empty = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_empty, PARRAY n_root)
S_twice = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ ppropref.SOURCES)}]]
~$named_reference_notice_array(S_twice, PARRAY n_root)
S_wrong_key = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_holder ($ptascii("missing")) ppropertyid])}]]
~$named_reference_notice_array(S_wrong_key, PARRAY n_root)
S_wrong_cell = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_holder, [{DECL (ppropertyid), NAME ($ptascii("p")), STATE (PROP_VALUE (ALIAS n_old_cell))}])]
~$named_reference_notice_array(S_wrong_cell, PARRAY n_root)
S_source_unit = S_pre[.NATIVEEXCESS = [HOBJECT n_holder]]
~$named_reference_notice_array(S_source_unit, PARRAY n_root)
S_called = S_pre[.DESTRUCTION.CALLED = [n_holder]]
~$named_reference_notice_array(S_called, PARRAY n_root)
pinstancestorage_source = {OBJECT n_holder, HANDLE 0, SLOTS pobjectprops_holder.SLOTS, NEXT 0, NOTIFY eps, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, USER false}
S_freeing = S_pre[.TODO = [INSTANCE_STORAGE_STEP pinstancestorage_source]]
$instance_storage_freeing(S_freeing, n_holder)
~$named_reference_notice_array(S_freeing, PARRAY n_root)
S_table = S_pre[.OBJECTTABLES = [{OBJECT n_holder, TABLE n_root}]]
~$named_reference_notice_array(S_table, PARRAY n_root)
S_parent = S_pre[.CLASSES = [pclassdesc[.PARENT = ($ptascii("Unknown"))]]]
~$named_reference_notice_array(S_parent, PARRAY n_root)
S_protected = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.VISIBILITY = PROPERTY_PROTECTED]]]]]
~$named_reference_notice_array(S_protected, PARRAY n_root)
S_nullable = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type])), (PTBRANCH ([PTBUILTIN "null"]))]]]]]]
$propref_source_valid(S_nullable, n_leaf, OBJECT_PROP_SOURCE n_holder ($ptascii("p")) ppropertyid)
~$named_reference_notice_array(S_nullable, PARRAY n_root)
S_extra_slot = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_holder, pobjectprops_holder.SLOTS ++ [{DECL eps, NAME ($ptascii("extra")), STATE (PROP_VALUE (DIRECT (PINT 0)))}])]
~$named_reference_notice_array(S_extra_slot, PARRAY n_root)
S_current_user = S_pre[.STORE[n_leaf] = DEFINED (POBJECT n_holder)]
~$named_reference_notice_array(S_current_user, PARRAY n_root)
S_current_owning = S_pre[.STORE[n_leaf] = DEFINED (POBJECT n_new)][.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_new, [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (POBJECT n_old)))}])]
$propref_source_valid(S_current_owning, n_leaf, OBJECT_PROP_SOURCE n_holder ($ptascii("p")) ppropertyid)
$named_reference_notice_object(S_current_owning, POBJECT n_old)
$node_children(S_current_owning, HCELL n_leaf) = [HOBJECT n_new]
~$named_reference_notice_object(S_current_owning, POBJECT n_new)
$objectprops_valid(S_current_owning, S_current_owning.OBJECTPROPS)
~$named_reference_notice_array(S_current_owning, PARRAY n_root)
S_root_unit = S_pre[.NATIVEEXCESS = [HARRAY n_root]]
~$named_reference_notice_array(S_root_unit, PARRAY n_root)
S_cell_unit = S_pre[.NATIVEEXCESS = [HCELL n_leaf]]
~$named_reference_notice_array(S_cell_unit, PARRAY n_root)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--capture-steps', type=int)
    selection.add_argument('--part', choices=('ownership', 'sources'))
    args = parser.parse_args()
    assert args.capture_steps is None or 0 < args.capture_steps <= 64
    native_path = args.native_provenance.resolve()
    native = json.loads(native_path.read_bytes())
    source = Path(native['command'][-1])
    assert native['passed'] and native['mode'] == 'native-only'
    assert source.read_bytes() == CASES[native['id']]
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='typed-alias-stdclass-reference-review-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), native_path, source,
        ROOT / 'tests/semantics/typed_alias_stdclass_reference_notice_review_cases.py',
        ROOT / 'tests/semantics/typed_alias_stdclass_reference_notice_review_cases.json',
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
        assert prepared.get('capture_steps') == args.capture_steps
        assert prepared.get('part') == args.part
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
        reached = PRE + OWNERSHIP if args.part == 'ownership' else PRE
        derived = SOURCES if args.part == 'sources' else []
        checks = [initial] + reached + derived
        signature = 'dec $main() : bool\ndef $main() = true\n'
        if args.capture_steps is not None:
            checks = [initial, f'S_snapshot = $drive_steps(S_initial[.COMPLETION = NORMAL], {args.capture_steps})']
            signature = 'dec $main() : pstate\ndef $main() = S_snapshot\n'
        fixture = directory / 'state.watsup'
        fixture.write_text(PREFIX + '\n' + signature +
            ''.join('  -- if ' + check + '\n' for check in checks))
        prepared = {'revision': revision, 'inputs': before, 'source': str(source),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'part': args.part, 'conditions': len(checks), 'reached_conditions': len(reached) + 1,
            'derived_conditions': len(derived), 'heap_bindings': sum(check.startswith('H_') for check in reached),
            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
        if args.capture_steps is not None:
            prepared.update(capture_steps=args.capture_steps, conditions=0,
                reached_conditions=0, derived_conditions=0, heap_bindings=0,
                scope='Finite typed pstate capture only; no ownership assertions or source agreements.')
        (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture = directory / 'state.watsup'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run',
        180 if args.capture_steps is not None else 480)
    stable = before == fingerprints() and hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    stdout = (directory / 'run.stdout').read_bytes()
    result_valid = stdout.startswith(b'{\n') if args.capture_steps is not None else stdout == b'true\n'
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and result_valid
        and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable,
        module_count=len(modules), mode='AL/cache=false/det=true',
        process=process, passed=passed, source_agreements=0)
    if args.capture_steps is not None:
        report['snapshot_sha256'] = hashlib.sha256(stdout).hexdigest()
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('finite AL capture' if args.capture_steps is not None else args.part,
        passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

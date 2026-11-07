#!/usr/bin/env python3
"""Check failed static binding, the retained static root, and exact source refusals."""
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
from typed_static_alias_stdclass_reference_notice_review_cases import CASES

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
  -- if $tsn_output(S.EVENTS) = $ptascii("A;B;H;")
def $tsn_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $tsn_output(S.EVENTS) = $ptascii("A;B;H;F;")
def $tsn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $tsn_output(S.EVENTS) = $ptascii("A;B;H;F;1:1:1:17;")
def $tsn_stage(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.OBJECTS[n] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
  -- if $tsn_output(S.EVENTS) = $ptascii("A;")
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
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cell)
$lookup(S_pre.ENV, $ptascii("replacement")) = (n_new_cell)
$lookup(S_pre.ENV, $ptascii("bad")) = (n_bad_cell)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
S_pre.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cell] = DEFINED (POBJECT n_new)
S_pre.STORE[n_bad_cell] = DEFINED (PINT 17)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
n_old =/= n_new /\ n_leaf =/= n_bad_cell
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.STORE[n_source] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertyid]
$propref_source_valid(S_pre, n_leaf, CLASS_PROP_SOURCE ppropertyid)
$propref_descriptor(S_pre, CLASS_PROP_SOURCE ppropertyid) = (ppropertydesc)
ppropertydesc.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
$ptlc(ptbytes_type) = $ptascii("stdclass")
ppropertydesc.STATIC /\ ppropertydesc.DEFAULT = PROP_UNINITIALIZED
S_pre.CLASSES = [pclassdesc]
pclassdesc.PROPERTIES = [ppropertydesc]
$property_declaring_class(S_pre.CLASSES, ppropertyid) = (pclassdesc.ORIGIN)
$class_named(S_pre.CLASSNAMES, $ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)
$class_static_active_desc(S_pre, S_pre.CLASSNAMES, ppropertyid) = (ppropertydesc)
S_pre.CLASSSTATICS = [{DECL ppropertyid, STATE (PROP_VALUE (ALIAS n_leaf))}]
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
$named_reference_notice_object(S_pre, POBJECT n_old)
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
~$named_reference_notice_operand(S_pre, REFERENCE n_leaf)
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_leaf) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2
$heap_owners(H_pre, HOBJECT n_new) = 1
(HCELL n_leaf) <- $heap_prune(H_pre).NODES
$proprefs_valid(S_pre) /\ $class_statics_valid(S_pre) /\ $call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

INGRESS = r'''
~$named_reference_notice_array(S_pre, PARRAY n_root)
~$named_reference_notice_pending(S_pre)
S_untyped = S_pre[.PROPREFS = eps]
$named_reference_notice_array(S_untyped, PARRAY n_root)
'''.strip().splitlines()

ADMITTED = r'''
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
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
S_failed = $tsn_seek(S_notice, 4, 768)
$tsn_stage(S_failed, 4)
S_failed.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_failed.PROPREFS, n_leaf) = (ppropref)
$propref_at(S_failed.PROPREFS, n_bad_cell) = eps
S_failed.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_failed.STORE[n_bad_cell] = DEFINED (PINT 17)
$class_static_roots(S_failed.CLASSSTATICS) = [HCELL n_leaf]
H_failed = $heap_graph(S_failed)
$heap_owners(H_failed, HCELL n_leaf) = 3
$proprefs_valid(S_failed) /\ $class_statics_valid(S_failed) /\ $heap_valid(H_failed)
S_resume = $tsn_seek(S_failed, 1, 768)[.COMPLETION = NORMAL]
$tsn_stage(S_resume, 1)
$lookup(S_resume.ENV, $ptascii("leaf")) = eps
S_resume.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_resume.PROPREFS, n_leaf) = (ppropref)
$propref_at(S_resume.PROPREFS, n_bad_cell) = eps
S_resume.STORE[n_leaf] = DEFINED (POBJECT n_old)
$class_static_roots(S_resume.CLASSSTATICS) = [HCELL n_leaf]
$duplicate_item(S_resume, n_root, ALIAS n_leaf) = ALIAS n_leaf
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HARRAY n_root) = 3
$heap_owners(H_resume, HCELL n_private) = 1
$heap_owners(H_resume, HCELL n_leaf) = 2
$heap_owners(H_resume, HOBJECT n_old) = 2
$heap_owners(H_resume, HOBJECT n_new) = 1
$proprefs_valid(S_resume) /\ $class_statics_valid(S_resume) /\ $call_descriptors_valid(S_resume) /\ $heap_valid(H_resume)
S_returned = $tsn_seek(S_resume, 2, 768)[.COMPLETION = NORMAL]
$tsn_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_returned.PROPREFS, n_leaf) = (ppropref)
$propref_at(S_returned.PROPREFS, n_bad_cell) = eps
S_returned.STORE[n_leaf] = DEFINED (POBJECT n_old)
$class_static_roots(S_returned.CLASSSTATICS) = [HCELL n_leaf]
$node_children(S_returned, HARRAY n_copied) = [HCELL n_leaf]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HARRAY n_root) = 2
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_leaf) = 3
$heap_owners(H_returned, HOBJECT n_old) = 2
$heap_owners(H_returned, HOBJECT n_new) = 1
$proprefs_valid(S_returned) /\ $class_statics_valid(S_returned) /\ $call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_zero = $drive(S_returned, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_returned
S_split = $drive($drive(S_returned, 1)[.COMPLETION = NORMAL], 1)
S_split = $drive(S_returned, 2)
S_reject = $tsn_seek(S_returned, 3, 768)[.COMPLETION = NORMAL]
$tsn_stage(S_reject, 3)
S_reject.CLASSSTATICS = S_pre.CLASSSTATICS
$propref_at(S_reject.PROPREFS, n_leaf) = (ppropref)
$propref_at(S_reject.PROPREFS, n_bad_cell) = eps
S_reject.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_reject.STORE[n_bad_cell] = DEFINED (PINT 23)
S_reject.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_reject.ARRAYS[n_copied].ITEMS = S_returned.ARRAYS[n_copied].ITEMS
'''.strip().splitlines()


SOURCES = r'''
S_no_active = S_pre[.CLASSNAMES = eps]
~$propref_source_valid(S_no_active, n_leaf, CLASS_PROP_SOURCE ppropertyid)
~$named_reference_notice_array(S_no_active, PARRAY n_root)
S_row_wrong_cell = S_pre[.CLASSSTATICS = [{DECL ppropertyid, STATE (PROP_VALUE (ALIAS n_bad_cell))}]]
~$named_reference_notice_array(S_row_wrong_cell, PARRAY n_root)
S_row_direct = S_pre[.CLASSSTATICS = [{DECL ppropertyid, STATE (PROP_VALUE (DIRECT (POBJECT n_old)))}]]
~$named_reference_notice_array(S_row_direct, PARRAY n_root)
S_row_initial = S_pre[.CLASSSTATICS = [{DECL ppropertyid, STATE PROP_INITIAL}]]
~$named_reference_notice_array(S_row_initial, PARRAY n_root)
S_empty = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_empty, PARRAY n_root)
S_twice = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES (ppropref.SOURCES ++ ppropref.SOURCES)}]]
~$named_reference_notice_array(S_twice, PARRAY n_root)
S_wrong_id = S_pre[.PROPREFS = [{CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE (INTERNAL_PROPERTY "stdClass" ($ptascii("p")))])}]]
~$named_reference_notice_array(S_wrong_id, PARRAY n_root)
S_parent = S_pre[.CLASSES = [pclassdesc[.PARENT = ($ptascii("Unknown"))]]]
~$named_reference_notice_array(S_parent, PARRAY n_root)
S_protected = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.VISIBILITY = PROPERTY_PROTECTED]]]]]
~$named_reference_notice_array(S_protected, PARRAY n_root)
S_nullable = S_pre[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type])), (PTBRANCH ([PTBUILTIN "null"]))]]]]]]
$propref_source_valid(S_nullable, n_leaf, CLASS_PROP_SOURCE ppropertyid)
~$named_reference_notice_array(S_nullable, PARRAY n_root)
S_current_owning = S_pre[.STORE[n_leaf] = DEFINED (POBJECT n_new)][.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_new, [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (POBJECT n_old)))}])]
$propref_source_valid(S_current_owning, n_leaf, CLASS_PROP_SOURCE ppropertyid)
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
    parser.add_argument('--part', choices=('ingress', 'ownership', 'sources'), required=True)
    args = parser.parse_args()
    native_path = args.native_provenance.resolve()
    native = json.loads(native_path.read_bytes())
    source = Path(native['command'][-1])
    assert native['passed'] and native['mode'] == 'native-only'
    assert source.read_bytes() == CASES[native['id']]
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='typed-static-alias-stdclass-reference-review-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), native_path, source,
        ROOT / 'tests/semantics/typed_static_alias_stdclass_reference_notice_review_cases.py',
        ROOT / 'tests/semantics/typed_static_alias_stdclass_reference_notice_review_cases.json',
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
        reached = PRE + (INGRESS if args.part == 'ingress' else ADMITTED)
        if args.part == 'ownership':
            reached += OWNERSHIP
        derived = SOURCES if args.part == 'sources' else []
        checks = [initial] + reached + derived
        signature = 'dec $main() : bool\ndef $main() = true\n'
        fixture = directory / 'state.watsup'
        fixture.write_text(PREFIX + '\n' + signature +
            ''.join('  -- if ' + check + '\n' for check in checks))
        prepared = {'revision': revision, 'inputs': before, 'source': str(source),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'part': args.part, 'conditions': len(checks), 'reached_conditions': len(reached) + 1,
            'derived_conditions': len(derived), 'heap_bindings': len({check.split(' = ', 1)[0] for check in reached if check.startswith('H_')}),
            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
        (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture = directory / 'state.watsup'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 480)
    stable = before == fingerprints() and hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    stdout = (directory / 'run.stdout').read_bytes()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and stdout == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable,
        module_count=len(modules), mode='AL/cache=false/det=true',
        process=process, passed=passed, source_agreements=0)
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.part, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

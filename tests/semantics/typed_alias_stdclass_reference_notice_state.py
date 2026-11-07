#!/usr/bin/env python3
"""Check actual typed-property sources, constrained COW and explicit detach."""
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

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $tan_output(pevent*) : ptbytes
def $tan_output(eps) = eps
def $tan_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $tan_output(pevent*)
dec $tan_stage(pstate, nat) : bool
def $tan_stage(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if S.RESULT = KNOWN (PARRAY n_root)
def $tan_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $tan_output(S.EVENTS) = $ptascii("A;H;")
def $tan_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $tan_output(S.EVENTS) = $ptascii("A;H;T;F;")
def $tan_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $tan_output(S.EVENTS) = $ptascii("P;")
def $tan_stage(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $tan_output(S.EVENTS) = $ptascii("P;V;")
def $tan_stage(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("take")
  -- if $tan_output(S.EVENTS) = $ptascii("P;V;U;")
def $tan_stage(S, 6) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $tan_output(S.EVENTS) = $ptascii("P;V;U;")
def $tan_stage(S, n) = false -- otherwise
dec $tan_seek(pstate, nat, nat) : pstate
def $tan_seek(S, n_stage, n) = S
  -- if $tan_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $tan_seek(S, n_stage, n) = $tan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$tan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tan_seek(S, n_stage, n) = $tan_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$tan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $tan_seek(S, n_stage, n) = S -- otherwise
'''

SHARED = r'''
S_pre = $tan_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$tan_stage(S_pre, 0)
S_pre.RESULT = KNOWN (PARRAY n_root)
$tan_output(S_pre.EVENTS) = $ptascii("A;")
$lookup(S_pre.ENV, $ptascii("shared")) = (n_shared)
$lookup(S_pre.ENV, $ptascii("holder")) = (n_holder_cell)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cell)
S_pre.STORE[n_holder_cell] = DEFINED (POBJECT n_holder)
S_pre.STORE[n_shared] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cell] = DEFINED (POBJECT n_old)
$propref_at(S_pre.PROPREFS, n_shared) = ({CELL n_shared, SOURCES ([OBJECT_PROP_SOURCE n_holder ptbytes porigin_decl])})
$propref_source_valid(S_pre, n_shared, OBJECT_PROP_SOURCE n_holder ptbytes porigin_decl)
$propref_descriptor(S_pre, OBJECT_PROP_SOURCE n_holder ptbytes porigin_decl) = (ppropertydesc)
ppropertydesc.TYPE = [(PTBRANCH ([PTCLASS ptbytes_type]))]
$ptlc(ptbytes_type) = $ptascii("stdclass")
$objectprops_record_at(S_pre.OBJECTPROPS, n_holder) = ({OBJECT n_holder, SLOTS ([{DECL (porigin_decl), NAME ptbytes, STATE PROP_VALUE (ALIAS n_shared)}]), MATERIALIZED false})
$node_children(S_pre, HOBJECT n_holder) = [HCELL n_shared]
$node_children(S_pre, HCELL n_shared) = [HOBJECT n_old]
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_shared), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_shared)]
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_shared) = 4
$heap_owners(H_pre, HOBJECT n_holder) = 1
$heap_owners(H_pre, HOBJECT n_old) = 2
(HOBJECT n_holder) <- $heap_prune(H_pre).NODES
$named_reference_notice_object(S_pre, POBJECT n_old)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_array(S_pre[.PROPREFS = eps], PARRAY n_root)
$positional_reference_notice_pending(S_pre)
$positional_reference_notice_pending(S_pre[.PROPREFS = eps])
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
'''.strip().splitlines()

SHARED += r'''
$named_reference_notice_object_property_source(S_pre, n_shared)
$lookup(S_pre.ENV, $ptascii("replacement")) = (n_replacement)
S_pre.STORE[n_replacement] = DEFINED (POBJECT n_new)
n_old =/= n_new
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HCELL n_shared) = 4
$heap_owners(H_notice, HOBJECT n_holder) = 1
$heap_owners(H_notice, HOBJECT n_old) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice) /\ $heap_valid(H_notice)
S_handler = $tan_seek(S_notice, 1, 512)[.COMPLETION = NORMAL]
$tan_stage(S_handler, 1)
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("source")) = eps
$lookup(psymboltable.ENV, $ptascii("shared")) = (n_shared)
S_handler.STORE[n_shared] = DEFINED (POBJECT n_new)
$node_children(S_handler, HCELL n_shared) = [HOBJECT n_new]
$propref_at(S_handler.PROPREFS, n_shared) = $propref_at(S_pre.PROPREFS, n_shared)
$named_reference_notice_object_property_source(S_handler, n_shared)
$named_reference_notice_array(S_handler, PARRAY n_root)
H_handler = $heap_graph(S_handler)
$heap_owners(H_handler, HARRAY n_root) = 2
$heap_owners(H_handler, HCELL n_shared) = 5
$heap_owners(H_handler, HOBJECT n_holder) = 1
$heap_owners(H_handler, HOBJECT n_old) = 1
$heap_owners(H_handler, HOBJECT n_new) = 2
$call_descriptors_valid(S_handler) /\ $heap_valid(H_handler)
S_returned = $tan_seek(S_handler, 2, 512)[.COMPLETION = NORMAL]
$tan_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.STORE[n_shared] = DEFINED (POBJECT n_new)
$node_children(S_returned, HCELL n_shared) = [HOBJECT n_new]
$propref_at(S_returned.PROPREFS, n_shared) = $propref_at(S_pre.PROPREFS, n_shared)
$named_reference_notice_object_property_source(S_returned, n_shared)
$propref_sources_valid(S_returned, n_shared, [OBJECT_PROP_SOURCE n_holder ptbytes porigin_decl])
$node_children(S_returned, HARRAY n_copied) = [HCELL n_shared, HCELL n_shared]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_shared) = 6
$heap_owners(H_returned, HOBJECT n_holder) = 1
$heap_owners(H_returned, HOBJECT n_old) = 1
$heap_owners(H_returned, HOBJECT n_new) = 2
$heap_owners(H_returned, HCELL n_private) = 1
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
'''.strip().splitlines()

UNWRAP = r'''
S_pre = $tan_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$tan_stage(S_pre, 0)
$positional_reference_notice_pending(S_pre)
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("shared")) = (n_shared)
$lookup(S_pre.ENV, $ptascii("holder")) = (n_holder_cell)
$lookup(S_pre.ENV, $ptascii("held")) = (n_held)
$lookup(S_pre.ENV, $ptascii("single")) = eps
S_pre.STORE[n_holder_cell] = DEFINED (POBJECT n_holder)
S_pre.STORE[n_held] = DEFINED (POBJECT n_object)
S_pre.STORE[n_shared] = DEFINED (POBJECT n_object)
$propref_at(S_pre.PROPREFS, n_shared) = ({CELL n_shared, SOURCES ([OBJECT_PROP_SOURCE n_holder ptbytes porigin_decl])})
$named_reference_notice_object_property_source(S_pre, n_shared)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_shared)]
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_shared) = 3
$heap_owners(H_pre, HOBJECT n_holder) = 1
$heap_owners(H_pre, HOBJECT n_object) = 2
$heap_owners(H_pre, HARRAY n_root) = 3
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
S_property = $tan_seek(S_pre, 3, 512)[.COMPLETION = NORMAL]
$tan_stage(S_property, 3)
$propref_at(S_property.PROPREFS, n_shared) = eps
~$named_reference_notice_object_property_source(S_property, n_shared)
$objectprops_record_at(S_property.OBJECTPROPS, n_holder) = ({OBJECT n_holder, SLOTS ([{DECL (porigin_decl), NAME ptbytes, STATE PROP_UNSET}]), MATERIALIZED false})
$node_children(S_property, HOBJECT n_holder) = eps
$node_children(S_property, HCELL n_shared) = [HOBJECT n_object]
H_property = $heap_graph(S_property)
$heap_owners(H_property, HCELL n_shared) = 2
$heap_owners(H_property, HOBJECT n_holder) = 1
$heap_owners(H_property, HARRAY n_root) = 3
$heap_owners(H_property, HOBJECT n_object) = 2
$call_descriptors_valid(S_property) /\ $heap_valid(H_property)
S_cv = $tan_seek(S_property, 4, 512)[.COMPLETION = NORMAL]
$tan_stage(S_cv, 4)
S_cv.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("shared")) = eps
$propref_at(S_cv.PROPREFS, n_shared) = eps
S_cv.STORE[n_shared] = DEFINED (POBJECT n_object)
$node_children(S_cv, HCELL n_shared) = [HOBJECT n_object]
H_cv = $heap_graph(S_cv)
$heap_owners(H_cv, HCELL n_shared) = 1
$heap_owners(H_cv, HOBJECT n_holder) = 1
$heap_owners(H_cv, HARRAY n_root) = 3
$call_descriptors_valid(S_cv) /\ $heap_valid(H_cv)
S_copied = $tan_seek(S_cv, 5, 512)[.COMPLETION = NORMAL]
$tan_stage(S_copied, 5)
$lookup(S_copied.ENV, $ptascii("v")) = (n_private)
S_copied.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_copied.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_copied.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_object)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
$propref_at(S_copied.PROPREFS, n_shared) = eps
$node_children(S_copied, HCELL n_shared) = [HOBJECT n_object]
$node_children(S_copied, HARRAY n_copied) = [HOBJECT n_object]
H_copied = $heap_graph(S_copied)
$heap_owners(H_copied, HARRAY n_root) = 1
$heap_owners(H_copied, HARRAY n_copied) = 1
$heap_owners(H_copied, HCELL n_shared) = 1
$heap_owners(H_copied, HOBJECT n_holder) = 1
$heap_owners(H_copied, HOBJECT n_object) = 3
$call_descriptors_valid(S_copied) /\ $heap_valid(H_copied)
S_returned = $tan_seek(S_copied, 6, 512)[.COMPLETION = NORMAL]
$tan_stage(S_returned, 6)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
S_returned.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (PINT 17)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.STORE[n_shared] = DEFINED (POBJECT n_object)
$propref_at(S_returned.PROPREFS, n_shared) = eps
$node_children(S_returned, HCELL n_shared) = [HOBJECT n_object]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_shared) = 1
$heap_owners(H_returned, HOBJECT n_holder) = 1
$heap_owners(H_returned, HOBJECT n_object) = 2
$heap_owners(H_returned, HCELL n_private) = 1
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
'''.strip().splitlines()

GROUPS = {
    'shared': ('positional-typed-shared-object-cell-retarget-cow', SHARED),
    'unwrap': ('positional-typed-object-cell-explicit-detach-unwrap', UNWRAP),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=GROUPS, required=True)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    case, reached = GROUPS[args.group]
    catalogue = Path(__file__).with_name('typed_alias_stdclass_reference_notice_cases.json')
    row, = [row for row in json.loads(catalogue.read_bytes()) if row['id'] == case]
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    native_row, = [item for item in native['records'] if item['id'] == case]
    source = Path(native_row['command'][-1])
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['passed'] and native['mode'] == 'native-first' and native_row['passed']
    assert native['profile'] == profile and source.read_bytes() == row['source'].encode()
    assert native['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    assert native_row['cwd'] == str(ROOT)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    directory = args.output or Path(tempfile.mkdtemp(prefix='typed-alias-stdclass-reference-state-' + args.group + '-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [ROOT / 'spec/semantics/modules.json', runner, Path(__file__), catalogue, native_path, source,
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php', 'frontend/target.php',
        'frontend/wire.php', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], directory / 'frontend')
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
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    checks = [initial] + reached
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    prepared = {'revision': revision, 'inputs': before, 'group': args.group, 'case': case, 'source': str(source),
        'conditions': len(checks), 'reached_conditions': len(checks), 'derived_conditions': 0,
        'heap_bindings': sum(check.startswith('H_') for check in reached),
        'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
    (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 360)
    stable = before == fingerprints() and prepared['fixture_sha256'] == hashlib.sha256(fixture.read_bytes()).hexdigest()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (directory / 'run.stdout').read_bytes() == b'true\n' and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable, module_count=len(modules),
        mode='AL/cache=false/det=true', process=process, source_agreements=0, passed=passed)
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.group, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

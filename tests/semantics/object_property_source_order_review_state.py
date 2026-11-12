#!/usr/bin/env python3
"""Check declaration-order deletion while retaining the actual surviving owners."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $osn_ready(pstate, nat) : bool
def $osn_ready(S, n_count) = true
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if S.HELD = eps /\ S.RETIREDOWNERS = eps
  -- if S.EVENTS = eps
  -- if $lookup(S.ENV, $ptascii("leaf")) = (n_leaf)
  -- if $propref_at(S.PROPREFS, n_leaf) = (ppropref)
  -- if |ppropref.SOURCES| = n_count
def $osn_ready(S, n_count) = false -- otherwise
dec $osn_seek(pstate, nat, nat) : pstate
def $osn_seek(S, n_count, n) = S
  -- if $osn_ready(S, n_count) \/ n = 0 \/ S.TODO = eps
def $osn_seek(S, n_count, n) = $osn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_count, $nabs($(n - 1)))
  -- if ~$osn_ready(S, n_count) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $osn_seek(S, n_count, n) = S -- otherwise
'''

REACHED = r'''
S_pre = $osn_seek(S_initial, 4, 1024)[.COMPLETION = NORMAL]
$osn_ready(S_pre, 4)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("replacement")) = (n_replacement)
$lookup(S_pre.ENV, $ptascii("first")) = (n_first_cv)
$lookup(S_pre.ENV, $ptascii("second")) = (n_second_cv)
$lookup(S_pre.ENV, $ptascii("middle")) = (n_middle_cv)
$lookup(S_pre.ENV, $ptascii("last")) = (n_last_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_replacement] = DEFINED (POBJECT n_new)
S_pre.STORE[n_first_cv] = DEFINED (POBJECT n_first)
S_pre.STORE[n_second_cv] = DEFINED (POBJECT n_second)
S_pre.STORE[n_middle_cv] = DEFINED (POBJECT n_middle)
S_pre.STORE[n_last_cv] = DEFINED (POBJECT n_last)
n_first =/= n_second /\ n_old =/= n_new
$propref_at(S_pre.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat, OBJECT_PROP_SOURCE n_last ($ptascii("p")) ppropertyid_last])})
ppropertyid_repeat =/= ppropertyid_middle /\ ppropertyid_repeat =/= ppropertyid_last
S_pre.OBJECTS[n_first] = INSTANCE porigin_repeat
S_pre.OBJECTS[n_second] = INSTANCE porigin_repeat
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle)
$propref_source_valid(S_pre, n_leaf, OBJECT_PROP_SOURCE n_last ($ptascii("p")) ppropertyid_last)
$node_children(S_pre, HOBJECT n_first) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_second) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_middle) = [HCELL n_leaf]
$node_children(S_pre, HOBJECT n_last) = [HCELL n_leaf]
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HCELL n_leaf) = 5
$heap_owners(H_pre, HCELL n_replacement) = 1
$heap_owners(H_pre, HOBJECT n_first) = 1 /\ $heap_owners(H_pre, HOBJECT n_second) = 1
$heap_owners(H_pre, HOBJECT n_middle) = 1 /\ $heap_owners(H_pre, HOBJECT n_last) = 1
$heap_owners(H_pre, HOBJECT n_old) = 1 /\ $heap_owners(H_pre, HOBJECT n_new) = 1
$proprefs_valid(S_pre) /\ $propref_slots_covered(S_pre, S_pre.OBJECTPROPS) /\ $objectprops_valid(S_pre, S_pre.OBJECTPROPS) /\ $heap_valid(H_pre)
S_post = $osn_seek(S_pre, 3, 1024)[.COMPLETION = NORMAL]
$osn_ready(S_post, 3)
$propref_at(S_post.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_last ($ptascii("p")) ppropertyid_last, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle, OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat])})
$propref_at(S_post.PROPREFS, n_replacement) = ({CELL n_replacement, SOURCES ([OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat])})
$propref_source_valid(S_post, n_leaf, OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat)
$propref_source_valid(S_post, n_leaf, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle)
$propref_source_valid(S_post, n_leaf, OBJECT_PROP_SOURCE n_last ($ptascii("p")) ppropertyid_last)
~$propref_source_present(S_post.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat)
~$propref_source_valid(S_post, n_leaf, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat)
$propref_source_valid(S_post, n_replacement, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat)
$node_children(S_post, HOBJECT n_first) = [HCELL n_leaf]
$node_children(S_post, HOBJECT n_middle) = [HCELL n_leaf]
$node_children(S_post, HOBJECT n_last) = [HCELL n_leaf]
$node_children(S_post, HOBJECT n_second) = [HCELL n_replacement]
S_post.STORE[n_leaf] = S_pre.STORE[n_leaf] /\ S_post.STORE[n_replacement] = S_pre.STORE[n_replacement]
H_post = $heap_graph(S_post)
H_post = $heap_graph(S_post[.PROPREFS = eps])
$heap_owners(H_post, HCELL n_leaf) = 4 /\ $heap_owners(H_post, HCELL n_replacement) = 2
$heap_owners(H_post, HOBJECT n_first) = 1 /\ $heap_owners(H_post, HOBJECT n_second) = 1
$heap_owners(H_post, HOBJECT n_middle) = 1 /\ $heap_owners(H_post, HOBJECT n_last) = 1
$heap_owners(H_post, HOBJECT n_old) = 1 /\ $heap_owners(H_post, HOBJECT n_new) = 1
$proprefs_valid(S_post) /\ $propref_slots_covered(S_post, S_post.OBJECTPROPS) /\ $objectprops_valid(S_post, S_post.OBJECTPROPS) /\ $heap_valid(H_post)
S_zero = $drive(S_post, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_post
$drive($drive(S_post, 1)[.COMPLETION = NORMAL], 1) = $drive(S_post, 2)
'''.strip().splitlines()

PROTOCOL = r'''
$propref_remove_sources([OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat], OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat) = [OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle]
$propref_remove_sources([OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat], OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat) = [OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle]
$propref_at($propref_attach($propref_detach(S_pre.PROPREFS, n_leaf, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat), n_leaf, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat), n_leaf) = ({CELL n_leaf, SOURCES ([OBJECT_PROP_SOURCE n_last ($ptascii("p")) ppropertyid_last, OBJECT_PROP_SOURCE n_middle ($ptascii("p")) ppropertyid_middle, OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat, OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_repeat])})
$propref_remove_sources([OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat], OBJECT_PROP_SOURCE n_second ($ptascii("p")) ppropertyid_middle) = [OBJECT_PROP_SOURCE n_first ($ptascii("p")) ppropertyid_repeat]
$propref_remove_sources([CLASS_PROP_SOURCE ppropertyid_repeat, CLASS_PROP_SOURCE ppropertyid_middle], CLASS_PROP_SOURCE ppropertyid_repeat) = [CLASS_PROP_SOURCE ppropertyid_middle]
ppropertyid_repeat = PORIGIN n_repeat_source pcpath_repeat
$propref_remove_sources([RETIRED_CLASS_PROP_SOURCE (PORIGIN n_repeat_source pcpath_repeat) 0, CLASS_PROP_SOURCE ppropertyid_middle, CLASS_PROP_SOURCE ppropertyid_repeat], CLASS_PROP_SOURCE ppropertyid_repeat) = [RETIRED_CLASS_PROP_SOURCE (PORIGIN n_repeat_source pcpath_repeat) 0, CLASS_PROP_SOURCE ppropertyid_middle]
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    catalogue = Path(__file__).with_name('object_property_source_order_review_cases.json')
    row, = json.loads(catalogue.read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed']
    assert native['id'] == row['id'] and source.read_bytes() == row['source'].encode()
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == digest(types.PHP)
    assert native['source_sha256'] == digest(source) == row['source_sha256']
    directory = args.output.resolve()
    directory.mkdir(parents=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), catalogue, provenance, source, types.PHP,
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): digest(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
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
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    checks = [initial] + REACHED + PROTOCOL
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    fixture_sha = digest(fixture)
    print(directory, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 540)
    stable = before == fingerprints() and digest(fixture) == fixture_sha
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'source': str(source), 'source_sha256': digest(source),
        'fixture_sha256': fixture_sha, 'conditions': len(checks), 'reached_conditions': len(REACHED) + 1,
        'derived_conditions': len(PROTOCOL), 'heap_bindings': 2, 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'inputs_stable': stable, 'head_stable': head_stable,
        'process': process, 'passed': passed, 'source_agreements': 0}
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('order and membership', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

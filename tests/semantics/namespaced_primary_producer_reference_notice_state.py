#!/usr/bin/env python3
"""Check actual early publication, Notice ownership and a late-primary refusal."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
from reference_send_notice_review_state import PREFIX
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('namespaced_primary_producer_reference_notice_cases.json')

COMMON = r'''
S_initial.COMPLETION = BUDGET
S_pre = $rsn_find(S_initial[.COMPLETION = NORMAL], 2000, 0)
$rsn_stage(S_pre, 0)
S_pre.COMPLETION = NORMAL /\ S_pre.CURRENT = eps
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes_fallback? =/= eps
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_pre, pfunction_producer)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
S_pre.STORE[n_leaf] = DEFINED (PINT 5)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$named_reference_notice_array(S_pre, PARRAY n_root)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
$call_task_valid(S_pre, CALL_SEND pcalltarget eps 0 eps (porigin_call) z)
$declaration_history_valid(S_pre)
H_pre = $heap_graph(S_pre)
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
'''.strip().splitlines()

PRIMARY = r'''
$rsn_outputs(S_pre.EVENTS) = $ptascii("A;")
pfunction_producer.NAME = $ptascii("PrimaryProducer31\\make")
pfunction_producer.EARLY /\ $declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_valid(H_notice) /\ $error_call_valid(S_notice, perrorcall)
S_full = $drive(S_notice, 10000)
S_full.COMPLETION = NORMAL
$rsn_outputs(S_full.EVENTS) = $ptascii("A;H;F;7:7:7:9;11:11;11:17:9:13;")
$rsn_diagnostics(S_full.EVENTS) = eps
S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
H_full = $heap_graph(S_full)
$heap_valid(H_full) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()

PRIMARY_CONTROLS = r'''
S_no_publication = S_pre[.DECLARATIONS = eps]
~$declaration_early(S_no_publication.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$reference_notice_producer_target(S_no_publication, porigin_argument) = eps
~$positional_reference_notice_pending(S_no_publication)
~$declaration_history_valid(S_no_publication)
$heap_graph(S_no_publication) = H_pre
S_wrong_publication = S_pre[.DECLARATIONS = [PDEFUNCTION n_unit (PORIGIN n_unit (pcpath_producer ++ [PCINDEX 999]))]]
$reference_notice_producer_target(S_wrong_publication, porigin_argument) = eps
~$declaration_history_valid(S_wrong_publication)
$heap_graph(S_wrong_publication) = H_pre
$reference_notice_producer_target(S_pre, PORIGIN 999 pcpath_argument) = eps
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $rsn_resume(S_zero, 1)
S_two = $rsn_resume(S_one, 1)
S_two = $drive(S_notice, 2)
'''.strip().splitlines()

LATE = r'''
$rsn_outputs(S_pre.EVENTS) = $ptascii("A;G;I;")
pfunction_producer.NAME = $ptascii("LateProducer31\\make")
~pfunction_producer.EARLY
~$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$(|S_pre.DECLARATIONS| > 0)
n_last = $nabs($(|S_pre.DECLARATIONS| - 1))
S_pre.DECLARATIONS[n_last] = PDRFUNCTION (PORIGIN n_unit pcpath_producer) pdeclcause
$reference_notice_producer_target(S_pre, porigin_argument) = eps
~$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
~$positional_reference_notice_pending(S_pre)
S_end = $drive(S_pre, 1)
S_end.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
$rsn_outputs(S_end.EVENTS) = $ptascii("A;G;I;")
'''.strip().splitlines()

LATE_CONTROLS = r'''
S_forged_publication = S_pre[.DECLARATIONS = S_pre.DECLARATIONS ++ [PDEFUNCTION n_unit pfunction_producer.ORIGIN]]
~$declaration_history_valid(S_forged_publication)
$heap_graph(S_forged_publication) = H_pre
S_rejected = $declaration_entry_check(S_forged_publication)
S_rejected.COMPLETION = UNSUPPORTED "invalid declaration publication history"
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--part', required=True, choices=('primary', 'late'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    case = json.loads(CATALOGUE.read_bytes())[0 if args.part == 'primary' else 1]
    record, = [row for row in native['records'] if row['id'] == case['id']]
    source = Path(record['command'][-1])
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert record['passed'] and record['exit'] == 0 and not record['timeout'] and not record['group_after']
    assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == record['source_sha256']
    assert Path(record['stdout']).read_bytes() == record['actual_stdout'].encode() == case['native_stdout'].encode()
    assert Path(record['stderr']).read_bytes() == record['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
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
    function = ('PrimaryProducer31' if args.part == 'primary' else 'LateProducer31') + '\\take'
    stage = ('\ndef $rsn_stage(S, 0) = true\n'
        '  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*\n'
        '  -- if S.RESULT = KNOWN (PARRAY n_root)\n'
        '  -- if $target_function(S, pcalltarget) = (pfunction)\n'
        '  -- if pfunction.NAME = $ptascii(' + json.dumps(function) + ')\n'
        'def $rsn_stage(S, n_stage) = false -- otherwise\n')
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached = [initial] + COMMON + (PRIMARY if args.part == 'primary' else LATE)
    derived = PRIMARY_CONTROLS if args.part == 'primary' else LATE_CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + stage + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, source, native_path, Path(record['stdout']), Path(record['stderr']), Path(__file__), CATALOGUE]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/reference_send_notice_review_state.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': args.part, 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'AL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.part, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

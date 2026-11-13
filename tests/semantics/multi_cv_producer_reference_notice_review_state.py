"""Check compiled last-CV lines, duplicate-CV COW, private cells and header refusals."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from multi_cv_producer_reference_notice_review_cases import CASES, HASHES, NAMED_ID
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = Path(__file__).with_name('multi_cv_producer_reference_notice_review_expected.json')
PREFIX = r"""
dec $mcvr_output(pevent*) : ptbytes
def $mcvr_output(eps) = eps
def $mcvr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mcvr_output(pevent*)
dec $mcvr_ready(pstate) : bool
def $mcvr_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* 0 poperand* porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PARRAY n_array)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.SIGNATURE.BYREF
def $mcvr_ready(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PARRAY n_array)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.SIGNATURE.BYREF
def $mcvr_ready(S) = false -- otherwise
dec $mcvr_seek(pstate, nat) : pstate
def $mcvr_seek(S, n) = S -- if $mcvr_ready(S) \/ n = 0 \/ S.TODO = eps
def $mcvr_seek(S, n) = $mcvr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$mcvr_ready(S) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcvr_seek(S, n) = S -- otherwise
"""

COMMON = r"""
S_initial.COMPLETION = BUDGET
S_pre = $mcvr_seek(S_initial, 1500)[.COMPLETION = NORMAL]
$mcvr_ready(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$mcvr_output(S_pre.EVENTS) = $ptascii("J;M:5:13;")
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_producer)
$call_argument_expression(S_pre, (porigin_call), 0) = expression_producer
expression_producer = NExprFuncCall phpType19 (SEQUENCE ([phpType7_first, phpType7_last])) metadata_call
phpType7_first = NArg ABSENT expression_first (BOOLEAN false) (BOOLEAN false) metadata_first_arg
phpType7_last = NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN false) metadata_last_arg
expression_first = NExprVariable (BYTES text_first) metadata_first
expression_last = NExprVariable (BYTES text_last) metadata_last
$reference_cv(expression_first) = ($ptascii("x"))
$reference_cv(expression_last) = ($ptascii("x"))
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_first = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1])
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_first) = (expression_first)
$origin_node(S_pre.SOURCES, porigin_last) = (expression_last)
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.TYPE = eps /\ psparam_last.TYPE = eps
psparam_first.REQUIRED /\ psparam_last.REQUIRED
pfunction_producer.SIGNATURE.RETURNS = eps /\ ~pfunction_producer.SIGNATURE.BYREF
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) ABSENT phpType23 metadata_function)
$lookup(S_pre.ENV, $ptascii("x")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
n_source =/= n_copy /\ n_source <- S_pre.REFCELLS
S_pre.STORE[n_source] = DEFINED (PARRAY n_current)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_saved)
S_pre.RESULT = KNOWN (PARRAY n_saved)
n_saved =/= n_current
S_pre.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
S_pre.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]
$call_descriptors_valid(S_pre) /\ $heap_valid($heap_graph(S_pre))
""".strip().splitlines()

FULL = r"""
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
$positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call
S_notice.STORE[n_private] = DEFINED (PARRAY n_saved)
n_private =/= n_source /\ n_private =/= n_copy
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_saved) = $heap_owners($heap_graph(S_pre), HARRAY n_saved)
$node_children(S_notice, HCELL n_private) = [HARRAY n_saved]
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_zero[.COMPLETION = NORMAL], 1)
S_two = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_two = S_direct
S_full = $drive(S_notice, 10000)
S_full.COMPLETION = NORMAL
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("r")) = eps
$lookup(S_full.ENV, $ptascii("x")) = eps
$lookup(S_full.ENV, $ptascii("copy")) = eps
$heap_owners($heap_graph(S_full), HCELL n_private) = 0
~((HCELL n_private) <- S_full.ALLOCATIONS)
$call_descriptors_valid(S_full) /\ $heap_valid($heap_graph(S_full))
""".strip().splitlines()

CONTROLS = r"""
phpType17_third = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES "dGhpcmQ=") metadata_first) ABSENT (SEQUENCE eps) metadata_first
psparam_third = psparam_first[.NAME = $ptascii("third")]
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last, phpType7_first]), SEQUENCE ([phpType17_first, phpType17_last, phpType17_third]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first, psparam_last, psparam_third]])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first]])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first, psparam_last[.BYREF = false]]])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.REQUIRED = false], psparam_last]])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.VARIADIC = true], psparam_last]])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]], psparam_last]])
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES "YXJyYXk=") metadata_call, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])
expression_computed = NExprVariable (NScalarString (BYTES text_first) metadata_first) metadata_first
~$reference_notice_producer_arguments(SEQUENCE ([NArg ABSENT expression_computed (BOOLEAN false) (BOOLEAN false) metadata_first_arg, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([NArg (NIdentifier (BYTES text_first) metadata_first) expression_first (BOOLEAN false) (BOOLEAN false) metadata_first_arg, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN true) metadata_last_arg]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, NArg ABSENT (NExprVariable (BYTES "dGhpcw==") metadata_last) (BOOLEAN false) (BOOLEAN false) metadata_last_arg]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, NArg ABSENT (NExprVariable (BYTES "R0xPQkFMUw==") metadata_last) (BOOLEAN false) (BOOLEAN false) metadata_last_arg]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, NArg ABSENT (NExprVariable (BYTES "aHR0cF9yZXNwb25zZV9oZWFkZXI=") metadata_last) (BOOLEAN false) (BOOLEAN false) metadata_last_arg]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first]), SEQUENCE ([phpType17_first]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first]])
$reference_notice_producer_arguments(SEQUENCE eps, SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = [path.resolve() for path in args.native_report]
    natives = [json.loads(path.read_bytes()) for path in provenance]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    rows = {}
    for native in natives:
        assert native['passed'] and native['inputs_stable'] and native['head_stable']
        assert native['mode'] == 'native-only' and native['profile'] == types.PROFILE
        assert native['runtime']['binary_sha256'] == sha(types.PHP)
        for row in native['records']:
            assert row['id'] not in rows
            rows[row['id']] = row
    expected = {row['id']: row for row in json.loads(EXPECTED.read_bytes())}
    selected = args.case or list(CASES)
    assert expected.keys() == CASES.keys() and set(rows) <= CASES.keys()
    assert set(selected) <= rows.keys()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs = []
    reached_count = derived_count = 0
    paths = [Path(__file__), EXPECTED, *provenance,
             ROOT / 'tests/semantics/multi_cv_producer_reference_notice_review_cases.py']
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, name in enumerate(selected):
            source_bytes = CASES[name]
            row = rows[name]
            source = Path(row['source'])
            assert row['passed'] and source.read_bytes() == source_bytes and sha(source) == HASHES[name]
            assert row['source_sha256'] == expected[name]['source_sha256']
            assert row['stdout'] == expected[name]['native_stdout']
            assert row['observed_line'] == expected[name]['notice_line']
            assert source.with_name('native.stdout').read_bytes() == row['stdout'].encode()
            assert source.with_name('native.stderr').read_bytes() == row['stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source_bytes).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            fixture = checked['fixture']
            lines = source_bytes.decode().splitlines()
            first = next(i + 1 for i, line in enumerate(lines) if line == '    $x,')
            last = next(i + 1 for i, line in enumerate(lines) if line == '    $x')
            conditions = ['S_initial = $php_run(' + fixture + ', 0, ' +
                json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + COMMON
            if name == NAMED_ID:
                replacements = {
                    'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*':
                        'S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*',
                    '$call_argument_origin(S_pre, (porigin_call), 0)': '$named_origin(S_pre, (porigin_call), 1)',
                    '$call_argument_expression(S_pre, (porigin_call), 0)': '$named_expression($named_source(S_pre, (porigin_call), 1))',
                    '"J;M:5:13;"': '"N;M:5:13;"',
                }
                for old, new in replacements.items():
                    conditions = [line.replace(old, new) for line in conditions]
                conditions += [
                    '$lookup(S_pre.ENV, $ptascii("prefix")) = (n_prefix)',
                    '$lookup(S_pre.ENV, $ptascii("prefixAlias")) = (n_prefix)',
                    'S_pre.STORE[n_prefix] = DEFINED (PINT 2)',
                    'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)]',
                    'pnamedargs.NAMED = eps',
                    '$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3',
                ]
            conditions += ['$source_line(metadata_first) = ' + str(first),
                '$source_line(metadata_last) = ' + str(last),
                '$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = ' + str(row['observed_line'])]
            if args.front:
                conditions += ['~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)']
                if name == NAMED_ID:
                    conditions += ['~$named_reference_notice_pending(S_pre)']
            else:
                full = list(FULL)
                if name == NAMED_ID:
                    full = [line.replace('$positional_reference_notice_pending(S_pre)', '$named_reference_notice_pending(S_pre)')
                        .replace('perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call',
                            'perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call') for line in full]
                    full += ['pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)]',
                        'pnamedargs_after.NAMED = eps',
                        '$lookup(S_full.ENV, $ptascii("prefix")) = eps',
                        '$lookup(S_full.ENV, $ptascii("prefixAlias")) = eps']
                conditions += full + ['$reference_notice_producer_line(S_pre, (porigin_producer), expression_producer) = ' + str(row['observed_line']),
                    'perrorcall.LINE = ' + str(row['observed_line']),
                    '$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(row['stdout']) + ')']
            derived = CONTROLS if not args.front and name == next(iter(CASES)) else []
            reached_count += len(conditions)
            derived_count += len(derived)
            # Function scope keeps each source's bound variables independent.
            name = '$mcvr_case' + str(index)
            case_specs.append('dec ' + name + '() : bool\ndef ' + name + '() = true\n' +
                ''.join('  -- if ' + line + '\n' for line in conditions + derived))
            paths += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) +
        '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if $mcvr_case' + str(i) + '()\n' for i in range(len(selected))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in (
        'spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe',
        '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php',
        'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    recorder.ROOT = ROOT
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n'
        and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'input_count': len(before),
        'inputs_stable': stable, 'head_stable': head_stable, 'module_count': len(modules),
        'mode': 'fixture-SL/cache=false/det=true', 'front': args.front, 'process': process, 'selection': selected,
        'conditions': reached_count + derived_count, 'reached_conditions': reached_count,
        'derived_conditions': derived_count, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('multi-cv-review-state', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

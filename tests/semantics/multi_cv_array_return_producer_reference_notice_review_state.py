"""Check actual array return verification, named COW, private-cell freedom and retirement."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
import multi_cv_producer_reference_notice_review_state as prior
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_array_return_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX + r"""
dec $mcar_ready(pstate, nat) : bool
def $mcar_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice50\\Named\\make")
def $mcar_ready(S, 1) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("N;M:5:13;H:8:13:2;F:29:5;R:23:17:5:31;")
def $mcar_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("N;M:5:13;H:8:13:2;F:29:5;R:23:17:5:31;D:41:17:5:31;")
def $mcar_ready(S, n_stage) = false -- otherwise
dec $mcar_seek(pstate, nat, nat) : pstate
def $mcar_seek(S, n_stage, n) = S -- if $mcar_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcar_seek(S, n_stage, n) = $mcar_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcar_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcar_seek(S, n_stage, n) = S -- otherwise
"""
RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $mcar_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$mcar_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)
$lookup(S_return.ENV, $ptascii("changed")) = (n_source_return)
n_formal =/= n_source_return /\ ~(n_formal <- S_return.REFCELLS)
n_source_return <- S_return.REFCELLS
S_return.STORE[n_formal] = DEFINED (PARRAY n_old)
S_return.STORE[n_source_return] = DEFINED (PARRAY n_current_return)
n_old =/= n_current_return
S_return.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
S_return.ARRAYS[n_current_return].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]
S_return.RESULT = VARIABLE ($ptascii("saved")) z_saved
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy_return)
S_return.STORE[n_copy_return] = DEFINED (PARRAY n_old)
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PARRAY n_old, pfunction_producer.CODE.STRICT) = TYPEVALUE (PARRAY n_old)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_old)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS /\ S_checked.ALLOCATIONS = S_return.ALLOCATIONS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_old)) porigin_return?) :: ptask_return_tail*
S_after_return.CURRENT = S_return.CURRENT /\ S_after_return.ENV = S_return.ENV
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_old)) porigin_return?) = [HARRAY n_old]
$heap_valid($heap_graph(S_after_return)) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()
WRITTEN = r"""
S_written = $mcar_seek(S_notice, 1, 10000)[.COMPLETION = NORMAL]
$mcar_ready(S_written, 1)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_private_array)
n_private_array =/= n_saved /\ n_private_array =/= n_current
S_written.ARRAYS[n_private_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23))]
S_written.STORE[n_source] = DEFINED (PARRAY n_current)
S_written.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]
S_written.STORE[n_copy] = DEFINED (PARRAY n_saved)
S_written.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
S_written.STORE[n_prefix] = DEFINED (PINT 31)
$heap_owners($heap_graph(S_written), HARRAY n_private_array) = 1
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps
$reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_scalar = $mcar_seek(S_written, 2, 5000)[.COMPLETION = NORMAL]
$mcar_ready(S_scalar, 2)
$lookup(S_scalar.ENV, $ptascii("r")) = (n_private)
S_scalar.STORE[n_private] = DEFINED (PINT 41)
~((HARRAY n_private_array) <- S_scalar.ALLOCATIONS)
$heap_owners($heap_graph(S_scalar), HARRAY n_private_array) = 0
S_scalar.STORE[n_source] = DEFINED (PARRAY n_current)
S_scalar.STORE[n_copy] = DEFINED (PARRAY n_saved)
S_scalar.STORE[n_prefix] = DEFINED (PINT 31)
$heap_valid($heap_graph(S_scalar)) /\ $call_descriptors_valid(S_scalar)
""".strip().splitlines()
CONTROLS = r"""
~$error_call_valid(S_notice, perrorcall[.LINE = 9])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES "aW50") metadata_type, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]])
$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_type, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]], psparam_last]])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native = json.loads(provenance.read_bytes())
    case, = json.loads(CATALOGUE.read_bytes())
    row, = native['records']
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    source = Path(row['command'][-1])
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert row['id'] == case['id'] and row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
    assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
    assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
    assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        fixture_program = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    common = prior.COMMON[1:]
    replacements = {
        '$mcvr_seek(S_initial, 1500)': '$mcvr_seek(S_after_return, 1500)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*':
            'S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*',
        '$call_argument_origin(S_pre, (porigin_call), 0)': '$named_origin(S_pre, (porigin_call), 1)',
        '$call_argument_expression(S_pre, (porigin_call), 0)': '$named_expression($named_source(S_pre, (porigin_call), 1))',
        '"J;M:5:13;"': '"N;M:5:13;"',
        'pfunction_producer.SIGNATURE.RETURNS = eps': 'pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]',
        '])) ABSENT phpType23 metadata_function)': '])) (NIdentifier (BYTES text_type) metadata_type) phpType23 metadata_function)',
    }
    for old, new in replacements.items():
        common = [line.replace(old, new) for line in common]
    conditions = ['S_initial = $php_run(' + fixture_program + ', 0, ' +
        json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + RETURN + common
    conditions += [
        '$ptlc($base64(text_type)) = $ptascii("array")',
        'n_saved = n_old /\\ n_source = n_source_return',
        '~((HCELL n_formal) <- S_pre.ALLOCATIONS)',
        '$lookup(S_pre.ENV, $ptascii("saved")) = eps /\\ $lookup(S_pre.ENV, $ptascii("changed")) = eps',
        '$lookup(S_pre.ENV, $ptascii("prefix")) = (n_prefix)',
        '$lookup(S_pre.ENV, $ptascii("prefixAlias")) = (n_prefix)',
        'S_pre.STORE[n_prefix] = DEFINED (PINT 2)',
        'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\\ pnamedargs.NAMED = eps',
        '$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3',
        '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])',
        '$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = ' + str(case['notice_line']),
    ]
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE)'
    conditions += [('~' if args.front else '') + header,
        ('~' if args.front else '') + '$named_reference_notice_pending(S_pre)']
    derived = []
    if not args.front:
        full = prior.FULL[1:]
        full = [line.replace('$positional_reference_notice_pending(S_pre)', '$named_reference_notice_pending(S_pre)')
            .replace('perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call',
                'perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call') for line in full]
        at = full.index('S_full = $drive(S_notice, 10000)')
        full[at:at + 1] = WRITTEN + ['S_full = $drive(S_scalar, 10000)']
        conditions += full + [
            'pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\\ pnamedargs_after.NAMED = eps',
            'perrorcall.LINE = ' + str(case['notice_line']),
            '$lookup(S_full.ENV, $ptascii("prefix")) = eps /\\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps',
            '$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + line + '\n' for line in conditions + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, Path(__file__), Path(prior.__file__), CATALOGUE, provenance,
        source, Path(row['stdout']), Path(row['stderr'])]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
        '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php',
        'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable,
        head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true',
        front=args.front, conditions=len(conditions) + len(derived), reached_conditions=len(conditions),
        derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('multi-cv-array-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

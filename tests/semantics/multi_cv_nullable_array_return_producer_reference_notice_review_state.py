"""Check nullable ARRAY returns, named duplicate-CV COW and return-TypeError priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
import multi_cv_array_return_producer_reference_notice_review_state as array_review
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_nullable_array_return_producer_reference_notice_review_cases.json')
NULLABLE = '[(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]'
RAW_RETURN = 'NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable'
PREFIX = array_review.PREFIX.replace('ReviewNotice50', 'ReviewNotice52') + r"""
dec $mcnar_ready(pstate, nat) : bool
def $mcnar_ready(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget phpType7* 2 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice52\\Priority\\make")
def $mcnar_ready(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice52\\Priority\\make")
def $mcnar_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("P;M:17:23:0;C:11:2:1;")
def $mcnar_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("P;M:17:23:0;C:11:2:1;D:31:11:17:1;")
def $mcnar_ready(S, n_stage) = false -- otherwise
dec $mcnar_seek(pstate, nat, nat) : pstate
def $mcnar_seek(S, n_stage, n) = S -- if $mcnar_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcnar_seek(S, n_stage, n) = $mcnar_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcnar_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcnar_seek(S, n_stage, n) = S -- otherwise
"""
PRIORITY = r"""
S_initial.COMPLETION = BUDGET
S_args = $mcnar_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$mcnar_ready(S_args, 0)
S_args.TODO = (CALL_ARGS pcalltarget_producer eps 2 ([KNOWN (PINT 17), REFERENCE n_original_x]) (porigin_call) z_call) :: ptask_args*
$target_function(S_args, pcalltarget_producer) = (pfunction_producer)
$lookup(S_args.ENV, $ptascii("x")) = (n_original_x)
$lookup(S_args.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(S_args.ENV, $ptascii("prefixAlias")) = (n_prefix)
$lookup(S_args.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(S_args.ENV, $ptascii("r")) = (n_r)
S_args.STORE[n_original_x] = DEFINED (PINT 17)
S_args.STORE[n_prefix] = DEFINED (PINT 2)
S_args.STORE[n_snapshot] = DEFINED (PINT 17)
S_args.STORE[n_r] = DEFINED (PINT 11)
n_original_x <- S_args.REFCELLS
$heap_owners($heap_graph(S_args), HCELL n_original_x) = 2
$heap_owners($heap_graph(S_args), HCELL n_prefix) = 3
$heap_valid($heap_graph(S_args)) /\ $call_descriptors_valid(S_args)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.TYPE = eps /\ psparam_last.TYPE = eps
psparam_first.REQUIRED /\ psparam_last.REQUIRED /\ ~psparam_first.VARIADIC /\ ~psparam_last.VARIADIC
~pfunction_producer.SIGNATURE.BYREF
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]
$origin_node(S_args.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) (NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable) phpType23 metadata_function)
$ptlc($base64(text_type)) = $ptascii("array")
S_return = $mcnar_seek(S_args, 1, 5000)[.COMPLETION = NORMAL]
$mcnar_ready(S_return, 1)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)
$lookup(S_return.ENV, $ptascii("changed")) = (n_original_x)
n_formal =/= n_original_x /\ ~(n_formal <- S_return.REFCELLS)
S_return.STORE[n_formal] = DEFINED (PINT 17)
S_return.STORE[n_original_x] = DEFINED (PINT 23)
S_return.RESULT = KNOWN (PINT 7)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = eps
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("r")) = (n_r)
S_return.STORE[n_prefix] = DEFINED (PINT 2)
S_return.STORE[n_r] = DEFINED (PINT 11)
$heap_owners($heap_graph(S_return), HCELL n_original_x) = 1
$heap_owners($heap_graph(S_return), HCELL n_prefix) = 3
$typed_return_task_valid(S_return, z_return)
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PINT 7, pfunction_producer.CODE.STRICT) = TYPEREJECT
S_rejected = $typed_return_value(S_return, z_return)
S_rejected.COMPLETION = THROWN "TypeError" ptbytes_message z_return
S_rejected.STORE = S_return.STORE /\ S_rejected.ARRAYS = S_return.ARRAYS
S_rejected.ALLOCATIONS = S_return.ALLOCATIONS /\ S_rejected.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS
S_rejected.PROPREFS = S_return.PROPREFS /\ S_rejected.REFCOERCIONS = S_return.REFCOERCIONS
$mcvr_output(S_rejected.EVENTS) = $ptascii("P;M:17:23:0;")
S_caught = $mcnar_seek(S_return, 2, 10000)[.COMPLETION = NORMAL]
$mcnar_ready(S_caught, 2)
$lookup(S_caught.ENV, $ptascii("x")) = eps
$lookup(S_caught.ENV, $ptascii("r")) = (n_r)
S_caught.STORE[n_r] = DEFINED (PINT 11)
$lookup(S_caught.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(S_caught.ENV, $ptascii("prefixAlias")) = (n_prefix)
S_caught.STORE[n_prefix] = DEFINED (PINT 2)
$heap_owners($heap_graph(S_caught), HCELL n_prefix) = 2
~((HCELL n_original_x) <- S_caught.ALLOCATIONS) /\ ~((HCELL n_formal) <- S_caught.ALLOCATIONS)
$lookup(S_caught.ENV, $ptascii("e")) = (n_exception_cv)
S_caught.STORE[n_exception_cv] = DEFINED (POBJECT n_exception)
$throwable_live(S_caught, n_exception)
$heap_valid($heap_graph(S_caught)) /\ $call_descriptors_valid(S_caught)
S_prefinal = $mcnar_seek(S_caught, 3, 5000)[.COMPLETION = NORMAL]
$mcnar_ready(S_prefinal, 3)
$lookup(S_prefinal.ENV, $ptascii("e")) = eps
~((HCELL n_exception_cv) <- S_prefinal.ALLOCATIONS) /\ ~((HOBJECT n_exception) <- S_prefinal.ALLOCATIONS)
S_prefinal.STORE[n_r] = DEFINED (PINT 11)
S_prefinal.STORE[n_prefix] = DEFINED (PINT 31)
S_prefinal.STORE[n_snapshot] = DEFINED (PINT 17)
$heap_valid($heap_graph(S_prefinal)) /\ $call_descriptors_valid(S_prefinal)
S_full = $drive(S_prefinal, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("x")) = eps
$lookup(S_full.ENV, $ptascii("r")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps
$lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
$lookup(S_full.ENV, $ptascii("snapshot")) = eps
~((HCELL n_r) <- S_full.ALLOCATIONS) /\ ~((HCELL n_prefix) <- S_full.ALLOCATIONS) /\ ~((HCELL n_snapshot) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native = json.loads(provenance.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 2
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), CATALOGUE, provenance, Path(array_review.__file__), Path(array_review.prior.__file__)]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row = rows[case['id']]
            source = Path(row['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            current_derived = []
            if index == 0:
                common = array_review.prior.COMMON[1:]
                replacements = {
                    '$mcvr_seek(S_initial, 1500)': '$mcvr_seek(S_after_return, 1500)',
                    'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*':
                        'S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*',
                    '$call_argument_origin(S_pre, (porigin_call), 0)': '$named_origin(S_pre, (porigin_call), 1)',
                    '$call_argument_expression(S_pre, (porigin_call), 0)': '$named_expression($named_source(S_pre, (porigin_call), 1))',
                    '"J;M:5:13;"': '"N;M:5:13;"',
                    'pfunction_producer.SIGNATURE.RETURNS = eps': 'pfunction_producer.SIGNATURE.RETURNS = ' + NULLABLE,
                    '])) ABSENT phpType23 metadata_function)': '])) (' + RAW_RETURN + ') phpType23 metadata_function)',
                }
                for old, new in replacements.items():
                    common = [line.replace(old, new) for line in common]
                actual_return = [line.replace('[(PTBRANCH ([PTBUILTIN "array"]))]', NULLABLE) for line in array_review.RETURN]
                conditions = [initial] + actual_return + common + [
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
                header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), ' + RAW_RETURN + ', pfunction_producer.SIGNATURE)'
                conditions += [('~' if args.front else '') + header,
                    ('~' if args.front else '') + '$named_reference_notice_pending(S_pre)']
                if not args.front:
                    full = array_review.prior.FULL[1:]
                    full = [line.replace('$positional_reference_notice_pending(S_pre)', '$named_reference_notice_pending(S_pre)')
                        .replace('perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call',
                            'perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call') for line in full]
                    at = full.index('S_full = $drive(S_notice, 10000)')
                    full[at:at + 1] = array_review.WRITTEN + ['S_full = $drive(S_scalar, 10000)']
                    conditions += full + [
                        'pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\\ pnamedargs_after.NAMED = eps',
                        'perrorcall.LINE = ' + str(case['notice_line']),
                        '$lookup(S_full.ENV, $ptascii("prefix")) = eps /\\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps',
                        '$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
                    current_derived = [
                        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
                        '~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE)',
                        '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])'),
                        '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "array"]))]])'),
                        '~' + header.replace('NIdentifier (BYTES text_type) metadata_type', 'NIdentifier (BYTES "aW50") metadata_type'),
                        '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]], psparam_last]])'),
                        '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])',
                        'S_zero = $drive(S_notice, 0)',
                        'S_zero.COMPLETION = BUDGET /\\ S_zero[.COMPLETION = NORMAL] = S_notice',
                    ]
            else:
                conditions = [initial] + PRIORITY + ['$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
            case_specs.append('dec $mcnar_case' + str(index) + '() : bool\ndef $mcnar_case' + str(index) + '() = true\n' +
                ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
            reached += conditions
            derived += current_derived
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) +
        '\ndec $main() : bool\ndef $main() = true\n  -- if $mcnar_case0()\n  -- if $mcnar_case1()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json',
        'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
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
        front=args.front, conditions=len(reached) + len(derived), reached_conditions=len(reached),
        derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('multi-cv-nullable-array-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

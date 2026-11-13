"""Check duplicate scalar receives, saved REQUEST bytes and strict argument priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
import multi_cv_array_formal_producer_reference_notice_review_state as prior
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_scalar_formal_producer_reference_notice_review_cases.json')
array = prior.array
PREFIX = array.prior.PREFIX + prior.PREFIX[prior.PREFIX.index('dec $mcaf_ready'):].replace('ReviewNotice56', 'ReviewNotice57') + r"""
dec $mcsfr_ready(pstate, nat) : bool
def $mcsfr_ready(S, 0) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice57\\Named\\make")
def $mcsfr_ready(S, 1) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 1]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice57\\Named\\make")
def $mcsfr_ready(S, 2) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice57\\Named\\make")
def $mcsfr_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("N;M:1:1;H:8:body:2;F:31:17;R:X7:29:17:43;")
def $mcsfr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("N;M:1:1;H:8:body:2;F:31:17;R:X7:29:17:43;D:47:29:17:43;")
def $mcsfr_ready(S, n_stage) = false -- otherwise
dec $mcsfr_seek(pstate, nat, nat) : pstate
def $mcsfr_seek(S, n_stage, n) = S -- if $mcsfr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcsfr_seek(S, n_stage, n) = $mcsfr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcsfr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcsfr_seek(S, n_stage, n) = S -- otherwise
"""
PRIORITY = prior.PRIORITY[:]
PRIORITY.insert(PRIORITY.index('pcallcontext.ARGC = 2'), '$typed_caller_strict(S_receive)')
PARAMETERS = [line.replace('$ptlc($base64(text_parameter_last)) = $ptascii("array")', '$ptlc($base64(text_parameter_last)) = $ptascii("string")')
    .replace('psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]', 'psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]') for line in prior.PARAMETERS]
FRONT = r"""
S_initial.COMPLETION = BUDGET
S_first = $mcsfr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$mcsfr_ready(S_first, 0)
S_first.TODO = [TYPE_RECEIVE porigin 0]
$receiving_function(S_first, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\ psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]
psparam_first.REQUIRED /\ psparam_last.REQUIRED /\ ~psparam_first.VARIADIC /\ ~psparam_last.VARIADIC
psparam_first.DEFAULT = PSNONE /\ psparam_last.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
~$typed_caller_strict(S_first)
$typed_receive_valid(S_first, porigin, 0)
$lookup(S_first.ENV, $ptascii("saved")) = (n_formal)
$lookup(S_first.ENV, $ptascii("changed")) = (n_x)
n_formal =/= n_x /\ ~(n_formal <- S_first.REFCELLS) /\ n_x <- S_first.REFCELLS
S_first.STORE[n_formal] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
S_first.STORE[n_x] = DEFINED pvalue_original
$string_carrier_valid(S_first, pvalue_original)
S_first.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
S_first.STORE[n_copy] = DEFINED pvalue_original
S_first.STORE[n_prefix] = DEFINED (PINT 2)
$typed_parameter_conversion(S_first, psparam_first, pvalue_original) = TYPEVALUE pvalue_original
S_last = $mcsfr_seek(S_first, 1, 200)[.COMPLETION = NORMAL]
$mcsfr_ready(S_last, 1)
$typed_receive_valid(S_last, porigin, 1)
~$typed_caller_strict(S_last)
S_last.STORE[n_formal] = DEFINED pvalue_original /\ S_last.STORE[n_x] = DEFINED pvalue_original
S_last.STORE[n_copy] = DEFINED pvalue_original
~$typed_parameter_source(S_last, psparam_last)
$typed_parameter_conversion(S_last, psparam_last, pvalue_original) = TYPEINTEGER pvalue_original
S_received_budget = $drive_steps(S_last, 1)
S_received_budget.COMPLETION = BUDGET
S_received = S_received_budget[.COMPLETION = NORMAL]
S_received.STORE[n_formal] = DEFINED pvalue_original
S_received.STORE[n_x] = DEFINED (PINT 17)
S_received.STORE[n_copy] = DEFINED pvalue_original
S_received.ARRAYS = S_last.ARRAYS /\ S_received.PROPREFS = S_last.PROPREFS /\ S_received.REFCOERCIONS = S_last.REFCOERCIONS
$heap_valid($heap_graph(S_received)) /\ $call_descriptors_valid(S_received)
$mcvr_output(S_received.EVENTS) = $ptascii("N;")
S_return = $mcsfr_seek(S_received, 2, 5000)[.COMPLETION = NORMAL]
$mcsfr_ready(S_return, 2)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.STORE[n_formal] = DEFINED pvalue_original
S_return.STORE[n_x] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))
S_return.RESULT = KNOWN (PARRAY n_return)
S_return.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_original)]
$typed_return_task_valid(S_return, z_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_return)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_pre = $mcvr_seek(S_return, 5000)[.COMPLETION = NORMAL]
$mcvr_ready(S_pre)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
S_pre.RESULT = KNOWN (PARRAY n_return)
S_pre.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_original)]
$lookup(S_pre.ENV, $ptascii("x")) = (n_x)
S_pre.STORE[n_x] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))
S_pre.STORE[n_copy] = DEFINED pvalue_original /\ S_pre.STORE[n_prefix] = DEFINED (PINT 2)
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("saved")) = eps /\ $lookup(S_pre.ENV, $ptascii("changed")) = eps
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\ pnamedargs.NAMED = eps
$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3
$parameter_backing_at(S_pre.PARAMETERBACKINGS, n_x) = eps
$propref_at(S_pre.PROPREFS, n_x) = eps /\ $reference_coercion_at(S_pre.REFCOERCIONS, n_x) = eps
$string_carrier_valid(S_pre, pvalue_original)
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19 (SEQUENCE ([phpType7_first, phpType7_last])) metadata_call
phpType7_first = NArg ABSENT expression_first (BOOLEAN false) (BOOLEAN false) metadata_first_arg
phpType7_last = NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN false) metadata_last_arg
$reference_cv(expression_first) = ($ptascii("x")) /\ $reference_cv(expression_last) = ($ptascii("x"))
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) phpType18_return phpType23 metadata_function)
phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_first_type) metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter
phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_last_type) metadata_last_type) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter
$ptlc($base64(text_first_type)) = $ptascii("string") /\ $ptlc($base64(text_last_type)) = $ptascii("int")
phpType18_return = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("array")
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression_last)
$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = 8
$mcvr_output(S_pre.EVENTS) = $ptascii("N;M:1:1;")
""".strip().splitlines()
FULL = r"""
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\ pnamedargs_after.NAMED = eps
perrorcall.LINE = 8
S_notice.STORE[n_private] = DEFINED (PARRAY n_return)
n_private =/= n_formal /\ n_private =/= n_x /\ n_private =/= n_prefix
$error_call_valid(S_notice, perrorcall)
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_notice)) /\ $call_descriptors_valid(S_notice)
S_written = $mcsfr_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]
$mcsfr_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_written)
S_written.ARRAYS[n_written].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_written)]
$string_bytes(pvalue_written) = ($ptascii("X7"))
pvalue_written = PSTRING ($ptascii("X7"))
S_written.STORE[n_copy] = DEFINED pvalue_original
$string_carrier_valid(S_written, pvalue_original)
S_written.STORE[n_x] = DEFINED (PINT 29) /\ S_written.STORE[n_prefix] = DEFINED (PINT 43)
$heap_owners($heap_graph(S_written), HARRAY n_written) = 1
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_retired = $mcsfr_seek(S_written, 4, 5000)[.COMPLETION = NORMAL]
$mcsfr_ready(S_retired, 4)
S_retired.STORE[n_private] = DEFINED (PINT 47)
~((HARRAY n_written) <- S_retired.ALLOCATIONS)
S_retired.STORE[n_copy] = DEFINED pvalue_original
$string_carrier_valid(S_retired, pvalue_original)
S_full = $drive(S_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("r")) = eps /\ $lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HCELL n_x) <- S_full.ALLOCATIONS)
~((HARRAY n_return) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_written) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()


def normal(initial, case, front):
    arguments = '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), phpType18_return, pfunction_producer.SIGNATURE)'
    conditions = [initial] + FRONT + [('~' if front else '') + p for p in (arguments, header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        conditions += FULL + ['$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        derived = ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = eps], psparam_last]]'),
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam_first, psparam_last[.BYREF = false]]]'),
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam_first[.REQUIRED = false], psparam_last]]'),
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam_first, psparam_last[.VARIADIC = true]]]'),
            'S_zero = $drive(S_notice, 0)', r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice',
            '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)']
    return conditions, derived


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
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(array.__file__), Path(array.prior.__file__)]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
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
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            if index == 0:
                conditions, current_derived = normal(initial, case, args.front)
            else:
                conditions, current_derived = [initial] + PRIORITY + PARAMETERS + ['$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')'], []
            case_specs.append('dec $mcaf_case' + str(index) + '() : bool\ndef $mcaf_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $mcaf_case0()\n  -- if $mcaf_case1()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('multi-cv-scalar-formal-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

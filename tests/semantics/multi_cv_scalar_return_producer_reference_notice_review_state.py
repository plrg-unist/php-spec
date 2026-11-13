"""Check INT/BOOL conversion, duplicate actuals, missing caller names and untyped private cells."""
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
CATALOGUE = Path(__file__).with_name('multi_cv_scalar_return_producer_reference_notice_review_cases.json')
PREFIX = r"""
dec $mcsr_output(pevent*) : ptbytes
def $mcsr_output(eps) = eps
def $mcsr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mcsr_output(pevent*)
dec $mcsr_ready(pstate, nat) : bool
def $mcsr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("ReviewNotice51\\Int\\make"), $ptascii("ReviewNotice51\\Bool\\make")]
def $mcsr_ready(S, 1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.SIGNATURE.BYREF
def $mcsr_ready(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.SIGNATURE.BYREF
def $mcsr_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcsr_output(S.EVENTS) <- [$ptascii("N;M:17:23:0;H:8:0:5;F:29:17:1;R:23:31:37:17:1:1;D:41:17:31;"), $ptascii("N;M:0:23:0;H:8:0:5;F:29:1;R:Xody:body:31:37:0:1:1;")]
def $mcsr_ready(S, n_stage) = false -- otherwise
dec $mcsr_seek(pstate, nat, nat) : pstate
def $mcsr_seek(S, n_stage, n) = S -- if $mcsr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcsr_seek(S, n_stage, n) = $mcsr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcsr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcsr_seek(S, n_stage, n) = S -- otherwise
"""
RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $mcsr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$mcsr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
~pfunction_producer.SIGNATURE.BYREF /\ ~pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.TYPE = eps /\ psparam_last.TYPE = eps
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN text_kind]))]
$origin_node(S_return.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) (NIdentifier (BYTES text_type) metadata_type) phpType23 metadata_function)
$ptlc($base64(text_type)) = $ptascii(text_kind)
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)
$lookup(S_return.ENV, $ptascii("changed")) = (n_original_x)
n_formal =/= n_original_x /\ ~(n_formal <- S_return.REFCELLS)
n_original_x <- S_return.REFCELLS
S_return.STORE[n_formal] = DEFINED (PARRAY n_root)
S_return.STORE[n_original_x] = DEFINED (PINT 23)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_string)]
S_return.RESULT = KNOWN pvalue_string
$string_carrier_valid(S_return, pvalue_string)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = eps
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("y")) = (n_y)
$lookup(psymboltable_caller.ENV, $ptascii("yAlias")) = (n_y)
S_return.STORE[n_copy] = DEFINED (PARRAY n_root)
S_return.STORE[n_snapshot] = DEFINED pvalue_string
S_return.STORE[n_y] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_return), HARRAY n_root) = 2
$heap_owners($heap_graph(S_return), HCELL n_original_x) = 1
$heap_owners($heap_graph(S_return), HCELL n_y) = 3
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN pvalue_expected
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS /\ S_checked.ALLOCATIONS = S_return.ALLOCATIONS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN pvalue_expected) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN pvalue_expected) porigin_return?) = eps
$heap_owners($heap_graph(S_after_return), HARRAY n_root) = 2
$heap_valid($heap_graph(S_after_return)) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()
PRE = r"""
S_pre = $mcsr_seek(S_after_return, 1, 5000)[.COMPLETION = NORMAL]
$mcsr_ready(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN pvalue_expected
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$lookup(S_pre.ENV, $ptascii("x")) = eps
~((HCELL n_original_x) <- S_pre.ALLOCATIONS) /\ ~((HCELL n_formal) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("y")) = (n_y)
$lookup(S_pre.ENV, $ptascii("yAlias")) = (n_y)
S_pre.STORE[n_y] = DEFINED (PINT 5)
S_pre.STORE[n_copy] = DEFINED (PARRAY n_root)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_string)]
S_pre.STORE[n_snapshot] = DEFINED pvalue_string
$string_carrier_valid(S_pre, pvalue_string)
$heap_owners($heap_graph(S_pre), HARRAY n_root) = 1
$heap_owners($heap_graph(S_pre), HCELL n_y) = 3
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_y)] /\ pnamedargs.NAMED = eps
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = expression_producer
expression_producer = NExprFuncCall phpType19 (SEQUENCE ([phpType7_first, phpType7_last])) metadata_call
phpType7_first = NArg ABSENT expression_first (BOOLEAN false) (BOOLEAN false) metadata_first_arg
phpType7_last = NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN false) metadata_last_arg
expression_first = NExprVariable (BYTES text_first) metadata_first
expression_last = NExprVariable (BYTES text_last) metadata_last
$reference_cv(expression_first) = ($ptascii("x"))
$reference_cv(expression_last) = ($ptascii("x"))
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression_last)
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])
$named_reference_notice_operand(S_pre, S_pre.RESULT)
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()
PRIVATE = r"""
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_y), NAMED_SENT (REFERENCE n_private)] /\ pnamedargs_after.NAMED = eps
S_notice.STORE[n_private] = DEFINED pvalue_expected
$node_children(S_notice, HCELL n_private) = eps
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_root) = 1
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_resume = $mcsr_seek(S_notice, 2, 7000)[.COMPLETION = NORMAL]
$mcsr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
$lookup(S_resume.ENV, $ptascii("x")) = (n_new_x)
n_new_x =/= n_original_x /\ n_new_x =/= n_private /\ n_new_x =/= n_y
S_resume.STORE[n_new_x] = DEFINED (PINT 37)
S_resume.STORE[n_y] = DEFINED (PINT 29)
S_resume.STORE[n_private] = DEFINED pvalue_expected
S_prefinal = $mcsr_seek(S_resume, 3, 10000)[.COMPLETION = NORMAL]
$mcsr_ready(S_prefinal, 3)
$lookup(S_prefinal.ENV, $ptascii("r")) = (n_private)
S_prefinal.STORE[n_y] = DEFINED (PINT 31)
S_prefinal.STORE[n_new_x] = DEFINED (PINT 37)
S_prefinal.STORE[n_copy] = DEFINED (PARRAY n_root)
S_prefinal.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_string)]
S_prefinal.STORE[n_snapshot] = DEFINED pvalue_string
$string_carrier_valid(S_prefinal, pvalue_string)
$parameter_backing_at(S_prefinal.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_prefinal.PROPREFS, n_private) = eps
$reference_coercion_at(S_prefinal.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_prefinal)) /\ $call_descriptors_valid(S_prefinal)
S_full = $drive(S_prefinal, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("r")) = eps
$lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("y")) = eps
$lookup(S_full.ENV, $ptascii("yAlias")) = eps
$lookup(S_full.ENV, $ptascii("x")) = (n_new_x)
S_full.STORE[n_new_x] = DEFINED (PINT 37)
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_root) <- S_full.ALLOCATIONS)
S_full.STORE[n_snapshot] = DEFINED pvalue_string
$string_carrier_valid(S_full, pvalue_string)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()
CONTROLS = r"""
~$error_call_valid(S_notice, perrorcall[.LINE = 9])
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), ABSENT, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_type, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]], psparam_last]])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
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
    paths = [Path(__file__), CATALOGUE, provenance]
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
            kind = 'int' if case['id'].startswith('named-int-') else 'bool'
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            values = ['text_kind = ' + json.dumps(kind), 'pvalue_expected = ' + ('PINT 17' if kind == 'int' else 'PBOOL false')]
            payload = ('pvalue_string = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))' if kind == 'int'
                else 'pvalue_string = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))')
            conditions = [initial] + values + RETURN + [payload] + PRE
            conditions += ['$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = ' + str(case['notice_line'])]
            header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE)'
            conditions += [('~' if args.front else '') + header, ('~' if args.front else '') + '$named_reference_notice_pending(S_pre)']
            current_derived = []
            if not args.front:
                conditions += PRIVATE + ['perrorcall.LINE = ' + str(case['notice_line']),
                    '$mcsr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
                if kind == 'int':
                    conditions += ['S_prefinal.STORE[n_private] = DEFINED (PARRAY n_private_array)',
                        'S_prefinal.ARRAYS[n_private_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 41))]',
                        '$node_children(S_prefinal, HCELL n_private) = [HARRAY n_private_array]']
                else:
                    conditions += ['S_prefinal.STORE[n_private] = DEFINED (PSTRING ($ptascii("Xody")))',
                        '$lookup(S_prefinal.ENV, $ptascii("hold")) = (n_hold)',
                        'S_prefinal.STORE[n_hold] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))',
                        '$lookup(S_full.ENV, $ptascii("hold")) = eps']
                current_derived = CONTROLS
            case_specs.append('dec $mcsr_case' + str(index) + '() : bool\ndef $mcsr_case' + str(index) + '() = true\n' +
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
        '\ndec $main() : bool\ndef $main() = true\n  -- if $mcsr_case0()\n  -- if $mcsr_case1()\n')
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
    print('multi-cv-scalar-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

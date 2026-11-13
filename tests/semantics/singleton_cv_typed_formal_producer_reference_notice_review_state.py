"""Ground singleton nullable-array snapshots and strict scalar entry rejection."""
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
CATALOGUE = Path(__file__).with_name('singleton_cv_typed_formal_producer_reference_notice_review_cases.json')
PREFIX = r"""
dec $scfr_output(pevent*) : ptbytes
def $scfr_output(eps) = eps
def $scfr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $scfr_output(pevent*)
dec $scfr_ready(pstate, nat) : bool
def $scfr_ready(S, 0) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice59\\Named\\make")
def $scfr_ready(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice59\\Named\\make")
def $scfr_ready(S, 2) = true
  -- if S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;")
def $scfr_ready(S, 3) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;H:8:5:2;")
def $scfr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;H:8:5:2;F:29:13;R:23:17:5:31;")
def $scfr_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;H:8:5:2;F:29:13;R:23:17:5:31;D:41:17:5:31;")
def $scfr_ready(S, 6) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice59\\Priority\\make")
def $scfr_ready(S, 7) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("P;C:11:2:1:1;")
def $scfr_ready(S, 8) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("P;C:11:2:1:1;D:11:31:23:1;")
def $scfr_ready(S, n_stage) = false -- otherwise
dec $scfr_seek(pstate, nat, nat) : pstate
def $scfr_seek(S, n_stage, n) = S -- if $scfr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $scfr_seek(S, n_stage, n) = $scfr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$scfr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scfr_seek(S, n_stage, n) = S -- otherwise
"""
FRONT = r"""
S_initial.COMPLETION = BUDGET
S_receive = $scfr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_receive, 0)
S_receive.TODO = [TYPE_RECEIVE porigin 0]
$receiving_function(S_receive, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]
~pfunction_producer.SIGNATURE.BYREF
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]
~$typed_caller_strict(S_receive)
$typed_receive_valid(S_receive, porigin, 0)
$lookup(S_receive.ENV, $ptascii("saved")) = (n_formal)
S_receive.STORE[n_formal] = DEFINED (PARRAY n_original)
~(n_formal <- S_receive.REFCELLS)
S_receive.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
n_formal =/= n_x /\ n_x =/= n_copy /\ n_prefix =/= n_x
S_receive.STORE[n_x] = DEFINED (PARRAY n_original)
S_receive.STORE[n_copy] = DEFINED (PARRAY n_original)
S_receive.STORE[n_prefix] = DEFINED (PINT 2)
S_receive.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
$typed_parameter_conversion(S_receive, psparam, PARRAY n_original) = TYPEVALUE (PARRAY n_original)
$parameter_backing_at(S_receive.PARAMETERBACKINGS, n_formal) = eps
$propref_at(S_receive.PROPREFS, n_formal) = eps /\ $reference_coercion_at(S_receive.REFCOERCIONS, n_formal) = eps
$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)
$scfr_output(S_receive.EVENTS) = $ptascii("N;")
S_received_budget = $drive_steps(S_receive, 1)
S_received_budget.COMPLETION = BUDGET
S_received = S_received_budget[.COMPLETION = NORMAL]
S_received.STORE = S_receive.STORE /\ S_received.ARRAYS = S_receive.ARRAYS
S_return = $scfr_seek(S_received, 1, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_return, 1)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.STORE[n_formal] = DEFINED (PARRAY n_return)
S_return.RESULT = VARIABLE ($ptascii("saved")) z_saved
S_resolved = $resolve_at(S_return, S_return.RESULT, z_return)
S_resolved.COMPLETION = NORMAL /\ S_resolved.RESULT = KNOWN (PARRAY n_return)
n_return =/= n_original
S_return.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]
S_return.STORE[n_x] = DEFINED (PARRAY n_original) /\ S_return.STORE[n_copy] = DEFINED (PARRAY n_original)
S_return.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
$typed_return_task_valid(S_return, z_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_return)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
S_pre = $scfr_seek(S_return, 2, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_pre, 2)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
S_pre.RESULT = KNOWN (PARRAY n_return)
S_pre.STORE[n_x] = DEFINED (PARRAY n_original) /\ S_pre.STORE[n_copy] = DEFINED (PARRAY n_original)
S_pre.STORE[n_prefix] = DEFINED (PINT 2)
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\ pnamedargs.NAMED = eps
$heap_owners($heap_graph(S_pre), HARRAY n_original) = 2
$heap_owners($heap_graph(S_pre), HARRAY n_return) = 1
$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19 (SEQUENCE ([phpType7])) metadata_call
phpType7 = NArg ABSENT expression (BOOLEAN false) (BOOLEAN false) metadata_arg
$reference_cv(expression) = ($ptascii("x"))
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
$ptlc($base64(text_type)) = $ptascii("array")
phpType18 = NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return_nullable
$ptlc($base64(text_return)) = $ptascii("array")
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression)
$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression) = 8
$scfr_output(S_pre.EVENTS) = $ptascii("N;M:5;")
""".strip().splitlines()
FULL = r"""
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\ pnamedargs_after.NAMED = eps
perrorcall.LINE = 8 /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED (PARRAY n_return)
n_private =/= n_formal /\ n_private =/= n_x /\ n_private =/= n_copy /\ n_private =/= n_prefix
n_private <- S_notice.REFCELLS
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_notice)) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $scfr_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_x] = DEFINED (PARRAY n_current)
n_current =/= n_original /\ n_current =/= n_return
S_resume.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]
S_resume.STORE[n_copy] = DEFINED (PARRAY n_original)
S_resume.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
S_resume.STORE[n_prefix] = DEFINED (PINT 29)
S_resume.STORE[n_private] = DEFINED (PARRAY n_return)
S_resume.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]
$heap_owners($heap_graph(S_resume), HARRAY n_original) = 1
$heap_owners($heap_graph(S_resume), HARRAY n_current) = 1
$heap_owners($heap_graph(S_resume), HARRAY n_return) = 1
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
S_written = $scfr_seek(S_resume, 4, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_written)
S_written.ARRAYS[n_written].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23))]
S_written.STORE[n_x] = DEFINED (PARRAY n_current) /\ S_written.STORE[n_copy] = DEFINED (PARRAY n_original)
S_written.STORE[n_prefix] = DEFINED (PINT 31)
$heap_owners($heap_graph(S_written), HARRAY n_written) = 1
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_retired = $scfr_seek(S_written, 5, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_retired, 5)
S_retired.STORE[n_private] = DEFINED (PINT 41)
~((HARRAY n_written) <- S_retired.ALLOCATIONS)
S_full = $drive(S_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("r")) = eps /\ $lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HCELL n_formal) <- S_full.ALLOCATIONS)
~((HARRAY n_original) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_current) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_written) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()
PRIORITY = r"""
S_initial.COMPLETION = BUDGET
S_receive = $scfr_seek(S_initial, 6, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_receive, 6)
S_receive.TODO = [TYPE_RECEIVE porigin 0]
$receiving_function(S_receive, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
psparam.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$typed_caller_strict(S_receive)
$typed_receive_valid(S_receive, porigin, 0)
$lookup(S_receive.ENV, $ptascii("saved")) = (n_formal)
S_receive.STORE[n_formal] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_receive, pvalue_original)
S_receive.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("alias")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("r")) = (n_r)
n_x <- S_receive.REFCELLS /\ ~(n_formal <- S_receive.REFCELLS) /\ n_formal =/= n_x
S_receive.STORE[n_x] = DEFINED pvalue_original /\ S_receive.STORE[n_copy] = DEFINED pvalue_original
S_receive.STORE[n_prefix] = DEFINED (PINT 2) /\ S_receive.STORE[n_r] = DEFINED (PINT 11)
~$typed_parameter_source(S_receive, psparam)
$typed_parameter_conversion(S_receive, psparam, pvalue_original) = TYPEREJECT
$scfr_output(S_receive.EVENTS) = $ptascii("P;")
$origin_node(S_receive.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) (NIdentifier (BYTES text_return) metadata_return) phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
$ptlc($base64(text_type)) = $ptascii("int") /\ $ptlc($base64(text_return)) = $ptascii("array")
$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)
S_rejected = $typed_parameter_value(S_receive, pfunction_producer, 0, pvalue_original)
S_rejected.COMPLETION = THROWN "TypeError" ptbytes_message z_error
S_rejected.STORE = S_receive.STORE /\ S_rejected.ARRAYS = S_receive.ARRAYS
S_rejected.PROPREFS = S_receive.PROPREFS /\ S_rejected.REFCOERCIONS = S_receive.REFCOERCIONS
S_rejected.EVENTS = S_receive.EVENTS
S_caught = $scfr_seek(S_receive, 7, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_caught, 7)
S_caught.CURRENT = eps /\ S_caught.FRAMES = eps
S_caught.STORE[n_x] = DEFINED pvalue_original /\ S_caught.STORE[n_copy] = DEFINED pvalue_original
S_caught.STORE[n_prefix] = DEFINED (PINT 2) /\ S_caught.STORE[n_r] = DEFINED (PINT 11)
~((HCELL n_formal) <- S_caught.ALLOCATIONS)
$lookup(S_caught.ENV, $ptascii("e")) = (n_exception_cv)
S_caught.STORE[n_exception_cv] = DEFINED (POBJECT n_exception)
$throwable_live(S_caught, n_exception)
$heap_valid($heap_graph(S_caught)) /\ $call_descriptors_valid(S_caught)
S_written = $scfr_seek(S_caught, 8, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 8)
S_written.STORE[n_x] = DEFINED (PINT 23) /\ S_written.STORE[n_copy] = DEFINED pvalue_original
S_written.STORE[n_prefix] = DEFINED (PINT 31) /\ S_written.STORE[n_r] = DEFINED (PINT 11)
$string_carrier_valid(S_written, pvalue_original)
$lookup(S_written.ENV, $ptascii("e")) = eps
~((HCELL n_exception_cv) <- S_written.ALLOCATIONS) /\ ~((HOBJECT n_exception) <- S_written.ALLOCATIONS)
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_full = $drive(S_written, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("alias")) = eps /\ $lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps /\ $lookup(S_full.ENV, $ptascii("r")) = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()


def normal(initial, case, front):
    arguments = '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    conditions = [initial] + FRONT + [('~' if front else '') + line for line in (arguments, header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        conditions += FULL + ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        derived = ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = eps]]]'),
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.BYREF = true]]]'),
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.REQUIRED = false]]]'),
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.VARIADIC = true]]]'),
            '~' + arguments.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "array"]))]]]]'),
            '~' + header.replace('phpType18,', 'NNullableType (NIdentifier (BYTES "aW50") metadata_return) metadata_return_nullable,').replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]])'),
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
    paths = [Path(__file__), CATALOGUE, provenance]
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
            conditions, current_derived = normal(initial, case, args.front) if index == 0 else ([initial] + PRIORITY + ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')'], [])
            case_specs.append('dec $scfr_case' + str(index) + '() : bool\ndef $scfr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $scfr_case0()\n  -- if $scfr_case1()\n')
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
    print('singleton-cv-typed-formal-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

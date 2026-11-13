#!/usr/bin/env python3
"""Check request-string snapshots, private cancellation and unchanged nested fences."""
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
CATALOGUE = Path(__file__).with_name('request_string_return_producer_cv_reference_notice_cases.json')

PREFIX = r"""
dec $rq_output(pevent*) : ptbytes
def $rq_output(eps) = eps
def $rq_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $rq_output(pevent*)
dec $rq_ready(pstate, nat) : bool
def $rq_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("RequestStringReturnProducer40\\make") \/ pcallcontext.NAME = $ptascii("RequestStringReturnThrow40\\make") \/ pcallcontext.NAME = $ptascii("RequestArrayChildNotice40\\make")
def $rq_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("RequestStringReturnProducer40\\take") \/ pfunction.NAME = $ptascii("RequestStringReturnThrow40\\take") \/ pfunction.NAME = $ptascii("RequestArrayChildNotice40\\take")
def $rq_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $rq_output(S.EVENTS) = $ptascii("W;M:17;H:1;")
def $rq_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $lookup(S.ENV, $ptascii("r")) = (n_private)
  -- if S.STORE[n_private] = DEFINED pvalue_private
  -- if $string_bytes(pvalue_private) = ($ptascii("19"))
  -- if $rq_output(S.EVENTS) = $ptascii("W;M:17;H:1;F:1;")
def $rq_ready(S, 4) = true
  -- if S.CURRENT = eps
  -- if $rq_output(S.EVENTS) = $ptascii("W;M:17;H:1;F:1;R:19:X7:X7:1;P:Y9:X7:1;")
def $rq_ready(S, 5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
def $rq_ready(S, n_stage) = false -- otherwise
dec $rq_seek(pstate, nat, nat) : pstate
def $rq_seek(S, n_stage, n) = S
  -- if $rq_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $rq_seek(S, n_stage, n) = $rq_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$rq_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $rq_seek(S, n_stage, n) = $rq_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$rq_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $rq_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $rq_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]
$rq_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("RequestStringReturnProducer40\\make")
~pfunction_producer.SIGNATURE.BYREF
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("input")) = (n_source_return)
S_return.STORE[n_source_return] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_original) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN pvalue_original
n_source_return <- S_return.REFCELLS
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
n_copy =/= n_source_return /\ ~(n_copy <- S_return.REFCELLS)
S_return.STORE[n_copy] = DEFINED pvalue_original
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN pvalue_original
S_checked.STORE = S_return.STORE /\ S_checked.STRINGDATA = S_return.STRINGDATA
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN pvalue_original) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN pvalue_original) porigin_return?) = eps
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source_return) = 3 /\ $heap_owners(H_return, HCELL n_copy) = 1
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $rq_seek(S_after_return, 1, 1536)[.COMPLETION = NORMAL]
$rq_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN pvalue_original
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("string")
pssignature = pfunction_producer.SIGNATURE
pssignature.PARAMETERS = [psparam]
psparam.BYREF /\ psparam.TYPE = eps /\ ~psparam.VARIADIC /\ psparam.REQUIRED /\ psparam.DEFAULT = PSNONE
pssignature.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature)
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_cv)
n_source_cv = n_source_return
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_cv)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
S_pre.STORE[n_source_cv] = DEFINED pvalue_original /\ S_pre.STORE[n_copy] = DEFINED pvalue_original
$string_carrier_valid(S_pre, pvalue_original)
~$named_reference_notice_value(pvalue_original)
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
$rq_output(S_pre.EVENTS) = $ptascii("W;M:17;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source_cv) = 2 /\ $heap_owners(H_pre, HCELL n_copy) = 1
$node_children(S_pre, HCELL n_source_cv) = eps /\ $node_children(S_pre, HCELL n_copy) = eps
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

PRIVATE = r"""
$named_reference_notice_root_value(S_pre, pvalue_original)
$named_reference_notice_operand(S_pre, KNOWN pvalue_original)
$positional_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source_cv /\ n_private =/= n_copy
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED pvalue_original
$named_reference_notice_operand(S_notice, REFERENCE n_private)
$node_children(S_notice, HCELL n_private) = eps
$error_call_valid(S_notice, perrorcall)
S_notice.PARAMETERBACKINGS = eps /\ S_notice.PROPREFS = eps /\ S_notice.REFCOERCIONS = eps
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_valid(H_notice)
S_resume = $rq_seek(S_notice, 2, 3000)[.COMPLETION = NORMAL]
$rq_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_source_cv] = DEFINED pvalue_source_changed
pvalue_source_changed = PSTRING_CARRIER (REQUEST_STRING n_source_changed) ($ptascii("X7"))
n_source_changed =/= n_original
S_resume.STORE[n_private] = DEFINED pvalue_original /\ S_resume.STORE[n_copy] = DEFINED pvalue_original
$string_carrier_valid(S_resume, pvalue_source_changed) /\ $string_carrier_valid(S_resume, pvalue_original)
$error_call_valid(S_resume, perrorcall)
S_string = $rq_seek(S_resume, 3, 3000)[.COMPLETION = NORMAL]
$rq_ready(S_string, 3)
$lookup(S_string.ENV, $ptascii("r")) = (n_private)
S_string.STORE[n_private] = DEFINED pvalue_private_changed
pvalue_private_changed = PSTRING_CARRIER (REQUEST_STRING n_private_changed) ($ptascii("19"))
n_private_changed =/= n_original
S_string.STORE[n_source_cv] = DEFINED pvalue_source_changed /\ S_string.STORE[n_copy] = DEFINED pvalue_original
$string_carrier_valid(S_string, pvalue_private_changed) /\ $string_carrier_valid(S_string, pvalue_original)
S_string.PARAMETERBACKINGS = eps /\ S_string.PROPREFS = eps /\ S_string.REFCOERCIONS = eps
H_string = $heap_graph(S_string)
$heap_owners(H_string, HCELL n_private) = 1 /\ $heap_valid(H_string)
S_second = $rq_seek(S_string, 4, 3000)[.COMPLETION = NORMAL]
$rq_ready(S_second, 4)
S_second.STORE[n_private] = DEFINED pvalue_second
pvalue_second = PSTRING_CARRIER (REQUEST_STRING n_second) ($ptascii("Y9"))
$string_carrier_valid(S_second, pvalue_second)
S_second.STORE[n_source_cv] = DEFINED pvalue_source_changed /\ S_second.STORE[n_copy] = DEFINED pvalue_original
S_full = $drive(S_second, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$rq_output(S_full.EVENTS) = $ptascii("W;M:17;H:1;F:1;R:19:X7:X7:1;P:Y9:X7:1;Q:1:X7:1;")
S_full.STORE[n_private] = DEFINED (PINT 31)
S_full.STORE[n_source_cv] = DEFINED pvalue_source_changed /\ S_full.STORE[n_copy] = DEFINED pvalue_original
$propref_at(S_full.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_full.REFCOERCIONS, n_private) = eps
$parameter_backing_at(S_full.PARAMETERBACKINGS, n_private) = eps
$node_children(S_full, HCELL n_private) = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

THROW = r"""
S_throw_pre = $rq_seek(S_throw_initial, 1, 3000)[.COMPLETION = NORMAL]
$rq_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN pvalue_throw
pvalue_throw = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_pre, pvalue_throw)
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call))
$positional_reference_notice_pending(S_throw_pre)
$lookup(S_throw_pre.ENV, $ptascii("source")) = (n_throw_source)
$lookup(S_throw_pre.ENV, $ptascii("sourceAlias")) = (n_throw_source)
$lookup(S_throw_pre.ENV, $ptascii("copy")) = (n_throw_copy)
$lookup(S_throw_pre.ENV, $ptascii("r")) = (n_throw_r)
S_throw_pre.STORE[n_throw_source] = DEFINED pvalue_throw /\ S_throw_pre.STORE[n_throw_copy] = DEFINED pvalue_throw
S_throw_pre.STORE[n_throw_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))
$rq_output(S_throw_pre.EVENTS) = $ptascii("T;M:17;")
n_throw_private = |S_throw_pre.STORE|
S_throw_notice = $drive(S_throw_pre, 1)[.COMPLETION = NORMAL]
S_throw_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_throw) :: ptask_throw_notice*
perrorcall_throw.RESUME = CALL_ARGS pcalltarget_throw eps 1 ([REFERENCE n_throw_private]) (porigin_throw_call) z_throw
S_throw_notice.STORE[n_throw_private] = DEFINED pvalue_throw
$error_call_valid(S_throw_notice, perrorcall_throw)
S_throw_pending = $rq_seek(S_throw_notice, 5, 4000)[.COMPLETION = NORMAL]
$rq_ready(S_throw_pending, 5)
S_throw_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw_pending*
perrorcall_entered.RESUME = perrorcall_throw.RESUME
$error_entered_call_valid(S_throw_pending, perrorcall_entered)
$throwable_live(S_throw_pending, n_exception)
S_throw_pending.STORE[n_throw_private] = DEFINED pvalue_throw /\ S_throw_pending.STORE[n_throw_copy] = DEFINED pvalue_throw
S_throw_pending.STORE[n_throw_source] = DEFINED pvalue_throw_changed
pvalue_throw_changed = PSTRING_CARRIER (REQUEST_STRING n_throw_changed) ($ptascii("X7"))
$string_carrier_valid(S_throw_pending, pvalue_throw_changed) /\ $string_carrier_valid(S_throw_pending, pvalue_throw)
H_throw = $heap_graph(S_throw_pending)
$heap_owners(H_throw, HCELL n_throw_private) = 1 /\ $heap_valid(H_throw)
S_cancel = $drive(S_throw_pending, 1)[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_exception) :: ptask_cancel*
~((HCELL n_throw_private) <- S_cancel.ALLOCATIONS)
$heap_owners($heap_graph(S_cancel), HCELL n_throw_private) = 0
S_cancel.ERRORHANDLER = S_throw_pre.ERRORHANDLER
S_cancel.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
S_throw_full = $drive(S_cancel, 10000)
S_throw_full.COMPLETION = NORMAL /\ S_throw_full.TODO = eps /\ S_throw_full.CURRENT = eps /\ S_throw_full.FRAMES = eps
$rq_output(S_throw_full.EVENTS) = $ptascii("T;M:17;H:1;C:stop:1:X7:X7:1;")
S_throw_full.STORE[n_throw_r] = S_throw_pre.STORE[n_throw_r]
S_throw_full.STORE[n_throw_source] = DEFINED pvalue_throw_changed /\ S_throw_full.STORE[n_throw_copy] = DEFINED pvalue_throw
$heap_valid($heap_graph(S_throw_full)) /\ $call_descriptors_valid(S_throw_full)
""".strip().splitlines()

NESTED = r"""
S_nested_pre = $rq_seek(S_nested_initial, 1, 3000)[.COMPLETION = NORMAL]
$rq_ready(S_nested_pre, 1)
S_nested_pre.RESULT = KNOWN (PARRAY n_nested)
S_nested_pre.TODO = (CALL_SEND pcalltarget_nested eps 0 eps (porigin_nested_call) z_nested) :: ptask_nested_tail*
S_nested_pre.ARRAYS[n_nested].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_nested_leaf)]
S_nested_pre.STORE[n_nested_leaf] = DEFINED pvalue_nested
pvalue_nested = PSTRING_CARRIER (REQUEST_STRING n_nested_string) ($ptascii("17"))
$string_carrier_valid(S_nested_pre, pvalue_nested)
$call_reference_operand_valid(S_nested_pre, REFERENCE n_nested_leaf)
$positional_reference_notice_source(S_nested_pre, pcalltarget_nested, 0, (porigin_nested_call))
~$named_reference_notice_array(S_nested_pre, PARRAY n_nested)
~$named_reference_notice_operand(S_nested_pre, KNOWN (PARRAY n_nested))
~$positional_reference_notice_pending(S_nested_pre)
S_nested_fenced = $drive(S_nested_pre, 1)
S_nested_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_nested_fenced.EVENTS = S_nested_pre.EVENTS
$rq_output(S_nested_fenced.EVENTS) = $ptascii("A;M;")
""".strip().splitlines()

CONTROLS = r"""
~$named_reference_notice_root_value(S_pre, PSTRING ($ptascii("17")))
~$named_reference_notice_operand(S_pre, KNOWN (PSTRING ($ptascii("17"))))
n_bad = |S_pre.STRINGDATA|
pvalue_bad = PSTRING_CARRIER (REQUEST_STRING n_bad) ($ptascii("17"))
~$string_carrier_valid(S_pre, pvalue_bad)
~$named_reference_notice_root_value(S_pre, pvalue_bad)
~$named_reference_notice_operand(S_pre, KNOWN pvalue_bad)
~$named_reference_notice_root_value(S_pre, PSTRING_CARRIER (REQUEST_STRING n_original) ($ptascii("18")))
S_nul = S_pre[.STRINGDATA = S_pre.STRINGDATA ++ [[0]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING n_bad) [0]
$string_carrier_valid(S_nul, pvalue_nul)
~$named_reference_notice_root_value(S_nul, pvalue_nul)
~$named_reference_notice_operand(S_nul, KNOWN pvalue_nul)
S_bad_reference = S_notice[.STORE = $set_cell(S_notice.STORE, n_private, DEFINED pvalue_bad)]
~$named_reference_notice_operand(S_bad_reference, REFERENCE n_private)
S_backed = S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction_producer.ORIGIN, INDEX 0, CELL n_private, LINE z, VALUE ($ptascii("17"))}]]
~$named_reference_notice_operand(S_backed, REFERENCE n_private)
S_sourced = S_notice[.PROPREFS = [{CELL n_private, SOURCES eps}]]
~$named_reference_notice_operand(S_sourced, REFERENCE n_private)
S_coerced = S_notice[.REFCOERCIONS = [{CELL n_private, SITE pfunction_producer.ORIGIN, LINE z, VALUE ($ptascii("17"))}]]
~$named_reference_notice_operand(S_coerced, REFERENCE n_private)
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
~$error_call_valid(S_notice, perrorcall[.RESUME = CALL_ARGS pcalltarget eps 1 ([KNOWN pvalue_original]) (porigin_call) z])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)
S_zero_throw = $drive(S_throw_pending, 0)
S_zero_throw.COMPLETION = BUDGET /\ S_zero_throw[.COMPLETION = NORMAL] = S_throw_pending
$drive($drive(S_zero_throw[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_throw_pending, 2)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    selected = [0] if args.front else [0, 1, 2]
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
    source = sources[0]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    for i in selected:
        case, record = cases[i], records[cases[i]['id']]
        assert record['passed'] and record['exit'] == 0 and not record['timeout'] and not record['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == record['source_sha256']
        assert Path(record['stdout']).read_bytes() == record['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(record['stderr']).read_bytes() == record['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in selected:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources[i].read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            fixtures[i] = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    def initial(name, i):
        return name + ' = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
    reached = [initial('S_initial', 0)] + RETURN + COMMON
    if args.front:
        derived = [
            '~$named_reference_notice_operand(S_pre, KNOWN pvalue_original)',
            '~$positional_reference_notice_pending(S_pre)',
            'S_fenced = $drive(S_pre, 1)',
            'S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
            'S_fenced.EVENTS = S_pre.EVENTS',
            'S_fenced.STORE = S_pre.STORE ++ [DEFINED pvalue_original]',
            'S_fenced.STORE[n_source_cv] = S_pre.STORE[n_source_cv]',
        ]
    else:
        reached += PRIVATE + [initial('S_throw_initial', 1)] + THROW + [initial('S_nested_initial', 2)] + NESTED
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = modules + [runner, Path(__file__), CATALOGUE, fixture, native_path, source, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
    watched += [ROOT / path for path in ('tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for i in selected:
        watched += [sources[i], Path(records[cases[i]['id']]['stdout']), Path(records[cases[i]['id']]['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in watched}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': 'request-string-return-front' if args.front else 'request-string-return-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

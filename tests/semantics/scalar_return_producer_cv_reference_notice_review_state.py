#!/usr/bin/env python3
"""Ground strict int-to-float DIM conversion, formal-array retirement and the separate Notice cell."""
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
CATALOGUE = Path(__file__).with_name('scalar_return_producer_cv_reference_notice_review_cases.json')
PREFIX = r"""
dec $nrpr_output(pevent*) : ptbytes
def $nrpr_output(eps) = eps
def $nrpr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nrpr_output(pevent*)
dec $nrpr_ready(pstate, nat) : bool
def $nrpr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice39\\Primary\\make")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:5;")
def $nrpr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PFLOAT 4617315517961601024)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice39\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:5;")
def $nrpr_ready(S, 2) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice39\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:5;H;")
def $nrpr_ready(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN PNULL
  -- if $lookup(S.ENV, $ptascii("r")) = (n_private)
  -- if S.STORE[n_private] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("peer")))
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:5;H;F:1;")
def $nrpr_ready(S, n_stage) = false -- otherwise
dec $nrpr_seek(pstate, nat, nat) : pstate
def $nrpr_seek(S, n_stage, n) = S
  -- if $nrpr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $nrpr_seek(S, n_stage, n) = $nrpr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$nrpr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nrpr_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $nrpr_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]
$nrpr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("ReviewNotice39\\Primary\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "float"]))]
$typed_return_task_valid(S_return, z_return)
S_return.ORIGIN = (porigin_return_source)
$origin_node(S_return.SOURCES, porigin_return_source) = (NStmtReturn (NExprArrayDimFetch expression_return_base (NScalarString (BYTES text_return_key) metadata_return_key) metadata_return_dim) metadata_return_statement)
$reference_cv(expression_return_base) = ($ptascii("input"))
$base64(text_return_key) = $ptascii("leaf")
$lookup(S_return.ENV, $ptascii("input")) = (n_formal)
$lookup(S_return.ENV, $ptascii("source")) = (n_source_return)
n_formal =/= n_source_return
~(n_formal <- S_return.REFCELLS) /\ n_source_return <- S_return.REFCELLS
S_return.STORE[n_formal] = DEFINED (PARRAY n_root)
S_return.STORE[n_source_return] = DEFINED (PINT 17)
S_return.RESULT = KNOWN (PINT 5)
S_return.FRAMES = [pframe_caller]
pframe_caller.LOCALS = eps
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
S_return.STORE[n_leaf] = DEFINED (PINT 5)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PINT 5, pfunction_producer.CODE.STRICT) = TYPEVALUE (PFLOAT 4617315517961601024)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PFLOAT 4617315517961601024)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS /\ S_checked.ALLOCATIONS = S_return.ALLOCATIONS
S_checked.FUNCTIONS = S_return.FUNCTIONS /\ S_checked.DECLARATIONS = S_return.DECLARATIONS
S_return_step = $drive(S_return, 1)
S_return_step.COMPLETION = BUDGET
S_after_return = S_return_step[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PFLOAT 4617315517961601024)) porigin_return?) :: ptask_return_tail*
S_after_return.CURRENT = S_return.CURRENT /\ S_after_return.ENV = S_return.ENV
$task_nodes(RETURN_UNWIND (KNOWN (PFLOAT 4617315517961601024)) porigin_return?) = eps
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HARRAY n_root) = 1
$heap_owners(H_return, HCELL n_source_return) = 3 /\ $heap_owners(H_return, HCELL n_leaf) = 2
$heap_owners(H_return, HCELL n_formal) = 1
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $nrpr_seek(S_after_return, 1, 1536)[.COMPLETION = NORMAL]
$nrpr_ready(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PFLOAT 4617315517961601024)
$named_origin(S_pre, (porigin_call), 0) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes = $ptascii("ReviewNotice39\\Primary\\make")
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
pfunction_producer.NAME = preqbytes /\ pfunction_producer.EARLY
$call_target(S_pre, $ptascii("make"), eps) = (pfunction_global)
pfunction_global.ORIGIN =/= pfunction_producer.ORIGIN
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.BYREF /\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_pre, pfunction_producer)
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
$ptlc($base64(text_type)) = $ptascii("array")
$named_expression($named_source(S_pre, (porigin_call), 0)) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer_call
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("float")
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "float"]))]
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE)
$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])
(PDEFUNCTION n_unit pfunction_producer.ORIGIN) <- S_pre.DECLARATIONS
$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$declaration_history_valid(S_pre)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
S_pre.FRAMES = eps /\ S_pre.CURRENT = eps
~((HCELL n_formal) <- S_pre.ALLOCATIONS) /\ ~((HARRAY n_root) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("input")) = eps
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_cv)
n_source_cv = n_source_return
S_pre.STORE[n_source_cv] = DEFINED (PINT 17)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
S_pre.STORE[n_leaf] = DEFINED (PINT 5)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source_cv) = 2 /\ $heap_owners(H_pre, HCELL n_leaf) = 1
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
""".strip().splitlines()

PRIVATE = r"""
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)
$named_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$named_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
n_private =/= n_source_cv /\ n_private =/= n_leaf /\ n_private =/= n_formal
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_private)]
S_notice.STORE[n_private] = DEFINED (PFLOAT 4617315517961601024)
n_private <- S_notice.REFCELLS /\ (HCELL n_private) <- S_notice.ALLOCATIONS
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = eps
S_notice.ARRAYS = S_pre.ARRAYS /\ S_notice.HELD = S_pre.HELD
~((HCELL n_formal) <- S_notice.ALLOCATIONS) /\ ~((HARRAY n_root) <- S_notice.ALLOCATIONS)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HCELL n_source_cv) = 2 /\ $heap_owners(H_notice, HCELL n_leaf) = 1
$heap_valid(H_notice) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $nrpr_seek(S_notice, 2, 1536)[.COMPLETION = NORMAL]
$nrpr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
$lookup(S_resume.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_resume.ENV, $ptascii("sourceAlias")) = (n_source_cv)
S_resume.STORE[n_source_cv] = DEFINED (PINT 23)
S_resume.STORE[n_leaf] = DEFINED (PINT 7)
S_resume.STORE[n_private] = DEFINED (PFLOAT 4617315517961601024)
$node_children(S_resume, HCELL n_private) = eps
S_resume.PARAMETERBACKINGS = eps /\ S_resume.PROPREFS = eps /\ S_resume.REFCOERCIONS = eps
~((HARRAY n_root) <- S_resume.ALLOCATIONS)
$error_call_valid(S_resume, perrorcall)
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_private) = 1
$heap_valid(H_resume) /\ $call_descriptors_valid(S_resume)
S_string = $nrpr_seek(S_resume, 3, 1536)[.COMPLETION = NORMAL]
$nrpr_ready(S_string, 3)
$lookup(S_string.ENV, $ptascii("r")) = (n_private)
S_string.STORE[n_private] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("peer")))
S_string.STORE[n_source_cv] = DEFINED (PINT 23) /\ S_string.STORE[n_leaf] = DEFINED (PINT 7)
$propref_at(S_string.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_string.REFCOERCIONS, n_private) = eps
$parameter_backing_at(S_string.PARAMETERBACKINGS, n_private) = eps
H_string = $heap_graph(S_string)
$heap_owners(H_string, HCELL n_private) = 1 /\ $heap_valid(H_string)
$call_descriptors_valid(S_string)
S_full = $drive(S_string, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PINT 31)
$lookup(S_full.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_full.ENV, $ptascii("sourceAlias")) = (n_source_cv)
S_full.STORE[n_source_cv] = DEFINED (PINT 23)
S_full.STORE[n_leaf] = DEFINED (PINT 7)
$node_children(S_full, HCELL n_private) = eps
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
~((HCELL n_formal) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_root) <- S_full.ALLOCATIONS)
H_full = $heap_graph(S_full)
$heap_valid(H_full) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()

CONTROLS = r"""
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.RETURNS = eps])
$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, ABSENT, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES "c3RyaW5n") metadata_return, pfunction_producer.SIGNATURE)
$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES "c3RyaW5n") metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(phpType6_producer, phpType16, NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "float"])),(PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return,NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "float"])),(PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "float"])),(PTBRANCH ([PTBUILTIN "null"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.REQUIRED = false]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.VARIADIC = true]]])
phpType16_untyped = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
$reference_notice_producer_header(phpType6_producer, phpType16_untyped, phpType18, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])
~$reference_notice_producer_header(SEQUENCE ([NArg ABSENT (NScalarInt (INTEGER 5) metadata_input) (BOOLEAN false) (BOOLEAN false) metadata_input]), phpType16, phpType18, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([NArg (NIdentifier (BYTES "aW5wdXQ=") metadata_input) expression_input (BOOLEAN false) (BOOLEAN false) metadata_input]), phpType16, phpType18, pfunction_producer.SIGNATURE)
~$reference_notice_producer_header(SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN true) metadata_input]), phpType16, phpType18, pfunction_producer.SIGNATURE)
$reference_notice_producer_header(SEQUENCE eps, phpType16, phpType18, pfunction_producer.SIGNATURE)
$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES "Ym9vbA==") metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES "dHJ1ZQ==") metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "true"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES "bWl4ZWQ=") metadata_return, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))]])
$named_reference_notice_value(PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))
~$named_reference_notice_value(PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("17")))
$reference_notice_producer_target(S_pre[.DECLARATIONS = eps], porigin_argument) = eps
~$named_reference_notice_source(S_pre[.DECLARATIONS = eps], pcalltarget, 0, (porigin_call))
~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
~$error_call_valid(S_notice, perrorcall[.RESUME = NAMED_ARGS pcalltarget eps 1 {SLOTS ([NAMED_SENT (KNOWN (PFLOAT 4617315517961601024))]), NAMED eps} (porigin_call) z_call])
S_zero_return = $drive(S_return, 0)
S_zero_return.COMPLETION = BUDGET /\ S_zero_return[.COMPLETION = NORMAL] = S_return
S_split_return = $drive($drive(S_zero_return[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1)
S_split_return = $drive(S_return, 2)
S_zero_notice = $drive(S_notice, 0)
S_zero_notice.COMPLETION = BUDGET /\ S_zero_notice[.COMPLETION = NORMAL] = S_notice
S_split_notice = $drive($drive(S_zero_notice[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1)
S_split_notice = $drive(S_notice, 2)
""".strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    row, = json.loads(CATALOGUE.read_bytes())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed'] and native['inputs_stable']
    assert native['id'] == row['id'] and source.read_bytes() == row['source'].encode()
    assert sha(source) == native['source_sha256'] == row['source_sha256']
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == sha(types.PHP)
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
    assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
    assert native['exit'] == row['native_exit'] == 0 and not native['timeout'] and not native['group_after']
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
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached = [initial] + RETURN + COMMON
    if args.front:
        derived = [
            '~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)',
            '~$named_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))',
            '~$named_reference_notice_pending(S_pre)',
            'S_fenced = $drive(S_pre, 1)',
            'S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
            'S_fenced.EVENTS = S_pre.EVENTS',
            'S_fenced.STORE = S_pre.STORE ++ [DEFINED (PFLOAT 4617315517961601024)]',
            'S_fenced.STORE[n_source_cv] = DEFINED (PINT 17) /\\ S_fenced.STORE[n_leaf] = DEFINED (PINT 5)',
        ]
    else:
        reached += PRIVATE
        reached.append('$nrpr_output(S_full.EVENTS) = $ptascii(' + json.dumps(row['native_stdout']) + ')')
        derived = CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, source, provenance, source.with_name('native.stdout'), source.with_name('native.stderr'), Path(__file__), CATALOGUE]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable,
        'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': 'scalar-dimension-return-front' if args.front else 'scalar-dimension-return-notice', 'conditions': len(reached) + len(derived),
        'reached_conditions': len(reached), 'derived_conditions': len(derived),
        'heap_bindings': len({line.split(' = ', 1)[0] for line in reached if line.startswith('H_') and ' = $heap_graph(' in line}),
        'executed_heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('scalar-dimension-return-producer', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

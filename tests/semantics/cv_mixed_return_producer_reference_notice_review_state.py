"""Ground mixed stdClass identity, private-cell retargeting and strict RECEIVE priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import singleton_cv_typed_formal_producer_reference_notice_review_state as prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_mixed_return_producer_reference_notice_review_cases.json')
PREFIX = r'''
dec $scfr_output(pevent*) : ptbytes
def $scfr_output(eps) = eps
def $scfr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $scfr_output(pevent*)
dec $scfr_ready(pstate, nat) : bool
def $scfr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice67\\Named\\make")
def $scfr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;")
def $scfr_ready(S, 2) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;H:8:0:5:2;")
def $scfr_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;H:8:0:5:2;F:29:1:17;R:19:19:77:31;")
def $scfr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:5;H:8:0:5:2;F:29:1:17;R:19:19:77:31;D:41:19:77:31;")
def $scfr_ready(S, 5) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice67\\Priority\\make")
def $scfr_ready(S, 6) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("P;C:11:2:1:1;")
def $scfr_ready(S, 7) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("P;C:11:2:1:1;D:11:31:23:1;")
def $scfr_ready(S, n_stage) = false -- otherwise
dec $scfr_seek(pstate, nat, nat) : pstate
def $scfr_seek(S, n_stage, n) = S -- if $scfr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $scfr_seek(S, n_stage, n) = $scfr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$scfr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scfr_seek(S, n_stage, n) = S -- otherwise
'''

FRONT = r'''
S_initial.COMPLETION = BUDGET
S_return = $scfr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_return, 0)
S_return.CURRENT = (pcallcontext)
$function_at($all_functions(S_return), pcallcontext.FUNCTION) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE /\ psparam.TYPE = eps
~pfunction_producer.SIGNATURE.BYREF /\ ~pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))]
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.RESULT = VARIABLE ($ptascii("saved")) z_saved
$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)
S_return.STORE[n_formal] = DEFINED (POBJECT n_old)
~(n_formal <- S_return.REFCELLS)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x_before)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("alias")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
S_return.STORE[n_x_before] = DEFINED (POBJECT n_before)
S_return.STORE[n_copy] = DEFINED (POBJECT n_old) /\ S_return.STORE[n_prefix] = DEFINED (PINT 2)
n_old =/= n_before /\ n_copy =/= n_formal
$objectprops_at(S_return.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}])
$objectprops_at(S_return.OBJECTPROPS, n_before) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 11)))}])
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, POBJECT n_old, pfunction_producer.CODE.STRICT) = TYPEVALUE (POBJECT n_old)
$typed_return_task_valid(S_return, z_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (POBJECT n_old)
S_checked.STORE = S_return.STORE /\ S_checked.OBJECTS = S_return.OBJECTS /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
S_pre = $scfr_seek(S_return, 1, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps /\ S_pre.RESULT = KNOWN (POBJECT n_old)
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
S_pre.STORE[n_x_before] = DEFINED (POBJECT n_before) /\ S_pre.STORE[n_copy] = DEFINED (POBJECT n_old)
S_pre.STORE[n_prefix] = DEFINED (PINT 2)
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\ pnamedargs.NAMED = eps
$heap_owners($heap_graph(S_pre), HOBJECT n_old) = 2
$heap_owners($heap_graph(S_pre), HOBJECT n_before) = 1
$heap_owners($heap_graph(S_pre), HCELL n_copy) = 2
$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3
$named_reference_notice_object(S_pre, POBJECT n_old)
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19 (SEQUENCE ([phpType7])) metadata_call
phpType7 = NArg ABSENT expression (BOOLEAN false) (BOOLEAN false) metadata_arg
$reference_cv(expression) = ($ptascii("x"))
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("mixed")
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression)
$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression) = 8
'''.strip().splitlines()

FULL = r'''
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\ pnamedargs_after.NAMED = eps
perrorcall.LINE = 8 /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED (POBJECT n_old) /\ n_private <- S_notice.REFCELLS
n_private =/= n_formal /\ n_private =/= n_copy /\ n_private =/= n_x_before /\ n_private =/= n_prefix
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HOBJECT n_old) = 2
$node_children(S_notice, HCELL n_private) = [HOBJECT n_old]
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_notice)) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $scfr_seek(S_notice, 2, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
$lookup(S_resume.ENV, $ptascii("x")) = (n_x_after)
n_x_after =/= n_x_before
S_resume.STORE[n_x_after] = DEFINED (POBJECT n_after)
n_after =/= n_old /\ n_after =/= n_before
S_resume.STORE[n_private] = DEFINED (POBJECT n_old) /\ S_resume.STORE[n_copy] = DEFINED (POBJECT n_old)
S_resume.STORE[n_prefix] = DEFINED (PINT 29)
$objectprops_at(S_resume.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 17)))}])
$objectprops_at(S_resume.OBJECTPROPS, n_after) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 77)))}])
~((HOBJECT n_before) <- S_resume.ALLOCATIONS) /\ ~((HCELL n_x_before) <- S_resume.ALLOCATIONS)
$heap_owners($heap_graph(S_resume), HOBJECT n_old) = 2
$heap_owners($heap_graph(S_resume), HOBJECT n_after) = 1
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
S_written = $scfr_seek(S_resume, 3, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (POBJECT n_old) /\ S_written.STORE[n_copy] = DEFINED (POBJECT n_old)
S_written.STORE[n_x_after] = DEFINED (POBJECT n_after) /\ S_written.STORE[n_prefix] = DEFINED (PINT 31)
$objectprops_at(S_written.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 19)))}])
$heap_owners($heap_graph(S_written), HOBJECT n_old) = 2
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_retired = $scfr_seek(S_written, 4, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_retired, 4)
S_retired.STORE[n_private] = DEFINED (PINT 41) /\ S_retired.STORE[n_copy] = DEFINED (POBJECT n_old)
$node_children(S_retired, HCELL n_private) = eps
$heap_owners($heap_graph(S_retired), HOBJECT n_old) = 1
S_full = $drive(S_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("r")) = eps /\ $lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("alias")) = eps
$lookup(S_full.ENV, $ptascii("copy")) = eps /\ $lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HCELL n_formal) <- S_full.ALLOCATIONS) /\ ~((HCELL n_x_after) <- S_full.ALLOCATIONS)
~((HOBJECT n_old) <- S_full.ALLOCATIONS) /\ ~((HOBJECT n_before) <- S_full.ALLOCATIONS) /\ ~((HOBJECT n_after) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()

PRIORITY = [line.replace('"array"', '"mixed"').replace('S_initial, 6,', 'S_initial, 5,')
    .replace('S_receive, 6)', 'S_receive, 5)').replace('S_receive, 7,', 'S_receive, 6,')
    .replace('S_caught, 7)', 'S_caught, 6)').replace('S_caught, 8,', 'S_caught, 7,')
    .replace('S_written, 8)', 'S_written, 7)') for line in prior.PRIORITY]


def normal(initial, case, front):
    arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
    header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
    conditions = [initial] + FRONT + [('~' if front else '') + line for line in (header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        conditions += FULL + ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        for target in ('array', 'string', 'null', 'void', 'never'):
            derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "' + target + '"]))]])')]
        derived += ['~' + header.replace('phpType18,', 'NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return,'),
            '~' + header.replace('phpType18,', 'NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return,').replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"])), (PTBRANCH ([PTBUILTIN "null"]))]])'),
            '~' + header.replace('phpType18,', 'NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES "aW50") metadata_return])) metadata_return,').replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"])), (PTBRANCH ([PTBUILTIN "int"]))]])'),
            '~' + header.replace('phpType18,', 'NName (BYTES text_return) metadata_return,'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.REQUIRED = false]]])'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.VARIADIC = true]]])'),
            '~' + header.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([NArg ABSENT (NScalarInt (INTEGER 5) metadata_arg) (BOOLEAN false) (BOOLEAN false) metadata_arg]),'),
            '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) phpType18 (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), phpType18, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]]]])',
            '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
            '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
            'S_zero = $drive(S_notice, 0)', r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice',
            '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)',
            'S_zero_return = $drive(S_return, 0)', r'S_zero_return.COMPLETION = BUDGET /\ S_zero_return[.COMPLETION = NORMAL] = S_return',
            '$drive($drive(S_zero_return[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_return, 2)']
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
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__)]
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
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/validate.py', 'tests/corpus.py')]
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
    print('cv-mixed-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

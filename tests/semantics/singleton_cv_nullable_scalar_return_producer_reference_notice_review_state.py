"""Ground ordered singleton returns, REQUEST snapshots and return-TypeError priority."""
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
CATALOGUE = Path(__file__).with_name('singleton_cv_nullable_scalar_return_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice59', 'ReviewNotice60')
for old, new in [
        ('N;M:5;H:8:5:2;F:29:13;R:23:17:5:31;D:41:17:5:31;', 'N;M:17;H:8:17:2;F:31:17:X7;R:XY:29:17:43;D:47:29:17:43;'),
        ('N;M:5;H:8:5:2;F:29:13;R:23:17:5:31;', 'N;M:17;H:8:17:2;F:31:17:X7;R:XY:29:17:43;'),
        ('N;M:5;H:8:5:2;', 'N;M:17;H:8:17:2;'), ('N;M:5;', 'N;M:17;'),
        ('P;C:11:2:1:1;D:11:31:23:1;', 'P;M:17;C:11:2:17:17;D:11:31:23:17;'),
        ('P;C:11:2:1:1;', 'P;M:17;C:11:2:17:17;')]:
    PREFIX = PREFIX.replace(old, new)
PREFIX = PREFIX.replace('def $scfr_ready(S, 6) = true\n  -- if S.TODO = [TYPE_RECEIVE porigin 0]',
    'def $scfr_ready(S, 6) = true\n  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*')
PREFIX = PREFIX.replace('def $scfr_ready(S, n_stage) = false -- otherwise', r"""
def $scfr_ready(S, 9) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice60\\Named\\take")
  -- if S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:17;H:8:17:2;F:31:17:X7;")
def $scfr_ready(S, n_stage) = false -- otherwise
""")
FRONT = r"""
S_initial.COMPLETION = BUDGET
S_return = $scfr_seek(S_initial, 1, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_return, 1)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext)
$function_at($all_functions(S_return), pcallcontext.FUNCTION) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE /\ psparam.TYPE = eps
~pfunction_producer.SIGNATURE.BYREF /\ ~pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "string"]))]
$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)
S_return.STORE[n_formal] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
~(n_formal <- S_return.REFCELLS)
$string_carrier_valid(S_return, pvalue_original)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
n_formal =/= n_x /\ n_x =/= n_copy /\ n_prefix =/= n_x
S_return.STORE[n_x] = DEFINED pvalue_original /\ S_return.STORE[n_copy] = DEFINED pvalue_original
S_return.STORE[n_prefix] = DEFINED (PINT 2)
S_return.RESULT = VARIABLE ($ptascii("saved")) z_saved
S_resolved = $resolve_at(S_return, S_return.RESULT, z_return)
S_resolved.COMPLETION = NORMAL /\ S_resolved.RESULT = KNOWN pvalue_original
$typed_return_task_valid(S_return, z_return)
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, pvalue_original, pfunction_producer.CODE.STRICT) = TYPEVALUE pvalue_original
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN pvalue_original
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
$scfr_output(S_return.EVENTS) = $ptascii("N;M:17;")
S_pre = $scfr_seek(S_return, 2, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_pre, 2)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
S_pre.RESULT = KNOWN pvalue_original
S_pre.STORE[n_x] = DEFINED pvalue_original /\ S_pre.STORE[n_copy] = DEFINED pvalue_original
S_pre.STORE[n_prefix] = DEFINED (PINT 2)
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\ pnamedargs.NAMED = eps
$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3
$string_carrier_valid(S_pre, pvalue_original)
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19 (SEQUENCE ([phpType7])) metadata_call
phpType7 = NArg ABSENT expression (BOOLEAN false) (BOOLEAN false) metadata_arg
$reference_cv(expression) = ($ptascii("x"))
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first, NIdentifier (BYTES text_last) metadata_last])) metadata_union
$ptlc($base64(text_first)) = $ptascii("null") /\ $ptlc($base64(text_last)) = $ptascii("string")
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression)
$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression) = 8
$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])
""".strip().splitlines()
FULL = r"""
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\ pnamedargs_after.NAMED = eps
perrorcall.LINE = 8 /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED pvalue_original
n_private =/= n_formal /\ n_private =/= n_x /\ n_private =/= n_copy /\ n_private =/= n_prefix
n_private <- S_notice.REFCELLS
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$string_carrier_valid(S_notice, pvalue_original)
$heap_valid($heap_graph(S_notice)) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $scfr_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_x] = DEFINED (PINT 29) /\ S_resume.STORE[n_prefix] = DEFINED (PINT 31)
S_resume.STORE[n_copy] = DEFINED pvalue_original /\ S_resume.STORE[n_private] = DEFINED pvalue_original
$string_carrier_valid(S_resume, pvalue_original)
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
S_cow = $scfr_seek(S_resume, 9, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_cow, 9)
$lookup(S_cow.ENV, $ptascii("local")) = (n_local)
$lookup(S_cow.ENV, $ptascii("value")) = (n_private)
S_cow.STORE[n_local] = DEFINED pvalue_original
S_cow.STORE[n_private] = DEFINED (PSTRING ($ptascii("X7")))
S_cow.STORE[n_copy] = DEFINED pvalue_original /\ S_cow.STORE[n_x] = DEFINED (PINT 29)
$string_carrier_valid(S_cow, pvalue_original)
$heap_valid($heap_graph(S_cow)) /\ $call_descriptors_valid(S_cow)
S_written = $scfr_seek(S_cow, 4, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PSTRING ($ptascii("XY")))
S_written.STORE[n_x] = DEFINED (PINT 29) /\ S_written.STORE[n_copy] = DEFINED pvalue_original
S_written.STORE[n_prefix] = DEFINED (PINT 43)
~((HCELL n_local) <- S_written.ALLOCATIONS)
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$string_carrier_valid(S_written, pvalue_original)
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_retired = $scfr_seek(S_written, 5, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_retired, 5)
S_retired.STORE[n_private] = DEFINED (PINT 47)
S_full = $drive(S_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("r")) = eps /\ $lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HCELL n_formal) <- S_full.ALLOCATIONS) /\ ~((HCELL n_local) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()
PRIORITY = r"""
S_initial.COMPLETION = BUDGET
S_return = $scfr_seek(S_initial, 6, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_return, 6)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext)
$function_at($all_functions(S_return), pcallcontext.FUNCTION) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE /\ psparam.TYPE = eps
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))]
$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)
S_return.STORE[n_formal] = DEFINED (PINT 17)
S_return.RESULT = VARIABLE ($ptascii("saved")) z_saved
$typed_return_task_valid(S_return, z_return)
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PINT 17, pfunction_producer.CODE.STRICT) = TYPEREJECT
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("alias")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("r")) = (n_r)
n_x <- S_return.REFCELLS /\ ~(n_formal <- S_return.REFCELLS) /\ n_formal =/= n_x
S_return.STORE[n_x] = DEFINED (PINT 17) /\ S_return.STORE[n_copy] = DEFINED (PINT 17)
S_return.STORE[n_prefix] = DEFINED (PINT 2) /\ S_return.STORE[n_r] = DEFINED (PINT 11)
$scfr_output(S_return.EVENTS) = $ptascii("P;M:17;")
$origin_node(S_return.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first, NIdentifier (BYTES text_last) metadata_last])) metadata_union
$ptlc($base64(text_first)) = $ptascii("bool") /\ $ptlc($base64(text_last)) = $ptascii("null")
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
S_rejected = $typed_return_value(S_return, z_return)
S_rejected.COMPLETION = THROWN "TypeError" ptbytes_message z_error
S_rejected.STORE = S_return.STORE /\ S_rejected.ARRAYS = S_return.ARRAYS
S_rejected.PROPREFS = S_return.PROPREFS /\ S_rejected.REFCOERCIONS = S_return.REFCOERCIONS
S_rejected.EVENTS = S_return.EVENTS
S_caught = $scfr_seek(S_return, 7, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_caught, 7)
S_caught.CURRENT = eps /\ S_caught.FRAMES = eps
S_caught.STORE[n_x] = DEFINED (PINT 17) /\ S_caught.STORE[n_copy] = DEFINED (PINT 17)
S_caught.STORE[n_prefix] = DEFINED (PINT 2) /\ S_caught.STORE[n_r] = DEFINED (PINT 11)
~((HCELL n_formal) <- S_caught.ALLOCATIONS)
$lookup(S_caught.ENV, $ptascii("e")) = (n_exception_cv)
S_caught.STORE[n_exception_cv] = DEFINED (POBJECT n_exception)
$throwable_live(S_caught, n_exception)
$heap_valid($heap_graph(S_caught)) /\ $call_descriptors_valid(S_caught)
S_written = $scfr_seek(S_caught, 8, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 8)
S_written.STORE[n_x] = DEFINED (PINT 23) /\ S_written.STORE[n_copy] = DEFINED (PINT 17)
S_written.STORE[n_prefix] = DEFINED (PINT 31) /\ S_written.STORE[n_r] = DEFINED (PINT 11)
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
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    conditions = [initial] + FRONT + [('~' if front else '') + line for line in (header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        conditions += FULL + ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        derived = ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "null"]))]])'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])'),
            'phpType17_array = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES "YXJyYXk=") metadata_first) metadata_union) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
            '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17_array]), NNullableType (NIdentifier (BYTES "aW50") metadata_first) metadata_union, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]]]][.RETURNS = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]])',
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
    print('singleton-cv-nullable-scalar-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

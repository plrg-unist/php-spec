"""Ground sole-null returns, private ARRAY COW and weak RETURN rejection."""
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
import singleton_cv_nullable_scalar_return_producer_reference_notice_review_state as return_prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_null_return_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice59', 'ReviewNotice66')
for old, new in [
        ('N;M:5;H:8:5:2;F:29:13;R:23:17:5:31;D:41:17:5:31;', 'N;M:1;H:8:1:2;F:29:1;R:23:19:17:1:31;D:41:19:17:1:31;'),
        ('N;M:5;H:8:5:2;F:29:13;R:23:17:5:31;', 'N;M:1;H:8:1:2;F:29:1;R:23:19:17:1:31;'),
        ('N;M:5;H:8:5:2;', 'N;M:1;H:8:1:2;'), ('N;M:5;', 'N;M:1;'),
        ('P;C:11:2:1:1;', 'P;M:17;C:11:2:1:1;')]:
    PREFIX = PREFIX.replace(old, new)
PREFIX = PREFIX.replace('def $scfr_ready(S, 6) = true\n  -- if S.TODO = [TYPE_RECEIVE porigin 0]',
    'def $scfr_ready(S, 6) = true\n  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*')

FRONT = r'''
S_initial.COMPLETION = BUDGET
S_receive = $scfr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_receive, 0)
S_receive.TODO = [TYPE_RECEIVE porigin 0]
$receiving_function(S_receive, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]
~pfunction_producer.SIGNATURE.BYREF /\ ~pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "null"]))]
$typed_receive_valid(S_receive, porigin, 0)
$lookup(S_receive.ENV, $ptascii("saved")) = (n_formal)
S_receive.STORE[n_formal] = DEFINED PNULL /\ ~(n_formal <- S_receive.REFCELLS)
S_receive.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("alias")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
n_x <- S_receive.REFCELLS /\ n_formal =/= n_x /\ n_x =/= n_copy
S_receive.STORE[n_x] = DEFINED PNULL /\ S_receive.STORE[n_copy] = DEFINED PNULL
S_receive.STORE[n_prefix] = DEFINED (PINT 2)
$typed_parameter_conversion(S_receive, psparam, PNULL) = TYPEVALUE PNULL
$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)
S_return = $scfr_seek(S_receive, 1, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_return, 1)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.RESULT = VARIABLE ($ptascii("saved")) z_saved
S_return.STORE[n_formal] = DEFINED PNULL
$typed_return_task_valid(S_return, z_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN PNULL
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
$scfr_output(S_return.EVENTS) = $ptascii("N;M:1;")
S_pre = $scfr_seek(S_return, 2, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_pre, 2)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps /\ S_pre.RESULT = KNOWN PNULL
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
S_pre.STORE[n_x] = DEFINED PNULL /\ S_pre.STORE[n_copy] = DEFINED PNULL
S_pre.STORE[n_prefix] = DEFINED (PINT 2)
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\ pnamedargs.NAMED = eps
$heap_owners($heap_graph(S_pre), HCELL n_x) = 2
$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19 (SEQUENCE ([phpType7])) metadata_call
phpType7 = NArg ABSENT expression (BOOLEAN false) (BOOLEAN false) metadata_arg
$reference_cv(expression) = ($ptascii("x"))
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
$ptlc($base64(text_type)) = $ptascii("array")
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("null")
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
S_notice.STORE[n_private] = DEFINED PNULL /\ n_private <- S_notice.REFCELLS
n_private =/= n_formal /\ n_private =/= n_x /\ n_private =/= n_copy /\ n_private =/= n_prefix
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$node_children(S_notice, HCELL n_private) = eps
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_notice)) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $scfr_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_x] = DEFINED (PARRAY n_current)
S_resume.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]
S_resume.STORE[n_copy] = DEFINED PNULL /\ S_resume.STORE[n_private] = DEFINED PNULL
S_resume.STORE[n_prefix] = DEFINED (PINT 29)
$heap_owners($heap_graph(S_resume), HARRAY n_current) = 1
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
S_written = $scfr_seek(S_resume, 4, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
$lookup(S_written.ENV, $ptascii("copyPrivate")) = (n_outside)
S_written.STORE[n_private] = DEFINED (PARRAY n_written)
S_written.STORE[n_outside] = DEFINED (PARRAY n_saved)
n_saved =/= n_written /\ n_saved =/= n_current /\ n_written =/= n_current
S_written.ARRAYS[n_written].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23))]
S_written.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 19))]
S_written.STORE[n_x] = DEFINED (PARRAY n_current) /\ S_written.STORE[n_copy] = DEFINED PNULL
S_written.STORE[n_prefix] = DEFINED (PINT 31)
$heap_owners($heap_graph(S_written), HARRAY n_saved) = 1
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
$lookup(S_full.ENV, $ptascii("r")) = eps /\ $lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("alias")) = eps
$lookup(S_full.ENV, $ptascii("copy")) = eps /\ $lookup(S_full.ENV, $ptascii("copyPrivate")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HCELL n_formal) <- S_full.ALLOCATIONS) /\ ~((HCELL n_outside) <- S_full.ALLOCATIONS)
~((HARRAY n_current) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_saved) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_written) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()

PRIORITY = []
for line in return_prior.PRIORITY:
    line = line.replace('PINT 17', 'pvalue_original')
    line = line.replace('pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))]',
        'pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "null"]))]')
    line = line.replace('~pfunction_producer.SIGNATURE.BYREF /\\ pfunction_producer.CODE.STRICT',
        '~pfunction_producer.SIGNATURE.BYREF /\\ ~pfunction_producer.CODE.STRICT')
    if line.startswith('phpType18 = NUnionType'):
        line = 'phpType18 = NIdentifier (BYTES text_return) metadata_return'
    if line.startswith('$ptlc($base64(text_first))'):
        line = '$ptlc($base64(text_return)) = $ptascii("null")'
    PRIORITY.append(line)
    if line == 'S_return.STORE[n_formal] = DEFINED (pvalue_original)':
        PRIORITY += ['pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))',
            '$string_carrier_valid(S_return, pvalue_original)']
    if line == 'S_written.STORE[n_x] = DEFINED (PINT 23) /\\ S_written.STORE[n_copy] = DEFINED (pvalue_original)':
        PRIORITY.append('$string_carrier_valid(S_written, pvalue_original)')


def normal(initial, case, front):
    arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
    header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
    conditions = [initial] + FRONT + [('~' if front else '') + line for line in (header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        conditions += FULL + ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        for target in ('array', 'mixed', 'void', 'never'):
            derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "' + target + '"]))]])')]
        derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "null"]))]])'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])'),
            '~' + header.replace('phpType18,', 'NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return,'),
            '~' + header.replace('phpType18,', 'NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return])) metadata_return,'),
            '~' + header.replace('phpType18,', 'NName (BYTES text_return) metadata_return,'),
            '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
            '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
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
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(return_prior.__file__)]
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
    print('cv-null-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

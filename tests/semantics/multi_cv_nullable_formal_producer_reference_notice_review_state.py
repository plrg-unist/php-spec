"""Check nullable scalar snapshots, private array COW and strict NULL reception."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
import multi_cv_scalar_formal_producer_reference_notice_review_state as prior
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_nullable_formal_producer_reference_notice_review_cases.json')
array = prior.array
PREFIX = prior.PREFIX.replace('ReviewNotice57', 'ReviewNotice58')
PREFIX = PREFIX.replace('P;C:11:2:5:5:17;D:11:31:29:5:23;', 'P;C:11:2:1:1:17;D:11:31:29:1:23;').replace('P;C:11:2:5:5:17;', 'P;C:11:2:1:1:17;')
PREFIX = PREFIX.replace('N;M:1:1;H:8:body:2;F:31:17;R:X7:29:17:43;D:47:29:17:43;', 'N;M:1:1;H:8:body:2;F:31:1:1;R:1:29:17:43:1;D:47:29:17:43:1;').replace('N;M:1:1;H:8:body:2;F:31:17;R:X7:29:17:43;', 'N;M:1:1;H:8:body:2;F:31:1:1;R:1:29:17:43:1;')
PREFIX = PREFIX.replace('def $mcaf_ready(S, n_stage) = false -- otherwise', r"""
def $mcaf_ready(S, 3) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice58\\Priority\\make")
def $mcaf_ready(S, n_stage) = false -- otherwise
""")
PREFIX = PREFIX.replace('def $mcsfr_ready(S, n_stage) = false -- otherwise', r"""
def $mcsfr_ready(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.RESULT = KNOWN PNULL
  -- if pcallcontext.NAME = $ptascii("ReviewNotice58\\Named\\take")
  -- if $mcvr_output(S.EVENTS) = $ptascii("N;M:1:1;H:8:body:2;F:31:1:1;")
def $mcsfr_ready(S, n_stage) = false -- otherwise
""")
PRIORITY = r"""
S_initial.COMPLETION = BUDGET
S_first_priority = $mcaf_seek(S_initial, 3, 5000)[.COMPLETION = NORMAL]
$mcaf_ready(S_first_priority, 3)
S_first_priority.TODO = [TYPE_RECEIVE porigin 0]
$receiving_function(S_first_priority, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "null"]))]
psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]
psparam_first.REQUIRED /\ psparam_last.REQUIRED /\ ~psparam_first.VARIADIC /\ ~psparam_last.VARIADIC
psparam_first.DEFAULT = PSNONE /\ psparam_last.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$typed_caller_strict(S_first_priority)
$typed_receive_valid(S_first_priority, porigin, 0)
$lookup(S_first_priority.ENV, $ptascii("saved")) = (n_formal)
$lookup(S_first_priority.ENV, $ptascii("changed")) = (n_bad)
n_formal =/= n_bad /\ ~(n_formal <- S_first_priority.REFCELLS) /\ n_bad <- S_first_priority.REFCELLS
S_first_priority.STORE[n_formal] = DEFINED PNULL
S_first_priority.STORE[n_bad] = DEFINED (PINT 17)
$typed_parameter_conversion(S_first_priority, psparam_first, PNULL) = TYPEVALUE PNULL
S_received_first_budget = $drive_steps(S_first_priority, 1)
S_received_first_budget.COMPLETION = BUDGET
S_receive = $mcaf_seek(S_received_first_budget[.COMPLETION = NORMAL], 0, 5000)[.COMPLETION = NORMAL]
$mcaf_ready(S_receive, 0)
S_receive.TODO = [TYPE_RECEIVE porigin 1]
$typed_receive_valid(S_receive, porigin, 1)
$typed_caller_strict(S_receive)
S_receive.STORE[n_formal] = DEFINED PNULL /\ S_receive.STORE[n_bad] = DEFINED (PINT 17)
S_receive.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("bad")) = (n_bad)
$lookup(psymboltable_caller.ENV, $ptascii("badAlias")) = (n_bad)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("r")) = (n_r)
S_receive.STORE[n_x] = DEFINED PNULL /\ S_receive.STORE[n_copy] = DEFINED PNULL
S_receive.STORE[n_prefix] = DEFINED (PINT 2) /\ S_receive.STORE[n_r] = DEFINED (PINT 11)
~$typed_parameter_source(S_receive, psparam_last)
$propref_at(S_receive.PROPREFS, n_bad) = eps /\ $reference_coercion_at(S_receive.REFCOERCIONS, n_bad) = eps
$typed_parameter_conversion(S_receive, psparam_last, PINT 17) = TYPEREJECT
$mcvr_output(S_receive.EVENTS) = $ptascii("P;")
$origin_node(S_receive.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) (NIdentifier (BYTES text_return) metadata_return) phpType23 metadata_function)
$ptlc($base64(text_return)) = $ptascii("array")
$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)
S_rejected = $typed_parameter_value(S_receive, pfunction_producer, 1, PINT 17)
S_rejected.COMPLETION = THROWN "TypeError" ptbytes_message z_error
S_rejected.STORE = S_receive.STORE /\ S_rejected.ARRAYS = S_receive.ARRAYS
S_rejected.PROPREFS = S_receive.PROPREFS /\ S_rejected.REFCOERCIONS = S_receive.REFCOERCIONS
S_rejected.EVENTS = S_receive.EVENTS
S_caught = $mcaf_seek(S_receive, 1, 10000)[.COMPLETION = NORMAL]
$mcaf_ready(S_caught, 1)
S_caught.CURRENT = eps /\ S_caught.FRAMES = eps
S_caught.STORE[n_bad] = DEFINED (PINT 17) /\ S_caught.STORE[n_prefix] = DEFINED (PINT 2) /\ S_caught.STORE[n_r] = DEFINED (PINT 11)
~((HCELL n_formal) <- S_caught.ALLOCATIONS)
$lookup(S_caught.ENV, $ptascii("e")) = (n_exception_cv)
S_caught.STORE[n_exception_cv] = DEFINED (POBJECT n_exception)
$throwable_live(S_caught, n_exception)
$heap_valid($heap_graph(S_caught)) /\ $call_descriptors_valid(S_caught)
S_written = $mcaf_seek(S_caught, 2, 5000)[.COMPLETION = NORMAL]
$mcaf_ready(S_written, 2)
S_written.STORE[n_bad] = DEFINED (PINT 23) /\ S_written.STORE[n_prefix] = DEFINED (PINT 31) /\ S_written.STORE[n_r] = DEFINED (PINT 11)
S_written.STORE[n_x] = DEFINED (PINT 29) /\ S_written.STORE[n_copy] = DEFINED PNULL
$lookup(S_written.ENV, $ptascii("e")) = eps
~((HCELL n_exception_cv) <- S_written.ALLOCATIONS) /\ ~((HOBJECT n_exception) <- S_written.ALLOCATIONS)
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_full = $drive(S_written, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("bad")) = eps /\ $lookup(S_full.ENV, $ptascii("badAlias")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps /\ $lookup(S_full.ENV, $ptascii("r")) = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()
PARAMETERS = r"""
phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES text_parameter_first) metadata_parameter_first_type) metadata_parameter_first_nullable) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_parameter_first
phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES text_parameter_last) metadata_parameter_last_type) metadata_parameter_last_nullable) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_parameter_last
$ptlc($base64(text_parameter_first)) = $ptascii("string") /\ $ptlc($base64(text_parameter_last)) = $ptascii("array")
""".strip().splitlines()
COW = r"""
S_copy = $mcsfr_seek(S_notice, 5, 10000)[.COMPLETION = NORMAL]
$mcsfr_ready(S_copy, 5)
$lookup(S_copy.ENV, $ptascii("local")) = (n_local)
$lookup(S_copy.ENV, $ptascii("value")) = (n_private)
S_copy.STORE[n_local] = DEFINED (PARRAY n_return)
S_copy.STORE[n_private] = DEFINED (PARRAY n_cow)
n_cow =/= n_return /\ ~(n_local <- S_copy.REFCELLS)
S_copy.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL true))]
S_copy.ARRAYS[n_cow].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL false))]
$heap_owners($heap_graph(S_copy), HARRAY n_return) = 1 /\ $heap_owners($heap_graph(S_copy), HARRAY n_cow) = 1
S_copy.STORE[n_x] = DEFINED (PINT 29) /\ S_copy.STORE[n_prefix] = DEFINED (PINT 31)
$heap_valid($heap_graph(S_copy)) /\ $call_descriptors_valid(S_copy)
S_written = $mcsfr_seek(S_copy, 3, 10000)[.COMPLETION = NORMAL]
$mcsfr_ready(S_written, 3)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_private] = DEFINED (PARRAY n_written)
S_written.ARRAYS[n_written].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL true))]
~((HCELL n_local) <- S_written.ALLOCATIONS) /\ ~((HARRAY n_return) <- S_written.ALLOCATIONS)
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
~((HARRAY n_return) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_cow) <- S_full.ALLOCATIONS) /\ ~((HARRAY n_written) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()


def normal(initial, case, front):
    conditions, derived = prior.normal(initial, case, front)
    changes = {
        'psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]': 'psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))] /\\ psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]',
        '$typed_parameter_conversion(S_first, psparam_first, pvalue_original) = TYPEVALUE pvalue_original': '$typed_parameter_conversion(S_first, psparam_first, pvalue_original) = TYPEBOOL pvalue_original',
        'S_last.STORE[n_formal] = DEFINED pvalue_original /\\ S_last.STORE[n_x] = DEFINED pvalue_original': 'S_last.STORE[n_formal] = DEFINED (PBOOL true) /\\ S_last.STORE[n_x] = DEFINED pvalue_original',
        'S_received.STORE[n_formal] = DEFINED pvalue_original': 'S_received.STORE[n_formal] = DEFINED (PBOOL true)',
        'S_return.STORE[n_formal] = DEFINED pvalue_original': 'S_return.STORE[n_formal] = DEFINED (PBOOL true)',
        'S_return.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_original)]': 'S_return.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL true))]',
        'S_pre.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_original)]': 'S_pre.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL true))]',
        '$ptlc($base64(text_first_type)) = $ptascii("string") /\\ $ptlc($base64(text_last_type)) = $ptascii("int")': '$ptlc($base64(text_first_type)) = $ptascii("bool") /\\ $ptlc($base64(text_last_type)) = $ptascii("int")',
    }
    conditions = [changes.get(line, line) for line in conditions]
    for which in ('first', 'last'):
        old = '(NIdentifier (BYTES text_' + which + '_type) metadata_' + which + '_type)'
        new = '(NNullableType ' + old + ' metadata_' + which + '_nullable)'
        conditions = [line.replace(old, new) if line.startswith('phpType17_' + which + ' = NParam') else line for line in conditions]
    if not front:
        at = conditions.index('S_written = $mcsfr_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]')
        conditions[at:] = COW + ['$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        derived += [
            'phpType17_union = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_first_type) metadata_first_type, NIdentifier (BYTES "bnVsbA==") metadata_first_type])) metadata_first_nullable) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter',
            '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_union, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])',
            '~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "bool"]))]], psparam_last]])']
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
    print('multi-cv-nullable-formal-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

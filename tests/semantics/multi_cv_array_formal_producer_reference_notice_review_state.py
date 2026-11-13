"""Check duplicate ARRAY formals, private COW and second-parameter TypeError priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
import multi_cv_array_return_producer_reference_notice_review_state as array
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_array_formal_producer_reference_notice_review_cases.json')
PREFIX = array.PREFIX.replace('ReviewNotice50', 'ReviewNotice56') + r"""
dec $mcaf_ready(pstate, nat) : bool
def $mcaf_ready(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice56\\Priority\\make")
  -- if S.TODO = [TYPE_RECEIVE porigin 1]
def $mcaf_ready(S, 1) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("P;C:11:2:5:5:17;")
def $mcaf_ready(S, 2) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcvr_output(S.EVENTS) = $ptascii("P;C:11:2:5:5:17;D:11:31:29:5:23;")
def $mcaf_ready(S, n_stage) = false -- otherwise
dec $mcaf_seek(pstate, nat, nat) : pstate
def $mcaf_seek(S, n_stage, n) = S -- if $mcaf_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcaf_seek(S, n_stage, n) = $mcaf_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcaf_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcaf_seek(S, n_stage, n) = S -- otherwise
"""
PARAMETERS = r"""
phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parameter_first) metadata_parameter_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_parameter_first
phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parameter_last) metadata_parameter_last_type) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_parameter_last
$ptlc($base64(text_parameter_first)) = $ptascii("array") /\ $ptlc($base64(text_parameter_last)) = $ptascii("array")
psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\ psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]
psparam_first.REQUIRED /\ psparam_last.REQUIRED /\ ~psparam_first.VARIADIC /\ ~psparam_last.VARIADIC
psparam_first.DEFAULT = PSNONE /\ psparam_last.DEFAULT = PSNONE
""".strip().splitlines()
PRIORITY = r"""
S_initial.COMPLETION = BUDGET
S_receive = $mcaf_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$mcaf_ready(S_receive, 0)
S_receive.TODO = [TYPE_RECEIVE porigin 1]
S_receive.CURRENT = (pcallcontext)
pcallcontext.ARGC = 2
$receiving_function(S_receive, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
~pfunction_producer.SIGNATURE.BYREF
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$origin_node(S_receive.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) (NIdentifier (BYTES text_return) metadata_return) phpType23 metadata_function)
$ptlc($base64(text_return)) = $ptascii("array")
$lookup(S_receive.ENV, $ptascii("saved")) = (n_formal)
$lookup(S_receive.ENV, $ptascii("changed")) = (n_bad)
n_formal =/= n_bad /\ ~(n_formal <- S_receive.REFCELLS)
n_bad <- S_receive.REFCELLS
S_receive.STORE[n_formal] = DEFINED (PARRAY n_old)
S_receive.STORE[n_bad] = DEFINED (PINT 17)
S_receive.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
S_receive.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("bad")) = (n_bad)
$lookup(psymboltable_caller.ENV, $ptascii("badAlias")) = (n_bad)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("r")) = (n_r)
S_receive.STORE[n_x] = DEFINED (PARRAY n_old)
S_receive.STORE[n_copy] = DEFINED (PARRAY n_old)
S_receive.STORE[n_prefix] = DEFINED (PINT 2)
S_receive.STORE[n_r] = DEFINED (PINT 11)
~$typed_parameter_source(S_receive, psparam_last)
$propref_at(S_receive.PROPREFS, n_bad) = eps
$reference_coercion_at(S_receive.REFCOERCIONS, n_bad) = eps
$typed_parameter_conversion(S_receive, psparam_first, PARRAY n_old) = TYPEVALUE (PARRAY n_old)
$typed_parameter_conversion(S_receive, psparam_last, PINT 17) = TYPEREJECT
$mcvr_output(S_receive.EVENTS) = $ptascii("P;")
$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)
S_rejected = $typed_parameter_value(S_receive, pfunction_producer, 1, PINT 17)
S_rejected.COMPLETION = THROWN "TypeError" ptbytes_message z_error
S_rejected.STORE = S_receive.STORE /\ S_rejected.ARRAYS = S_receive.ARRAYS
S_rejected.PROPREFS = S_receive.PROPREFS /\ S_rejected.REFCOERCIONS = S_receive.REFCOERCIONS
S_rejected.EVENTS = S_receive.EVENTS
S_caught = $mcaf_seek(S_receive, 1, 10000)[.COMPLETION = NORMAL]
$mcaf_ready(S_caught, 1)
S_caught.CURRENT = eps /\ S_caught.FRAMES = eps
S_caught.STORE[n_bad] = DEFINED (PINT 17)
S_caught.STORE[n_prefix] = DEFINED (PINT 2)
S_caught.STORE[n_r] = DEFINED (PINT 11)
~((HCELL n_formal) <- S_caught.ALLOCATIONS)
$lookup(S_caught.ENV, $ptascii("e")) = (n_exception_cv)
S_caught.STORE[n_exception_cv] = DEFINED (POBJECT n_exception)
$throwable_live(S_caught, n_exception)
$heap_valid($heap_graph(S_caught)) /\ $call_descriptors_valid(S_caught)
S_written = $mcaf_seek(S_caught, 2, 5000)[.COMPLETION = NORMAL]
$mcaf_ready(S_written, 2)
S_written.STORE[n_bad] = DEFINED (PINT 23)
S_written.STORE[n_prefix] = DEFINED (PINT 31)
S_written.STORE[n_r] = DEFINED (PINT 11)
S_written.STORE[n_x] = DEFINED (PARRAY n_current)
n_current =/= n_old
S_written.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 29))]
S_written.STORE[n_copy] = DEFINED (PARRAY n_old)
S_written.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]
$lookup(S_written.ENV, $ptascii("e")) = eps
~((HCELL n_exception_cv) <- S_written.ALLOCATIONS) /\ ~((HOBJECT n_exception) <- S_written.ALLOCATIONS)
$heap_owners($heap_graph(S_written), HARRAY n_old) = 2
$heap_count(HARRAY n_old, $pools_nodes(S_written.POOLS)) = 1
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_full = $drive(S_written, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("copy")) = eps
$lookup(S_full.ENV, $ptascii("bad")) = eps /\ $lookup(S_full.ENV, $ptascii("badAlias")) = eps
$lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
$lookup(S_full.ENV, $ptascii("r")) = eps
(HARRAY n_old) <- S_full.ALLOCATIONS /\ ~((HARRAY n_current) <- S_full.ALLOCATIONS)
$heap_owners($heap_graph(S_full), HARRAY n_old) = 1 /\ $heap_count(HARRAY n_old, $pools_nodes(S_full.POOLS)) = 1
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
""".strip().splitlines()


def normal(initial, case, front):
    replacements = {
        '$mcvr_seek(S_initial, 1500)': '$mcvr_seek(S_after_return, 1500)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*': 'S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*',
        '$call_argument_origin(S_pre, (porigin_call), 0)': '$named_origin(S_pre, (porigin_call), 1)',
        '$call_argument_expression(S_pre, (porigin_call), 0)': '$named_expression($named_source(S_pre, (porigin_call), 1))',
        '"J;M:5:13;"': '"N;M:5:13;"',
        'pfunction_producer.SIGNATURE.RETURNS = eps': 'pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]',
        '])) ABSENT phpType23 metadata_function)': '])) (NIdentifier (BYTES text_type) metadata_type) phpType23 metadata_function)',
    }
    common = [line for line in array.prior.COMMON[1:] if line != 'psparam_first.TYPE = eps /\\ psparam_last.TYPE = eps']
    for old, new in replacements.items():
        common = [line.replace(old, new) for line in common]
    conditions = [initial] + array.RETURN + common + PARAMETERS
    conditions += [
        '$ptlc($base64(text_type)) = $ptascii("array")', 'n_saved = n_old /\\ n_source = n_source_return',
        '~((HCELL n_formal) <- S_pre.ALLOCATIONS)',
        '$lookup(S_pre.ENV, $ptascii("saved")) = eps /\\ $lookup(S_pre.ENV, $ptascii("changed")) = eps',
        '$lookup(S_pre.ENV, $ptascii("prefix")) = (n_prefix)', '$lookup(S_pre.ENV, $ptascii("prefixAlias")) = (n_prefix)',
        'S_pre.STORE[n_prefix] = DEFINED (PINT 2)',
        'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\\ pnamedargs.NAMED = eps',
        '$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3',
        '$propref_at(S_pre.PROPREFS, n_source) = eps', '$reference_coercion_at(S_pre.REFCOERCIONS, n_source) = eps',
        '$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = ' + str(case['notice_line']),
    ]
    arguments = '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps])'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), NIdentifier (BYTES text_type) metadata_type, pfunction_producer.SIGNATURE)'
    conditions += [('~' if front else '') + x for x in (arguments, header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        full = [line.replace('$positional_reference_notice_pending(S_pre)', '$named_reference_notice_pending(S_pre)')
            .replace('perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call', 'perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call') for line in array.prior.FULL[1:]]
        at = full.index('S_full = $drive(S_notice, 10000)')
        full[at:at + 1] = array.WRITTEN + ['S_full = $drive(S_scalar, 10000)']
        conditions += full + [
            'pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\\ pnamedargs_after.NAMED = eps',
            'perrorcall.LINE = ' + str(case['notice_line']),
            '$lookup(S_full.ENV, $ptascii("prefix")) = eps /\\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps',
            '$mcvr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        derived = [line.replace('psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]]', 'psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]') for line in array.CONTROLS]
        derived += ['~' + arguments.replace('pfunction_producer.SIGNATURE[.RETURNS = eps]', 'pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = eps], psparam_last]]'),
            '~' + arguments.replace('pfunction_producer.SIGNATURE[.RETURNS = eps]', 'pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first, psparam_last[.TYPE = eps]]]'),
            '~' + arguments.replace('pfunction_producer.SIGNATURE[.RETURNS = eps]', 'pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first, psparam_last[.BYREF = false]]]'),
            '~' + arguments.replace('pfunction_producer.SIGNATURE[.RETURNS = eps]', 'pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first[.REQUIRED = false], psparam_last]]'),
            '~' + arguments.replace('pfunction_producer.SIGNATURE[.RETURNS = eps]', 'pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam_first, psparam_last[.VARIADIC = true]]]')]
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
    paths = [Path(__file__), CATALOGUE, provenance, Path(array.__file__), Path(array.prior.__file__)]
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
    print('multi-cv-array-formal-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

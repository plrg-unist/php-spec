"""Ground strict mixed reception, NULL aliases and separate private Notice cells."""
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
CATALOGUE = Path(__file__).with_name('cv_mixed_formal_producer_reference_notice_review_cases.json')
PREFIX = r'''
dec $scfr_output(pevent*) : ptbytes
def $scfr_output(eps) = eps
def $scfr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $scfr_output(pevent*)
dec $scfr_ready(pstate, nat) : bool
def $scfr_ready(S, 0) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("ReviewNotice68\\Strict\\make"), $ptascii("ReviewNotice68\\Null\\make")]
def $scfr_ready(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("ReviewNotice68\\Strict\\make"), $ptascii("ReviewNotice68\\Null\\make")]
def $scfr_ready(S, 2) = true
  -- if S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) <- [$ptascii("S;M:1;"), $ptascii("N;M:1;")]
def $scfr_ready(S, 3) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) <- [$ptascii("S;M:1;H:8:1:2;"), $ptascii("N;M:1;H:8:13:2;")]
def $scfr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) <- [$ptascii("S;M:1;H:8:1:2;F:29:1;R:23:19:23:1:31;"), $ptascii("N;M:1;H:8:13:2;F:29:1:17;R:19:19:23:1:31;")]
def $scfr_ready(S, 5) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) <- [$ptascii("S;M:1;H:8:1:2;F:29:1;R:23:19:23:1:31;D:41:19:23:1:31;"), $ptascii("N;M:1;H:8:13:2;F:29:1:17;R:19:19:23:1:31;D:41:19:23:1:31;")]
def $scfr_ready(S, n_stage) = false -- otherwise
dec $scfr_seek(pstate, nat, nat) : pstate
def $scfr_seek(S, n_stage, n) = S -- if $scfr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $scfr_seek(S, n_stage, n) = $scfr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$scfr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scfr_seek(S, n_stage, n) = S -- otherwise
'''

RECEIVE = r'''
S_initial.COMPLETION = BUDGET
S_receive = $scfr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_receive, 0)
S_receive.TODO = [TYPE_RECEIVE porigin 0]
$receiving_function(S_receive, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.BYREF = __BYREF__ /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
psparam.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.CODE.STRICT = __STRICT__
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))]
__CALLER_STRICT__$typed_caller_strict(S_receive)
$typed_receive_valid(S_receive, porigin, 0)
$lookup(S_receive.ENV, $ptascii("saved")) = (n_formal)
S_receive.STORE[n_formal] = DEFINED pvalue_input
__INPUT__
S_receive.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("alias")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
n_x <- S_receive.REFCELLS /\ n_copy =/= n_x
S_receive.STORE[n_x] = DEFINED pvalue_input /\ S_receive.STORE[n_copy] = DEFINED pvalue_input
S_receive.STORE[n_prefix] = DEFINED (PINT 2)
__FORMAL_IDENTITY__
~$typed_parameter_source(S_receive, psparam)
$typed_parameter_conversion(S_receive, psparam, pvalue_input) = TYPEVALUE pvalue_input
$parameter_backing_at(S_receive.PARAMETERBACKINGS, n_formal) = eps
$propref_at(S_receive.PROPREFS, n_formal) = eps /\ $reference_coercion_at(S_receive.REFCOERCIONS, n_formal) = eps
$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)
S_received = $drive(S_receive, 1)[.COMPLETION = NORMAL]
S_received.STORE = S_receive.STORE /\ S_received.ARRAYS = S_receive.ARRAYS
S_received.PROPREFS = S_receive.PROPREFS /\ S_received.REFCOERCIONS = S_receive.REFCOERCIONS
'''.strip().splitlines()

RETURN = r'''
S_return = $scfr_seek(S_received, 1, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_return, 1)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.STORE[n_formal] = DEFINED pvalue_return
__RETURN_VALUE__
$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN pvalue_return
S_return.STORE[n_x] = DEFINED pvalue_return /\ S_return.STORE[n_copy] = DEFINED pvalue_input
$typed_return_task_valid(S_return, z_return)
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, pvalue_return, pfunction_producer.CODE.STRICT) = TYPEVALUE pvalue_return
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN pvalue_return
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
S_pre = $scfr_seek(S_return, 2, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_pre, 2)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps /\ S_pre.RESULT = KNOWN pvalue_return
S_pre.STORE[n_x] = DEFINED pvalue_return /\ S_pre.STORE[n_copy] = DEFINED pvalue_input
S_pre.STORE[n_prefix] = DEFINED (PINT 2)
__FORMAL_RETIREMENT__
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix)] /\ pnamedargs.NAMED = eps
$heap_owners($heap_graph(S_pre), HCELL n_x) = 2
$heap_owners($heap_graph(S_pre), HCELL n_prefix) = 3
$parameter_backing_at(S_pre.PARAMETERBACKINGS, n_x) = eps
$propref_at(S_pre.PROPREFS, n_x) = eps /\ $reference_coercion_at(S_pre.REFCOERCIONS, n_x) = eps
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
$named_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19 (SEQUENCE ([phpType7])) metadata_call
phpType7 = NArg ABSENT expression (BOOLEAN false) (BOOLEAN false) metadata_arg
$reference_cv(expression) = ($ptascii("x"))
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal) metadata_type) (BOOLEAN __BYREF__) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
$ptlc($base64(text_formal)) = $ptascii("mixed")
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("mixed")
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression)
$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression) = 8
'''.strip().splitlines()

NOTICE = r'''
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\ pnamedargs_after.NAMED = eps
perrorcall.LINE = 8 /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED pvalue_return /\ n_private <- S_notice.REFCELLS
n_private =/= n_x /\ n_private =/= n_formal /\ n_private =/= n_copy /\ n_private =/= n_prefix
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_notice)) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $scfr_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED pvalue_return /\ S_resume.STORE[n_copy] = DEFINED pvalue_input
S_resume.STORE[n_prefix] = DEFINED (PINT 29)
__HANDLER_VALUE__
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
S_written = $scfr_seek(S_resume, 4, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
S_written.STORE[n_x] = DEFINED (PINT 23) /\ S_written.STORE[n_copy] = DEFINED pvalue_input
S_written.STORE[n_prefix] = DEFINED (PINT 31)
__WRITTEN__
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_retired = $scfr_seek(S_written, 5, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_retired, 5)
S_retired.STORE[n_private] = DEFINED (PINT 41)
__RETIRED__
S_full = $drive(S_retired, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$lookup(S_full.ENV, $ptascii("r")) = eps /\ $lookup(S_full.ENV, $ptascii("x")) = eps /\ $lookup(S_full.ENV, $ptascii("alias")) = eps
$lookup(S_full.ENV, $ptascii("copy")) = eps /\ $lookup(S_full.ENV, $ptascii("prefix")) = eps /\ $lookup(S_full.ENV, $ptascii("prefixAlias")) = eps
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HCELL n_formal) <- S_full.ALLOCATIONS) /\ ~((HCELL n_x) <- S_full.ALLOCATIONS)
__FINAL__
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()


def normal(initial, case, index, front):
    values = dict(__BYREF__='true' if index else 'false', __STRICT__='false' if index else 'true', __CALLER_STRICT__='~' if index else '',
        __INPUT__='pvalue_input = PNULL' if index else 'pvalue_input = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))\n$string_carrier_valid(S_receive, pvalue_input)',
        __FORMAL_IDENTITY__='n_formal = n_x' if index else 'n_formal =/= n_x /\\ ~(n_formal <- S_receive.REFCELLS)',
        __RETURN_VALUE__='pvalue_return = POBJECT n_old\n$objectprops_at(S_return.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 13)))}])' if index else 'pvalue_return = pvalue_input\n$string_carrier_valid(S_return, pvalue_return)',
        __FORMAL_RETIREMENT__='(HCELL n_formal) <- S_pre.ALLOCATIONS /\\ n_formal <- S_pre.REFCELLS' if index else '~((HCELL n_formal) <- S_pre.ALLOCATIONS)')
    if index:
        values.update(__HANDLER_VALUE__='S_resume.STORE[n_x] = DEFINED pvalue_return\n$objectprops_at(S_resume.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 17)))}])\n$heap_owners($heap_graph(S_resume), HOBJECT n_old) = 2',
            __WRITTEN__='$lookup(S_written.ENV, $ptascii("snapshot")) = (n_snapshot)\nS_written.STORE[n_private] = DEFINED pvalue_return /\\ S_written.STORE[n_snapshot] = DEFINED pvalue_return\n$objectprops_at(S_written.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 19)))}])\n$heap_owners($heap_graph(S_written), HOBJECT n_old) = 2',
            __RETIRED__='$node_children(S_retired, HCELL n_private) = eps\n$heap_owners($heap_graph(S_retired), HOBJECT n_old) = 1',
            __FINAL__='$lookup(S_full.ENV, $ptascii("snapshot")) = eps\n~((HCELL n_snapshot) <- S_full.ALLOCATIONS) /\\ ~((HOBJECT n_old) <- S_full.ALLOCATIONS)')
    else:
        values.update(__HANDLER_VALUE__='S_resume.STORE[n_x] = DEFINED (PINT 23)\n$string_carrier_valid(S_resume, pvalue_return)',
            __WRITTEN__='$lookup(S_written.ENV, $ptascii("copyPrivate")) = (n_snapshot)\nS_written.STORE[n_private] = DEFINED (PARRAY n_written)\nS_written.STORE[n_snapshot] = DEFINED (PARRAY n_saved)\nn_written =/= n_saved\nS_written.ARRAYS[n_written].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23))]\nS_written.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 19))]\n$heap_owners($heap_graph(S_written), HARRAY n_written) = 1\n$heap_owners($heap_graph(S_written), HARRAY n_saved) = 1\n$string_carrier_valid(S_written, pvalue_input)',
            __RETIRED__='~((HARRAY n_written) <- S_retired.ALLOCATIONS)',
            __FINAL__='$lookup(S_full.ENV, $ptascii("copyPrivate")) = eps\n~((HCELL n_snapshot) <- S_full.ALLOCATIONS) /\\ ~((HARRAY n_saved) <- S_full.ALLOCATIONS)')
    def filled(lines):
        text = '\n'.join(lines)
        for key, value in values.items():
            text = text.replace(key, value)
        return text.splitlines()
    arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
    proof = '$reference_notice_producer_arguments(' + arguments + 'pfunction_producer.SIGNATURE[.RETURNS = eps])'
    header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
    conditions = [initial] + filled(RECEIVE + RETURN) + [('~' if front else '') + line for line in (proof, header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        conditions += filled(NOTICE) + ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        for target in ('array', 'int', 'string', 'null'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "' + target + '"]))]]]]')]
        for update in ('.BYREF = ' + ('false' if index else 'true'), '.VARIADIC = true', '.REQUIRED = false'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]]')]
        for raw, normalized in [
                ('NNullableType (NIdentifier (BYTES text_formal) metadata_type) metadata_type', '[(PTBRANCH ([PTBUILTIN "mixed"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
                ('NUnionType (SEQUENCE ([NIdentifier (BYTES text_formal) metadata_type, NIdentifier (BYTES "aW50") metadata_type])) metadata_type', '[(PTBRANCH ([PTBUILTIN "mixed"])), (PTBRANCH ([PTBUILTIN "int"]))]')]:
            derived += ['~$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN ' + values['__BYREF__'] + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])']
        derived += ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
        for name in ('receive', 'return', 'notice'):
            cap = 'S_' + name
            derived += ['S_zero_' + name + ' = $drive(' + cap + ', 0)', 'S_zero_' + name + '.COMPLETION = BUDGET /\\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + cap,
                '$drive($drive(S_zero_' + name + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + cap + ', 2)']
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
            conditions, current_derived = normal(initial, case, index, args.front)
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
    print('cv-mixed-formal-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

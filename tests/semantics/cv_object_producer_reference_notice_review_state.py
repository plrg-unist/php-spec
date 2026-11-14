"""Ground object reception, ordinary BYREF rebinding and private Notice ownership."""
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
CATALOGUE = Path(__file__).with_name('cv_object_producer_reference_notice_review_cases.json')
PREFIX = r'''
dec $scfr_output(pevent*) : ptbytes
def $scfr_output(eps) = eps
def $scfr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $scfr_output(pevent*)
dec $scfr_ready(pstate, nat) : bool
def $scfr_ready(S, 0) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("ReviewNotice76\\ObjectNamed\\make"), $ptascii("ReviewNotice76\\NullNamed\\make")]
def $scfr_ready(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("ReviewNotice76\\ObjectNamed\\make"), $ptascii("ReviewNotice76\\NullNamed\\make")]
def $scfr_ready(S, 2) = true
  -- if S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:1;")
def $scfr_ready(S, 3) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $scfr_output(S.EVENTS) = $ptascii("N;M:1;H:8:1:2;")
def $scfr_ready(S, 4) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $scfr_output(S.EVENTS) <- [$ptascii("N;M:1;H:8:1:2;F:29:13;R:23:23:17:1:31;"), $ptascii("N;M:1;H:8:1:2;F:29:1;R:23:19:17:1:31;")]
def $scfr_ready(S, n_stage) = false -- otherwise
dec $scfr_seek(pstate, nat, nat) : pstate
def $scfr_seek(S, n_stage, n) = S -- if $scfr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $scfr_seek(S, n_stage, n) = $scfr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$scfr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scfr_seek(S, n_stage, n) = S -- otherwise
'''


def branches(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + kind + '"]))' for kind in members) + ']'


def raw(members):
    atoms = ['NIdentifier (BYTES "' + base64.b64encode(kind.encode()).decode() + '") metadata_formal' for kind in members]
    return atoms[0] if len(atoms) == 1 else 'NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_formal'


def normal(initial, case, index, front):
    object_case = index == 0
    input_value = 'POBJECT n_old' if object_case else 'PNULL'
    formal_type = branches(['object'] if object_case else ['object', 'null'])
    return_type = branches(['object', 'null'])
    byref, strict = ('true', 'false') if object_case else ('false', 'true')
    formal_raw = 'NIdentifier (BYTES text_formal) metadata_formal'
    if not object_case:
        formal_raw = 'NNullableType (' + formal_raw + ') metadata_formalnullable'
    return_raw = ('NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_nullable' if object_case else
        'NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES text_return_null) metadata_return_null])) metadata_union')
    reached = [initial] + r'''
S_initial.COMPLETION = BUDGET
S_receive = $scfr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_receive, 0)
S_receive.TODO = [TYPE_RECEIVE porigin 0]
$receiving_function(S_receive, porigin) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF
$typed_receive_valid(S_receive, porigin, 0)
$lookup(S_receive.ENV, $ptascii("saved")) = (n_formal)
S_receive.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("alias")) = (n_x)
$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)
$lookup(psymboltable_caller.ENV, $ptascii("prefix")) = (n_prefix)
$lookup(psymboltable_caller.ENV, $ptascii("prefixAlias")) = (n_prefix)
n_x <- S_receive.REFCELLS /\ n_copy =/= n_x
S_receive.STORE[n_formal] = DEFINED pvalue_input
S_receive.STORE[n_x] = DEFINED pvalue_input /\ S_receive.STORE[n_copy] = DEFINED pvalue_input
S_receive.STORE[n_prefix] = DEFINED (PINT 2)
~$typed_parameter_source(S_receive, psparam)
$typed_parameter_conversion(S_receive, psparam, pvalue_input) = TYPEVALUE pvalue_input
$parameter_backing_at(S_receive.PARAMETERBACKINGS, n_formal) = eps
$propref_at(S_receive.PROPREFS, n_formal) = eps /\ $reference_coercion_at(S_receive.REFCOERCIONS, n_formal) = eps
$heap_valid($heap_graph(S_receive)) /\ $call_descriptors_valid(S_receive)
S_received = $drive(S_receive, 1)[.COMPLETION = NORMAL]
S_received.STORE = S_receive.STORE /\ S_received.OBJECTPROPS = S_receive.OBJECTPROPS
S_received.PROPREFS = S_receive.PROPREFS /\ S_received.REFCOERCIONS = S_receive.REFCOERCIONS
S_return = $scfr_seek(S_received, 1, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_return, 1)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN pvalue_input
$typed_return_task_valid(S_return, z_return)
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, pvalue_input, pfunction_producer.CODE.STRICT) = TYPEVALUE pvalue_input
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN pvalue_input
S_checked.STORE = S_return.STORE /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
$heap_valid($heap_graph(S_return)) /\ $call_descriptors_valid(S_return)
S_pre = $scfr_seek(S_return, 2, 5000)[.COMPLETION = NORMAL]
$scfr_ready(S_pre, 2)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps /\ S_pre.RESULT = KNOWN pvalue_input
S_pre.STORE[n_copy] = DEFINED pvalue_input /\ S_pre.STORE[n_prefix] = DEFINED (PINT 2)
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
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
$reference_notice_producer_line(S_pre, (porigin_producer), $named_expression($named_source(S_pre, (porigin_call), 1))) = 8
'''.strip().splitlines()
    reached += ['pvalue_input = ' + input_value, 'psparam.BYREF = ' + byref, 'psparam.TYPE = ' + formal_type,
        'pfunction_producer.SIGNATURE.RETURNS = ' + return_type, 'pfunction_producer.CODE.STRICT = ' + strict,
        ('' if strict == 'true' else '~') + '$typed_caller_strict(S_receive)',
        'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (' + formal_raw + ') (BOOLEAN ' + byref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
        '$ptlc($base64(text_formal)) = $ptascii("object")', 'phpType18 = ' + return_raw,
        '$ptlc($base64(text_return)) = $ptascii("object")']
    if object_case:
        reached += ['n_formal = n_x', '$lookup(S_return.ENV, $ptascii("keep")) = (n_keep)',
            r'S_return.STORE[n_formal] = DEFINED (PINT 11) /\ S_return.STORE[n_keep] = DEFINED pvalue_input',
            'S_pre.STORE[n_x] = DEFINED (PINT 11)', '~((HCELL n_keep) <- S_pre.ALLOCATIONS)',
            '$objectprops_at(S_pre.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 13)))}])',
            '$heap_owners($heap_graph(S_pre), HOBJECT n_old) = 2', '$named_reference_notice_object(S_pre, pvalue_input)']
    else:
        reached += [r'n_formal =/= n_x /\ ~(n_formal <- S_receive.REFCELLS)',
            'S_pre.STORE[n_x] = DEFINED PNULL', '~((HCELL n_formal) <- S_pre.ALLOCATIONS)',
            '$ptlc($base64(text_return_null)) = $ptascii("null")']
    proof = '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    reached += [('~' if front else '') + line for line in (proof, header, '$named_reference_notice_pending(S_pre)')]
    if front:
        return reached, []
    reached += r'''
n_private = |S_pre.STORE|
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_prefix), NAMED_SENT (REFERENCE n_private)] /\ pnamedargs_after.NAMED = eps
perrorcall.LINE = 8 /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED pvalue_input /\ n_private <- S_notice.REFCELLS
n_private =/= n_x /\ n_private =/= n_formal /\ n_private =/= n_copy /\ n_private =/= n_prefix
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_notice.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_notice.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_notice)) /\ $error_call_valid(S_notice, perrorcall)
S_resume = $scfr_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED pvalue_input /\ S_resume.STORE[n_copy] = DEFINED pvalue_input
S_resume.STORE[n_prefix] = DEFINED (PINT 29) /\ S_resume.STORE[n_x] = DEFINED (PINT 17)
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
S_written = $scfr_seek(S_resume, 4, 10000)[.COMPLETION = NORMAL]
$scfr_ready(S_written, 4)
$lookup(S_written.ENV, $ptascii("r")) = (n_private)
$lookup(S_written.ENV, $ptascii("snapshot")) = (n_snapshot)
S_written.STORE[n_x] = DEFINED (PINT 17) /\ S_written.STORE[n_copy] = DEFINED pvalue_input
S_written.STORE[n_prefix] = DEFINED (PINT 31)
$parameter_backing_at(S_written.PARAMETERBACKINGS, n_private) = eps
$propref_at(S_written.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_written.REFCOERCIONS, n_private) = eps
$heap_valid($heap_graph(S_written)) /\ $call_descriptors_valid(S_written)
S_full = $drive(S_written, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
~((HCELL n_private) <- S_full.ALLOCATIONS) /\ ~((HCELL n_x) <- S_full.ALLOCATIONS) /\ ~((HCELL n_copy) <- S_full.ALLOCATIONS)
~((HCELL n_snapshot) <- S_full.ALLOCATIONS) /\ ~((HCELL n_prefix) <- S_full.ALLOCATIONS)
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()
    if object_case:
        reached += [r'S_written.STORE[n_private] = DEFINED pvalue_input /\ S_written.STORE[n_snapshot] = DEFINED pvalue_input',
            '$objectprops_at(S_written.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 23)))}])',
            '$heap_owners($heap_graph(S_written), HOBJECT n_old) = 3', '~((HOBJECT n_old) <- S_full.ALLOCATIONS)']
    else:
        reached += [r'S_written.STORE[n_private] = DEFINED (PINT 23) /\ S_written.STORE[n_snapshot] = DEFINED (PINT 19)']
    reached += ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    derived = ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for stage in ('receive', 'return', 'notice'):
        state = 'S_' + stage
        derived += ['S_zero_' + stage + ' = $drive(' + state + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = ' + state,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + state + ', 2)']
    if object_case:
        vectors = [(['object'], True), (['object', 'null'], True), (['null', 'object'], True),
            (['object', 'false', 'int'], True), (['array', 'float', 'object'], True),
            (['object', 'array', 'int', 'float', 'string', 'null', 'true'], True),
            (['object', 'object'], False), (['object', 'object', 'int'], False),
            (['object', 'bool', 'false'], False), (['object', 'false', 'true'], False),
            (['object', 'array', 'int', 'float', 'string', 'null', 'false', 'true'], False),
            (['object', 'mixed', 'int'], False), (['object', 'callable', 'int'], False)]
        for members, accepted in vectors:
            normalized, syntax = branches(members), raw(members)
            mark = '' if accepted else '~'
            derived += [mark + '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), ' + syntax + ', pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + syntax + ') (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
            derived += [mark + '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([' + parameter + ']), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])']
        for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged object default"'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]]')]
        for normalized in ('eps', branches(['array']), branches(['object', 'null']), '[(PTBRANCH ([PTCLASS ($ptascii("stdClass"))]))]'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]]')]
        derived += ['~' + proof.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),')]
        for normalized in (branches(['object', 'null', 'int']), branches(['null', 'object']), branches(['object'])):
            derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])')]
        for tag in ('NName', 'NNameFullyQualified'):
            derived += ['~' + header.replace('phpType18,', tag + ' (BYTES "b2JqZWN0") metadata_formal,').replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + branches(['object']) + '])')]
        for strict_value in ('false', 'true'):
            for value in ('PNULL', 'PBOOL false', 'PINT 0', 'PSTRING ($ptascii("17"))'):
                derived += ['$typed_conversion_at(S_receive, psparam.TYPE, ' + value + ', ' + strict_value + ') = TYPEREJECT']
        derived += ['$named_reference_notice_object(S_pre, pvalue_input)',
            '~$named_reference_notice_object(S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HOBJECT n_old]], pvalue_input)']
    return reached, derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native, cases = json.loads(provenance.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), CATALOGUE, provenance]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:2]):
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
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[row['id'] for row in cases[:2]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-object-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

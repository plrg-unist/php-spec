#!/usr/bin/env python3
"""Ground ordered plain-class returns, frame retirement and private Notice cells."""
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
CATALOGUE = Path(__file__).with_name('global_plain_ordered_stdclass_return_producer_reference_notice_cases.json')
PREFIX = r'''
dec $gpo_output(pevent*) : ptbytes
def $gpo_output(eps) = eps
def $gpo_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $gpo_output(pevent*)
dec $gpo_ready(pstate, nat) : bool
def $gpo_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("make")
def $gpo_ready(S, 1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget eps 0 eps porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
def $gpo_ready(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 ([REFERENCE n]) porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
def $gpo_ready(S, n) = false -- otherwise
dec $gpo_seek(pstate, nat, nat) : pstate
def $gpo_seek(S, n_stage, n) = S -- if $gpo_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $gpo_seek(S, n_stage, n) = $gpo_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$gpo_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gpo_seek(S, n_stage, n) = S -- otherwise
'''


def normalized(members, name):
    nominal = '([' + ', '.join(map(str, name.encode())) + '])' if '\x00' in name else '($ptascii(' + json.dumps(name) + '))'
    return '[' + ', '.join('(PTBRANCH ([PTCLASS ' + nominal + ']))' if kind == 'class' else '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw(members, name, tag='NName'):
    nodes = [(tag if kind == 'class' else 'NIdentifier') + ' (BYTES ' + json.dumps(base64.b64encode((name if kind == 'class' else kind).encode()).decode()) + ') metadata_function' for kind in members]
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_function'


def reached(case, front):
    lines = r'''
S_initial.COMPLETION = BUDGET
S_return = $gpo_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$gpo_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("make")
~pfunction_producer.SIGNATURE.BYREF
pfunction_producer.ENV.NAMESPACE = eps /\ pfunction_producer.ENV.CLASSES = eps
$lookup(S_return.ENV, $ptascii("saved")) = (n_saved)
S_return.STORE[n_saved] = DEFINED pvalue_saved
$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN pvalue_saved
$typed_return_task_valid(S_return, z_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL
S_checked.RESULT = KNOWN pvalue_return
S_pre = $gpo_seek(S_return, 1, 4000)[.COMPLETION = NORMAL]
$gpo_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN pvalue_return
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
~((HCELL n_saved) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("saved")) = eps
$lookup(S_pre.ENV, $ptascii("x")) = (n_caller)
$lookup(S_pre.ENV, $ptascii("alias")) = (n_caller)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
n_copy =/= n_caller /\ n_saved =/= n_caller
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer
phpType6_producer = SEQUENCE ([NArg ABSENT expression_actual (BOOLEAN false) (BOOLEAN false) metadata_actual])
$reference_cv(expression_actual) = ($ptascii("x"))
phpType16 = SEQUENCE ([phpType17])
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.NAME = $ptascii("saved") /\ ~psparam.BYREF /\ psparam.REQUIRED /\ ~psparam.VARIADIC
$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])
$reference_notice_producer_line(S_pre, (porigin_argument), NExprFuncCall phpType19_producer phpType6_producer metadata_producer) = 8
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
'''.strip().splitlines()
    lines += [('' if case['callee_strict'] else '~') + 'pfunction_producer.CODE.STRICT',
        'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case['return_members'], case['class_return'])]
    nodes = [(('NName' if kind == 'class' else 'NIdentifier') + ' (BYTES text_return' + str(i) + ') metadata_return' + str(i)) for i, kind in enumerate(case['return_members'])]
    lines += ['phpType18 = NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_union']
    for i, kind in enumerate(case['return_members']):
        lines += [('$base64(text_return' + str(i) + ') = $ptascii(' + json.dumps(case['class_return']) + ')') if kind == 'class' else ('$ptlc($base64(text_return' + str(i) + ')) = $ptascii(' + json.dumps(kind) + ')')]
    if case['kind'] in ('bool', 'int'):
        result = 'PBOOL false' if case['kind'] == 'bool' else 'PINT 37'
        conversion = 'TYPEBOOL pvalue_saved' if case['kind'] == 'bool' else 'TYPEVALUE (PINT 37)'
        lines += ['$string_bytes(pvalue_saved) = ($ptascii(' + json.dumps(case['input_text']) + '))',
            'pvalue_return = ' + result, '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, pvalue_saved, false) = ' + conversion,
            '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, pvalue_saved, true) = TYPEREJECT']
    elif case['kind'] == 'string':
        lines += ['pvalue_saved = PINT 37', '$string_bytes(pvalue_return) = ($ptascii("37"))',
            '$string_carrier_valid(S_pre, pvalue_return)', '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PINT 37, false) = TYPESTRING (PINT 37)']
    elif case['kind'] == 'array':
        lines += ['pvalue_saved = PARRAY n_array', 'pvalue_return = PARRAY n_array',
            'S_pre.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13)), ENTRY (KINT 1) (DIRECT (PINT 17))]',
            '$heap_owners($heap_graph(S_pre), HARRAY n_array) = 1',
            'S_pre.STORE[n_copy] = DEFINED (PARRAY n_original_array)', 'n_array =/= n_original_array',
            'S_pre.ARRAYS[n_original_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]']
    else:
        lines += ['pvalue_saved = POBJECT n_object', 'pvalue_return = POBJECT n_object',
            'S_pre.STORE[n_copy] = DEFINED (POBJECT n_object)',
            '$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops_pre)',
            'pobjectprops_pre.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 11)))}]']
    lines += [('~' if front else '') + '$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)',
        ('~' if front else '') + '$positional_reference_notice_pending(S_pre)']
    return lines


def completed(case):
    lines = r'''
n_private = |S_pre.STORE|
n_private =/= n_caller /\ n_private =/= n_saved
S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call
perrorcall.LINE = 8 /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED pvalue_return
n_private <- S_notice.REFCELLS
$node_children(S_notice, HCELL n_private) = $value_nodes(pvalue_return)
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$error_call_valid(S_notice, perrorcall) /\ $heap_valid($heap_graph(S_notice))
S_resume = $gpo_seek(S_notice, 2, 4000)[.COMPLETION = NORMAL]
$gpo_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED pvalue_return
S_resume.STORE[n_caller] = DEFINED (PINT 17)
S_resume.PARAMETERBACKINGS = eps /\ S_resume.PROPREFS = eps /\ S_resume.REFCOERCIONS = eps
$error_call_valid(S_resume, perrorcall)
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
S_full = $drive(S_resume, 12000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.FRAMES = eps /\ S_full.CURRENT = eps
S_full.ENV = eps /\ ~((HCELL n_private) <- S_full.ALLOCATIONS)
~((HCELL n_caller) <- S_full.ALLOCATIONS) /\ ~((HCELL n_copy) <- S_full.ALLOCATIONS)
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines() + ['$gpo_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    if case['kind'] == 'array':
        lines += ['~((HARRAY n_array) <- S_full.ALLOCATIONS)', '~((HARRAY n_original_array) <- S_full.ALLOCATIONS)']
    if case['kind'] == 'object':
        lines += ['~((HOBJECT n_object) <- S_full.ALLOCATIONS)']
    return lines


def controls(case):
    header = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    name = case['class_return']
    source_nodes = [(('NName' if kind == 'class' else 'NIdentifier') + ' (BYTES text_return' + str(i) + ') metadata_return' + str(i)) for i, kind in enumerate(case['return_members'])]
    view_nodes = [node.replace('NName ', 'NNameFullyQualified ', 1) for node in source_nodes]
    accepted = [['class', k] for k in ('array', 'int', 'float', 'bool', 'string', 'null', 'false', 'true', 'callable', 'iterable')]
    accepted += [m[::-1] for m in accepted]
    accepted += [['float', 'int', 'class'], ['bool', 'class', 'string'], ['class', 'array', 'int', 'float', 'bool', 'string', 'null', 'callable'], ['callable', 'null', 'string', 'true', 'float', 'int', 'iterable', 'class']]
    lines = ['$reference_notice_producer_global_union_view([' + ', '.join(source_nodes) + '], false) = ([' + ', '.join(view_nodes) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for members in accepted:
        proof = header + raw(members, name) + ', ' + signature + '[.RETURNS = ' + normalized(members, name) + '])'
        lines += [proof, '~' + proof.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
            ('' if name == 'stdClass' else '~') + proof.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]],', 1),
            '~' + proof.replace(normalized(members, name), normalized(members[::-1], name)),
            '~' + proof.replace(normalized(members, name), normalized(members, name.swapcase()))]
    for members in [['class'], ['class', 'class'], ['class', 'int', 'int'], ['class', 'bool', 'true'], ['class', 'false', 'true'], ['class', 'array', 'iterable'], ['class', 'object'], ['class', 'mixed'], ['class', 'void']]:
        lines += ['~' + header + raw(members, name) + ', ' + signature + '[.RETURNS = ' + normalized(members, name) + '])']
    for tag in ('NNameFullyQualified', 'NNameRelative', 'NIdentifier'):
        node = raw(case['return_members'], name, tag)
        nodes = node.removeprefix('NUnionType (SEQUENCE (').removesuffix(')) metadata_function')
        lines += ['$reference_notice_producer_global_union_view(' + nodes + ', false) = eps']
    lines += ['$reference_notice_producer_global_union_view([NIdentifier (BYTES "aW50") metadata_function, NIdentifier (BYTES "ZmxvYXQ=") metadata_function], false) = eps']
    for bad in ('Other', 'Other\\stdClass', '\\stdClass', 'stdClass\x00'):
        lines += ['~' + header + raw(case['return_members'], bad) + ', ' + signature + '[.RETURNS = ' + normalized(case['return_members'], bad) + '])']
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged ordered return formal"'):
        lines += ['~' + header + 'phpType18, ' + signature + '[.PARAMETERS = [psparam[' + update + ']]])']
    bare_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (NName (BYTES "c1RkQ2xBc1M=") metadata_function) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    lines += ['~$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + bare_parameter + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized(['class'], 'sTdClAsS') + ']]])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)', 'S_zero_' + stage + '.COMPLETION = BUDGET /\\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    return lines


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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 5
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths, specs, reached_lines, derived = [Path(__file__), CATALOGUE, provenance], [], [], []
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            current = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + reached(case, args.front)
            extra = [] if args.front or index else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $gpo_case' + str(index) + '() : bool\ndef $gpo_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached_lines += current
            derived += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $gpo_case' + str(i) + '()\n' for i in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived), reached_conditions=len(reached_lines), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-ordered-stdclass-return-front' if args.front else 'global-plain-ordered-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

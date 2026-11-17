#!/usr/bin/env python3
"""Independently check nullable/union formals, iterable return arrays and Notice cleanup."""
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
CATALOGUE = Path(__file__).with_name('singleton_cv_iterable_return_producer_reference_notice_review_cases.json')
ITERABLE = '[(PTBRANCH ([PTBUILTIN "iterable"]))]'
PREFIX = r'''
dec $sr_output(pevent*) : ptbytes
def $sr_output(eps) = eps
def $sr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $sr_output(pevent*)
dec $sr_quiet(pevent*) : bool
def $sr_quiet(eps) = true
def $sr_quiet((OUTPUT ptbytes) :: pevent*) = $sr_quiet(pevent*)
def $sr_quiet(pevent*) = false -- otherwise
dec $sr_ready(pstate, nat) : bool
def $sr_ready(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- NAMES_MAKE
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
def $sr_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget eps 0 eps porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- NAMES_TAKE
def $sr_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- NAMES_TAKE
def $sr_ready(S, n_stage) = false -- otherwise
dec $sr_seek(pstate, nat, nat) : pstate
def $sr_seek(S, n_stage, n) = S -- if $sr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $sr_seek(S, n_stage, n) = $sr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$sr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $sr_seek(S, n_stage, n) = S -- otherwise
'''


def branches(kinds):
    return '[' + ', '.join('PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + '])' for kind in kinds) + ']'


def reached(case, front):
    if case.get('priority_control'):
        return ['S_initial.COMPLETION = BUDGET',
            'S_full = $drive(S_initial[.COMPLETION = NORMAL], 10000)',
            r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
            '$sr_quiet(S_full.EVENTS)',
            '$sr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
            '$lookup(S_full.ENV, $ptascii("r")) = (n_r)',
            'S_full.STORE[n_r] = DEFINED (PINT 11)',
            '$lookup(S_full.ENV, $ptascii("x")) = (n_x)',
            '$lookup(S_full.ENV, $ptascii("alias")) = (n_x)',
            'S_full.STORE[n_x] = DEFINED (PINT 23)',
            '$lookup(S_full.ENV, $ptascii("copy")) = (n_copy)',
            'S_full.STORE[n_copy] = DEFINED pvalue_copy',
            '$string_bytes(pvalue_copy) = ($ptascii("17"))',
            r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_return = $sr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]',
        '$sr_ready(S_return, 0)',
        'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
        'S_return.CURRENT = (pcallcontext)',
        '$function_at($all_functions(S_return), pcallcontext.FUNCTION) = (pfunction_producer)',
        'pfunction_producer.NAME = $ptascii(' + json.dumps(case['namespace'] + '\\make') + ')',
        r'~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_return, pfunction_producer)',
        '~pfunction_producer.CODE.STRICT',
        'pfunction_producer.SIGNATURE.RETURNS = ' + ITERABLE,
        'pfunction_producer.SIGNATURE.PARAMETERS = [psparam]',
        'psparam.NAME = $ptascii("saved")',
        'psparam.TYPE = ' + branches(case['formal_members']),
        ('psparam.BYREF' if case['formal_byref'] else '~psparam.BYREF'),
        r'psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE',
        '$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)',
        '$typed_return_task_valid(S_return, z_return)',
        'S_resolved = $resolve_at(S_return, S_return.RESULT, z_return)',
        'S_resolved.RESULT = KNOWN (PARRAY n_root)',
        '$typed_conversion_at(S_resolved, ' + ITERABLE + ', PARRAY n_root, false) = TYPEVALUE (PARRAY n_root)',
        '$typed_conversion_at(S_resolved, ' + ITERABLE + ', PARRAY n_root, true) = TYPEVALUE (PARRAY n_root)',
        '$typed_return_value(S_return, z_return) = S_resolved',
        'S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]',
        'S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_unwind*',
        r'$heap_valid($heap_graph(S_after_return)) /\ $call_descriptors_valid(S_after_return)',
        'S_pre = $sr_seek(S_after_return, 1, 5000)[.COMPLETION = NORMAL]',
        '$sr_ready(S_pre, 1)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*',
        'S_pre.RESULT = KNOWN (PARRAY n_root)',
        r'S_pre.CURRENT = eps /\ S_pre.FRAMES = eps /\ S_pre.PARAMETERBACKINGS = eps',
        '$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer',
        'phpType6_producer = SEQUENCE ([phpType7_actual])',
        'phpType7_actual = NArg ABSENT expression_actual (BOOLEAN false) (BOOLEAN false) metadata_actual',
        'expression_actual = NExprVariable (BYTES text_actual) metadata_variable',
        '$reference_cv(expression_actual) = (ptbytes_actual)',
        '$lookup(S_pre.ENV, ptbytes_actual) = (n_caller)',
        '$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)',
        '$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
        'phpType16 = SEQUENCE ([phpType17])',
        'phpType18 = NIdentifier (BYTES text_return) metadata_return',
        '$ptlc($base64(text_return)) = $ptascii("iterable")',
        '~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE)',
        '$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])',
        ('~' if front else '') + '$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)',
        ('~' if front else '') + '$positional_reference_notice_pending(S_pre)',
        '$named_reference_notice_array(S_pre, PARRAY n_root)',
        r'$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)']
    if case['formal_byref']:
        lines += ['n_formal = n_caller',
            'S_pre.STORE[n_copy] = DEFINED (PBOOL false)',
            'S_pre.STORE[n_caller] = DEFINED (PARRAY n_root)',
            '$lookup(S_pre.ENV, $ptascii("alias")) = (n_caller)',
            '$heap_owners($heap_graph(S_pre), HCELL n_caller) = 2']
    else:
        lines += ['n_formal =/= n_caller',
            'S_return.STORE[n_formal] = DEFINED PNULL',
            r'S_pre.STORE[n_copy] = DEFINED PNULL /\ S_pre.STORE[n_caller] = DEFINED PNULL',
            '~((HCELL n_formal) <- S_pre.ALLOCATIONS)']
    if front:
        lines += ['S_stop = $drive(S_pre, 1)',
            'S_stop.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"']
    return lines


def completed(case):
    if case.get('priority_control'):
        return []
    lines = ['n_private = |S_pre.STORE|',
        r'n_private =/= n_caller /\ n_private =/= n_formal /\ n_private =/= n_copy',
        'S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*',
        'perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z',
        'perrorcall.LINE = $reference_notice_producer_line(S_pre, $call_argument_origin(S_pre, (porigin_call), 0), $call_argument_expression(S_pre, (porigin_call), 0))',
        'perrorcall.LEVEL = 8',
        'S_notice.STORE[n_private] = DEFINED (PARRAY n_root)',
        '$node_children(S_notice, HCELL n_private) = [HARRAY n_root]',
        '$heap_owners($heap_graph(S_notice), HCELL n_private) = 1',
        r'$error_call_valid(S_notice, perrorcall) /\ $heap_valid($heap_graph(S_notice))']
    if case.get('handler_throws'):
        # The returned constant array remains owned by its compiled literal pool.
        lines += ['S_full = $drive(S_notice, 10000)',
            '~((HCELL n_private) <- S_full.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_full), HCELL n_private) = 0',
            '$lookup(S_full.ENV, $ptascii("r")) = (n_r)',
            'S_full.STORE[n_r] = DEFINED (PINT 11)',
            '$lookup(S_full.ENV, $ptascii("alias")) = (n_alias)',
            'S_full.STORE[n_alias] = DEFINED (PARRAY n_alias_array)',
            'n_alias_array =/= n_root',
            'pfunction_producer.ORIGIN = PORIGIN n_source pcpath_producer',
            'porigin_literal = PORIGIN n_source (pcpath_producer ++ [PCFIELD 5, PCINDEX 0, PCFIELD 0, PCFIELD 1])',
            '$origin_node(S_full.SOURCES, porigin_literal) = (NExprArray phpType12_literal metadata_literal)',
            '$pool_value(S_full.POOLS, porigin_literal) = (PARRAY n_root)',
            '(HARRAY n_root) <- $pools_nodes(S_full.POOLS)',
            '$heap_owners($heap_graph(S_full), HARRAY n_root) = 1',
            '$entry_lookup(S_full.ARRAYS[n_root].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 5))',
            '$entry_lookup(S_full.ARRAYS[n_alias_array].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 29))']
    else:
        lines += ['S_resume = $sr_seek(S_notice, 2, 5000)[.COMPLETION = NORMAL]',
            '$sr_ready(S_resume, 2)',
            'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
            'S_resume.STORE[n_private] = DEFINED (PARRAY n_root)',
            r'$error_call_valid(S_resume, perrorcall) /\ $heap_valid($heap_graph(S_resume))',
            'S_full = $drive(S_resume, 10000)',
            '$lookup(S_full.ENV, $ptascii("r")) = (n_private)',
            'S_full.STORE[n_private] = DEFINED pvalue_retyped',
            '$string_bytes(pvalue_retyped) = ($ptascii("done"))',
            '$node_children(S_full, HCELL n_private) = eps',
            '$lookup(S_full.ENV, $ptascii("snapshot")) = (n_snapshot)',
            'S_full.STORE[n_snapshot] = DEFINED (PARRAY n_snapshot_array)',
            '$entry_lookup(S_full.ARRAYS[n_snapshot_array].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 41))']
    lines += [r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
        '$sr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
        '$sr_quiet(S_full.EVENTS)',
        r'$propref_at(S_full.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_full.REFCOERCIONS, n_private) = eps',
        'S_full.PARAMETERBACKINGS = eps',
        r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']
    return lines


def controls(case):
    if case.get('priority_control'):
        return ['$typed_conversion_at(S_full, ' + branches(['int']) + ', pvalue_copy, true) = TYPEREJECT']
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    raw = 'NIdentifier (BYTES text_return) metadata_return'
    for replacement in ('NName (BYTES text_return) metadata_return',
            'NNameFullyQualified (BYTES text_return) metadata_return',
            'NNullableType (' + raw + ') metadata_return'):
        lines += ['~' + header + replacement + ', ' + signature + ')']
    for kind in ('array', 'null', 'mixed', 'callable'):
        lines += ['~' + header + raw + ', ' + signature + '[.RETURNS = ' + branches([kind]) + '])']
    for edit in ('REQUIRED = false', 'VARIADIC = true', 'BYREF = ' + str(not case['formal_byref']).lower(),
            'DEFAULT = PSDEFAULTUNSUPPORTED "forged iterable default"', 'TYPE = ' + branches(['bool'])):
        lines += ['~' + header + raw + ', ' + signature + '[.PARAMETERS = [psparam[.' + edit + ']]])']
    lines += ['$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), ' + signature + '[.PARAMETERS = [psparam, psparam]][.RETURNS = eps])',
        '$reference_notice_producer_header(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), phpType18, ' + signature + '[.PARAMETERS = [psparam, psparam]])']
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), CATALOGUE, provenance]
    specs, reached_lines, derived_lines = [], [], []
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
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            current = [initial] + reached(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $sr_case' + str(index) + '() : bool\ndef $sr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached_lines += current
            derived_lines += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    prefix = PREFIX
    for marker, name in (('NAMES_MAKE', 'make'), ('NAMES_TAKE', 'take')):
        prefix = prefix.replace(marker, '[' + ', '.join('$ptascii(' + json.dumps(case['namespace'] + '\\' + name) + ')' for case in cases) + ']')
    fixture = out / 'state.watsup'
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $sr_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('singleton-cv-iterable-return-front' if args.front else 'singleton-cv-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

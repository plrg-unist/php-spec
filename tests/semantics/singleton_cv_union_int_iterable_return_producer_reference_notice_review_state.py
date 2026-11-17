#!/usr/bin/env python3
"""Check single-CV ordered iterable/int returns, scalar coercion and real private-cell cleanup."""
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
import singleton_cv_iterable_return_producer_reference_notice_review_state as base

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('singleton_cv_union_int_iterable_return_producer_reference_notice_review_cases.json')
PREFIX = base.PREFIX.replace('S.RESULT = KNOWN (PARRAY n_root)', 'S.RESULT = KNOWN pvalue_result')
branches = base.branches


def raw(members, leaf='NIdentifier'):
    return 'NUnionType (SEQUENCE ([' + ', '.join((leaf if kind == 'iterable' else 'NIdentifier') + ' (BYTES "' + base64.b64encode(kind.encode()).decode() + '") metadata_union' for kind in members) + '])) metadata_union'


def reached(case, front):
    signature = 'pfunction_producer.SIGNATURE'
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_return = $sr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]', '$sr_ready(S_return, 0)',
        'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*', 'S_return.CURRENT = (pcallcontext)',
        '$function_at($all_functions(S_return), pcallcontext.FUNCTION) = (pfunction_producer)',
        'pfunction_producer.NAME = $ptascii(' + json.dumps(case['namespace'] + chr(92) + 'make') + ')',
        '~pfunction_producer.SIGNATURE.BYREF /\\ ~$function_generator(S_return, pfunction_producer)',
        ('pfunction_producer.CODE.STRICT' if case.get('callee_strict') else '~pfunction_producer.CODE.STRICT'),
        signature + '.RETURNS = ' + branches(case['return_members']),
        signature + '.PARAMETERS = [psparam]',
        'psparam.NAME = $ptascii("saved")',
        'psparam.BYREF = ' + str(case['formal_byref']).lower(),
        r'psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE',
        'psparam.TYPE = ' + (branches(case['formal_members']) if case.get('formal_kind') else 'eps'),
        '$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)',
        '$typed_return_task_valid(S_return, z_return)',
        '$origin_node(S_return.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
        'phpType16 = SEQUENCE ([phpType17])',
        'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first, NIdentifier (BYTES text_second) metadata_second])) metadata_union',
        '$ptlc($base64(text_first)) = $ptascii(' + json.dumps(case['return_members'][0]) + ')',
        '$ptlc($base64(text_second)) = $ptascii(' + json.dumps(case['return_members'][1]) + ')',
        'S_resolved = $resolve_at(S_return, S_return.RESULT, z_return)']
    if case.get('priority_control'):
        return lines + ['S_resolved.RESULT = KNOWN pvalue_string', '$string_bytes(pvalue_string) = ($ptascii("17"))',
            '$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', pvalue_string, true) = TYPEREJECT',
            'S_checked = $typed_return_value(S_return, z_return)', 'S_checked.COMPLETION = THROWN "TypeError" ptbytes_error z_return',
            'S_full = $drive(S_return, 10000)',
            'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps /\\ S_full.CURRENT = eps /\\ S_full.FRAMES = eps',
            '$sr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')', '$sr_quiet(S_full.EVENTS)',
            '$lookup(S_full.ENV, $ptascii("r")) = (n_r)', 'S_full.STORE[n_r] = DEFINED (PINT 11)',
            '$lookup(S_full.ENV, $ptascii("x")) = (n_caller)', '$lookup(S_full.ENV, $ptascii("alias")) = (n_caller)',
            'S_full.STORE[n_caller] = DEFINED (PINT 23)',
            '$heap_valid($heap_graph(S_full)) /\\ $call_descriptors_valid(S_full)']
    result = 'PINT 17' if case['value_kind'] == 'int' else 'PARRAY n_root'
    lines += (['S_resolved.RESULT = KNOWN (PARRAY n_root)'] if case['value_kind'] == 'array' else [])
    lines += ['S_checked = $typed_return_value(S_return, z_return)',
        'S_checked.COMPLETION = NORMAL /\\ S_checked.RESULT = KNOWN (' + result + ')',
        'S_checked.STORE = S_resolved.STORE /\\ S_checked.ARRAYS = S_resolved.ARRAYS',
        'S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]',
        'S_after_return.TODO = (RETURN_UNWIND (KNOWN (' + result + ')) porigin_return?) :: ptask_unwind*',
        'S_pre = $sr_seek(S_after_return, 1, 5000)[.COMPLETION = NORMAL]', '$sr_ready(S_pre, 1)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*',
        'S_pre.RESULT = KNOWN (' + result + ')',
        'S_pre.CURRENT = eps /\\ S_pre.FRAMES = eps /\\ S_pre.PARAMETERBACKINGS = eps',
        '$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer',
        'phpType6_producer = SEQUENCE ([phpType7_actual])',
        'phpType7_actual = NArg ABSENT expression_actual (BOOLEAN false) (BOOLEAN false) metadata_actual',
        '$reference_cv(expression_actual) = ($ptascii("x"))',
        '$lookup(S_pre.ENV, $ptascii("x")) = (n_caller)', '$lookup(S_pre.ENV, $ptascii("alias")) = (n_caller)',
        '$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)',
        '$reference_notice_producer_arguments(phpType6_producer, phpType16, ' + signature + '[.RETURNS = eps])',
        ('~' if front else '') + '$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, ' + signature + ')',
        ('~' if front else '') + '$positional_reference_notice_pending(S_pre)',
        '$named_reference_notice_operand(S_pre, S_pre.RESULT)',
        '$heap_valid($heap_graph(S_pre)) /\\ $call_descriptors_valid(S_pre)']
    if case['value_kind'] == 'int':
        lines += ['S_resolved.RESULT = KNOWN pvalue_string', '$string_bytes(pvalue_string) = ($ptascii("17"))',
            'S_return.STORE[n_formal] = DEFINED pvalue_string',
            'S_pre.STORE[n_caller] = DEFINED pvalue_string /\\ S_pre.STORE[n_copy] = DEFINED pvalue_string',
            'n_formal =/= n_caller /\\ ~((HCELL n_formal) <- S_pre.ALLOCATIONS)']
    else:
        lines += ['S_resolved.RESULT = KNOWN (PARRAY n_root)', 'n_formal = n_caller',
            'S_pre.STORE[n_caller] = DEFINED (PARRAY n_root)',
            'S_pre.STORE[n_copy] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
            '$entry_lookup(S_pre.ARRAYS[n_copy_root].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 3))']
    if front:
        lines += ['S_stop = $drive(S_pre, 1)', 'S_stop.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"']
    return lines


def completed(case):
    if case.get('priority_control'):
        return []
    result = 'PINT 17' if case['value_kind'] == 'int' else 'PARRAY n_root'
    lines = ['n_private = |S_pre.STORE|', 'n_private =/= n_caller /\\ n_private =/= n_formal',
        'S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]', 'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*',
        'perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(case['expected_notice_line']),
        'S_notice.STORE[n_private] = DEFINED (' + result + ')', '$heap_owners($heap_graph(S_notice), HCELL n_private) = 1',
        '$error_call_valid(S_notice, perrorcall) /\\ $heap_valid($heap_graph(S_notice))',
        'S_full = $drive(S_notice, 10000)',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps /\\ S_full.CURRENT = eps /\\ S_full.FRAMES = eps',
        '$sr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')', '$sr_quiet(S_full.EVENTS)',
        'S_full.PARAMETERBACKINGS = eps',
        '$propref_at(S_full.PROPREFS, n_private) = eps /\\ $reference_coercion_at(S_full.REFCOERCIONS, n_private) = eps',
        '$heap_valid($heap_graph(S_full)) /\\ $call_descriptors_valid(S_full)']
    if case['value_kind'] == 'int':
        lines += ['$node_children(S_notice, HCELL n_private) = eps',
            '$lookup(S_full.ENV, $ptascii("r")) = (n_private)', 'S_full.STORE[n_private] = DEFINED pvalue_done',
            '$string_bytes(pvalue_done) = ($ptascii("done"))', '$node_children(S_full, HCELL n_private) = eps',
            '$lookup(S_full.ENV, $ptascii("snapshot")) = (n_snapshot)', 'S_full.STORE[n_snapshot] = DEFINED (PARRAY n_snapshot_array)',
            '$entry_lookup(S_full.ARRAYS[n_snapshot_array].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 41))',
            'S_full.STORE[n_copy] = DEFINED pvalue_string', 'S_full.STORE[n_caller] = DEFINED pvalue_new',
            '$string_bytes(pvalue_new) = ($ptascii("new"))']
    else:
        lines += ['$node_children(S_notice, HCELL n_private) = [HARRAY n_root]',
            '~((HCELL n_private) <- S_full.ALLOCATIONS)', '$heap_owners($heap_graph(S_full), HCELL n_private) = 0',
            '$heap_owners($heap_graph(S_full), HARRAY n_root) = 1',
            '$entry_lookup(S_full.ARRAYS[n_root].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 5))']
    return lines


def controls(case):
    if case.get('priority_control'):
        return ['$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', pvalue_string, false) = TYPEINTEGER pvalue_string']
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + '.COMPLETION = BUDGET /\\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    for leaf in ('NName', 'NNameFullyQualified'):
        lines.append('~' + header + raw(case['return_members'], leaf) + ', ' + signature + ')')
    for members in (['iterable', 'int'], ['int', 'iterable'], ['iterable', 'null'], ['null', 'iterable']):
        lines.append(header + raw(members) + ', ' + signature + '[.RETURNS = ' + branches(members) + '])')
    for members in (['iterable', 'float'], ['float', 'iterable'], ['iterable', 'array'], ['array', 'iterable'], ['iterable', 'iterable'], ['int', 'int'], ['iterable', 'int', 'null']):
        polarity = '' if members in (['iterable', 'float'], ['float', 'iterable']) else '~'
        lines.append(polarity + header + raw(members) + ', ' + signature + '[.RETURNS = ' + branches(members) + '])')
    for members in (list(reversed(case['return_members'])), ['array', 'int']):
        lines.append('~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + branches(members) + '])')
    for edit in ('REQUIRED = false', 'VARIADIC = true', 'BYREF = ' + str(not case['formal_byref']).lower(), 'DEFAULT = PSDEFAULTUNSUPPORTED "forged producer default"'):
        lines.append('~' + header + 'phpType18, ' + signature + '[.PARAMETERS = [psparam[.' + edit + ']]])')
    for bad_arg in ('NArg ABSENT expression_actual (BOOLEAN true) (BOOLEAN false) metadata_actual', 'NArg ABSENT expression_actual (BOOLEAN false) (BOOLEAN true) metadata_actual'):
        lines.append('~$reference_notice_producer_header(SEQUENCE ([' + bad_arg + ']), phpType16, phpType18, ' + signature + ')')
    for member in ('iterable', 'int'):
        bare = 'NIdentifier (BYTES "' + base64.b64encode(member.encode()).decode() + '") metadata_union'
        lines.append(header + bare + ', ' + signature + '[.RETURNS = ' + branches([member]) + '])')
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
    paths = [Path(__file__), Path(base.__file__), CATALOGUE, provenance]
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
    print('singleton-cv-union-int-iterable-return-front' if args.front else 'singleton-cv-union-int-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

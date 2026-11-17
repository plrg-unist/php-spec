#!/usr/bin/env python3
"""Check mixed and duplicate CV iterable formals through return and private Notice cells."""
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
import singleton_cv_iterable_formal_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_iterable_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX
ITERABLE = prior.ITERABLE
branches = prior.prior.branches


def vector(case, selected, other):
    return '[' + ', '.join([selected, other] if case['iterable_index'] == 0 else [other, selected]) + ']'


def reached(case, front):
    if case.get('receive_priority_control'):
        return prior.reached(case, front) + [
            '$call_target(S_full, $ptascii(' + json.dumps(case['namespace'] + chr(92) + 'make') + '), eps) = (pfunction_producer)',
            'pfunction_producer.SIGNATURE.PARAMETERS = ' + vector(case, 'psparam', 'psparam_other'),
            'psparam.TYPE = ' + ITERABLE,
            'psparam_other.TYPE = ' + branches(['int']),
            '$lookup(S_full.ENV, $ptascii("stamp")) = (n_stamp)',
            '$lookup(S_full.ENV, $ptascii("stampAlias")) = (n_stamp)',
            'S_full.STORE[n_stamp] = DEFINED pvalue_done',
            '$string_bytes(pvalue_done) = ($ptascii("done"))',
            '$propref_at(S_full.PROPREFS, n_stamp) = eps',
            '$reference_coercion_at(S_full.REFCOERCIONS, n_stamp) = eps']
    # The inherited fixture names its non-null return leaf "iterable"; source
    # branches here are array/null while the selected formal stays iterable.
    base = dict(case, return_members=['iterable' if kind == 'array' else kind for kind in case['return_members']])
    lines = []
    for line in prior.reached(base, front):
        if line == 'pfunction_producer.SIGNATURE.PARAMETERS = [psparam]':
            line = 'pfunction_producer.SIGNATURE.PARAMETERS = ' + vector(case, 'psparam', 'psparam_other')
        elif line == 'phpType6_producer = SEQUENCE ([phpType7_actual])':
            line = 'phpType6_producer = SEQUENCE (' + vector(case, 'phpType7_actual', 'phpType7_other') + ')'
        elif line == 'phpType16 = SEQUENCE ([phpType17])':
            line = 'phpType16 = SEQUENCE (' + vector(case, 'phpType17', 'phpType17_other') + ')'
        elif line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + branches(case['return_members'])
        elif line == '$ptlc($base64(text_return)) = $ptascii("iterable")':
            line = '$ptlc($base64(text_return)) = $ptascii("array")'
        lines.append(line)
    ref = str(case['other_byref']).lower()
    lines += ['phpType7_other = NArg ABSENT expression_other (BOOLEAN false) (BOOLEAN false) metadata_other_actual',
        'expression_other = NExprVariable (BYTES text_other_actual) metadata_other_variable',
        '$reference_cv(expression_other) = ($ptascii(' + json.dumps(case['other_actual_name']) + '))',
        '$lookup(S_pre.ENV, $ptascii(' + json.dumps(case['other_actual_name']) + ')) = (n_other_caller)',
        'phpType17_other = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_other_formal) metadata_other_type) (BOOLEAN ' + ref + ') (BOOLEAN false) phpType10_other ABSENT (SEQUENCE eps) metadata_other_parameter',
        '$ptlc($base64(text_other_formal)) = $ptascii(' + json.dumps(case['other_kind']) + ')',
        'psparam_other.NAME = $ptascii(' + json.dumps(case['other_name']) + ')',
        'psparam_other.TYPE = ' + branches([case['other_kind']]),
        'psparam_other.BYREF = ' + ref + r' /\ psparam_other.REQUIRED /\ ~psparam_other.VARIADIC /\ psparam_other.DEFAULT = PSNONE',
        '$lookup(S_return.ENV, $ptascii(' + json.dumps(case['other_name']) + ')) = (n_other_formal)',
        'S_return.GLOBALTABLE = (psymboltable_caller)',
        '$lookup(psymboltable_caller.ENV, $ptascii(' + json.dumps(case['other_actual_name']) + ')) = (n_other_caller)',
        'S_return.STORE[n_other_formal] = DEFINED pvalue_other',
        'S_return.STORE[n_other_caller] = DEFINED pvalue_other',
        'S_pre.STORE[n_other_caller] = DEFINED pvalue_other',
        'n_other_formal =/= n_other_caller', 'n_other_formal =/= n_formal',
        '~(n_other_formal <- S_return.REFCELLS)',
        '~((HCELL n_other_formal) <- S_pre.ALLOCATIONS)',
        '$typed_parameter_conversion(S_return, psparam_other, pvalue_other) = TYPEVALUE pvalue_other']
    if case['other_value_kind'] == 'integer':
        lines += ['pvalue_other = PINT ' + str(case['other_integer'])]
    else:
        lines += ['pvalue_other = PARRAY n_other_root', 'n_other_caller = n_caller',
            'n_other_root =/= n_root',
            '$entry_lookup(S_return.ARRAYS[n_other_root].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 5))']
    last = 'expression_actual' if case['iterable_index'] == 1 else 'expression_other'
    lines += ['$call_argument_origin(S_pre, (porigin_call), 0) = (PORIGIN n_unit pcpath_producer_call)',
        'porigin_last = PORIGIN n_unit (pcpath_producer_call ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1])',
        '$origin_node(S_pre.SOURCES, porigin_last) = (' + last + ')',
        '$expression_line(' + last + ') = ' + str(case['last_actual_source_line']),
        '$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, ' + last + ') = ' + str(case['expected_notice_line']),
        '$reference_notice_producer_line(S_pre, (PORIGIN n_unit pcpath_producer_call), NExprFuncCall phpType19_producer phpType6_producer metadata_producer) = ' + str(case['expected_notice_line']),
        '$ir_output(S_pre.EVENTS) = $ptascii(' + json.dumps(case['native_stdout'].split('H:', 1)[0]) + ')']
    return lines


def completed(case):
    lines = prior.completed(case)
    if case.get('receive_priority_control'):
        return lines
    lines += ['perrorcall.LINE = ' + str(case['expected_notice_line']),
        r'n_private =/= n_other_caller /\ n_private =/= n_other_formal',
        '$propref_at(S_full.PROPREFS, n_other_caller) = eps',
        '$reference_coercion_at(S_full.REFCOERCIONS, n_other_caller) = eps']
    if case['other_value_kind'] == 'integer':
        lines += ['S_full.STORE[n_other_caller] = DEFINED (PINT ' + str(case['other_integer']) + ')']
    else:
        lines += ['S_full.STORE[n_other_caller] = DEFINED (PARRAY n_other_current)',
            '$entry_lookup(S_full.ARRAYS[n_other_current].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 23))',
            '$lookup(S_full.ENV, $ptascii("copy")) = (n_outside_copy)',
            'S_full.STORE[n_outside_copy] = DEFINED (PARRAY n_other_root)',
            '$entry_lookup(S_full.ARRAYS[n_other_root].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 5))']
    return lines


def controls(case):
    if case.get('receive_priority_control'):
        return prior.controls(case)
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, '
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    for which, ref in (('psparam', case['formal_byref']), ('psparam_other', case['other_byref'])):
        wrong = 'array' if which == 'psparam' or case['other_kind'] == 'iterable' else 'bool'
        for edit in ('REQUIRED = false', 'VARIADIC = true', 'BYREF = ' + str(not ref).lower(),
                'DEFAULT = PSDEFAULTUNSUPPORTED "forged multi iterable default"', 'TYPE = ' + branches([wrong])):
            selected, other = ('psparam[.' + edit + ']', 'psparam_other') if which == 'psparam' else ('psparam', 'psparam_other[.' + edit + ']')
            lines += ['~' + header + signature + '[.PARAMETERS = ' + vector(case, selected, other) + '])']
    raw = '(NIdentifier (BYTES text_formal) metadata_formal)'
    for shape, members in (('(NNullableType ' + raw + ' metadata_formal)', ['iterable', 'null']),
            ('(NUnionType (SEQUENCE ([NIdentifier (BYTES "bnVsbA==") metadata_formal, ' + raw + '])) metadata_formal)', ['null', 'iterable'])):
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) ' + shape + ' (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        lines += ['$reference_notice_producer_arguments(phpType6_producer, SEQUENCE (' + vector(case, parameter, 'phpType17_other') + '), ' + signature + '[.RETURNS = eps][.PARAMETERS = ' + vector(case, 'psparam[.TYPE = ' + branches(members) + ']', 'psparam_other') + '])']
    lines += ['~$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual]), phpType16, ' + signature + '[.RETURNS = eps])',
        '~' + header + signature + '[.RETURNS = ' + branches(['iterable', 'null']) + '])']
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, provenance]
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
            specs.append('dec $ir_case' + str(index) + '() : bool\ndef $ir_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $ir_case' + str(index) + '()\n' for index in range(len(cases))))
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
    print('multi-cv-iterable-formal-front' if args.front else 'multi-cv-iterable-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

#!/usr/bin/env python3
"""Check Builtin iterable returns, exact object/callable/numeric values and private-cell cleanup."""
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
import singleton_cv_union_int_iterable_return_producer_reference_notice_review_state as single
import multi_cv_union_int_iterable_return_producer_reference_notice_review_state as multi
import cv_union_float_iterable_return_producer_reference_notice_review_state as floating

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_builtin_union_iterable_return_producer_reference_notice_review_cases.json')
PREFIX, branches, raw = single.PREFIX, single.branches, single.raw


def basis(case):
    return single if case['cv_arity'] == 1 else multi


def template(case):
    return dict(case, value_kind='int')


def value(case):
    return '(POBJECT n_old)' if case['value_kind'] == 'object' else 'pvalue_input'


def indexed_return(lines, case):
    result = []
    for line in lines:
        if line.startswith('phpType18 = NUnionType '):
            atoms = ['NIdentifier (BYTES text_return_' + str(i) + ') metadata_return_' + str(i) for i in range(len(case['return_members']))]
            result.append('phpType18 = NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_union')
            result += ['$ptlc($base64(text_return_' + str(i) + ')) = $ptascii(' + json.dumps(kind) + ')' for i, kind in enumerate(case['return_members'])]
        elif line.startswith(('$ptlc($base64(text_first))', '$ptlc($base64(text_second))')):
            continue
        else:
            result.append(line)
    return result


def reached(case, front):
    if case['value_kind'] == 'float':
        lines = floating.reached(case, front)
        lines += ['pvalue_string = PSTRING_CARRIER INTERNED_STRING ($ptascii("17.5"))',
            'S_checked = S_resolved[.RESULT = KNOWN (PFLOAT ' + str(case['return_float_bits']) + ')]']
        return indexed_return(lines, case)
    lines = basis(case).reached(template(case), front)
    lines = [line.replace('(PINT 17)', value(case)).replace('pvalue_string', 'pvalue_input') for line in lines]
    original = ('POBJECT n_old' if case['value_kind'] == 'object' else
        'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(case['value_name']) + '))')
    ordered = []
    for line in lines:
        if line in ('S_resolved.RESULT = KNOWN pvalue_input', '$string_bytes(pvalue_input) = ($ptascii("17"))'):
            continue
        ordered.append(line)
        if line == 'S_resolved = $resolve_at(S_return, S_return.RESULT, z_return)':
            ordered += ['S_resolved.RESULT = KNOWN pvalue_input', 'pvalue_input = (' + original + ')']
    lines = ordered
    lines += ['S_checked = S_resolved']
    for strict in ('false', 'true'):
        lines.append('$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', pvalue_input, ' + strict + ') = TYPEVALUE pvalue_input')
    if case['value_kind'] == 'object':
        lines += ['$objectprops_at(S_pre.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 13)))}])',
            '$named_reference_notice_object(S_pre, pvalue_input)']
    else:
        lines += ['$typed_registered(S_resolved, $ptascii(' + json.dumps(case['value_name']) + '))',
            '$typed_callable(S_resolved, pvalue_input) = (true)', '$typed_callable(S_pre, pvalue_input) = (true)',
            '$string_carrier_valid(S_pre, pvalue_input)']
    return indexed_return(lines, case)


def completed(case):
    if case['value_kind'] == 'float':
        return floating.completed(case)
    lines = basis(case).completed(template(case))
    lines = [line.replace('(PINT 17)', value(case)).replace('pvalue_string', 'pvalue_input') for line in lines]
    if case['value_kind'] == 'object':
        lines = [line.replace('$node_children(S_notice, HCELL n_private) = eps', '$node_children(S_notice, HCELL n_private) = [HOBJECT n_old]') for line in lines]
        lines += ['$objectprops_at(S_full.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 37)))}])',
            '$heap_owners($heap_graph(S_full), HOBJECT n_old) = 1']
    else:
        lines.append('$string_carrier_valid(S_full, pvalue_input)')
    return lines


def raw_members(members):
    return '[' + ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_union' for kind in members) + ']'


def controls(case):
    lines = basis(case).controls(template(case))
    if case['value_kind'] != 'object':
        return lines
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    fold = '$reference_notice_producer_iterable_return_union_members('
    valid = [['iterable', 'object'], ['object', 'iterable'], ['iterable', 'callable'], ['callable', 'iterable'],
        ['iterable', 'int', 'float'], ['float', 'int', 'iterable']]
    valid += [['iterable', 'object', 'callable', 'int', 'float', boolean, 'string', 'null'] for boolean in ('bool', 'false', 'true')]
    invalid = [['iterable', 'array'], ['array', 'iterable'], ['iterable', 'array', 'string'],
        ['iterable', 'iterable', 'int'], ['iterable', 'int', 'int'], ['iterable', 'bool', 'false'],
        ['iterable', 'false', 'true'], ['iterable', 'mixed'], ['iterable', 'void', 'int'], ['iterable', 'never', 'int']]
    for members in valid + invalid:
        mark = '' if members in valid else '~'
        raw = raw_members(members)
        lines += [mark + fold + raw + ', ' + branches(members) + ', eps)',
            mark + header + 'NUnionType (SEQUENCE (' + raw + ')) metadata_union, ' + signature + '[.RETURNS = ' + branches(members) + '])']
    for members in (['object', 'callable'], ['int', 'string', 'null']):
        lines.append('~' + fold + raw_members(members) + ', ' + branches(members) + ', eps)')
    lines += ['~' + fold + 'eps, eps, eps)',
        '~' + fold + raw_members(['iterable', 'int', 'float']) + ', ' + branches(['iterable', 'float', 'int']) + ', eps)',
        '~' + fold + raw_members(['iterable', 'int', 'float']) + ', ' + branches(['iterable', 'int']) + ', eps)',
        '~' + fold + raw_members(['iterable', 'int']) + ', ' + branches(['iterable', 'int', 'float']) + ', eps)',
        'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter']
    for members in (['iterable', 'object'], ['iterable', 'callable'], ['iterable', 'int', 'float']):
        raw = 'NUnionType (SEQUENCE (' + raw_members(members) + ')) metadata_union'
        formal = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        lines.append('~$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + formal + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + branches(members) + ']]])')
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
    paths = [Path(__file__), Path(single.__file__), Path(multi.__file__), Path(single.base.__file__), Path(floating.__file__), CATALOGUE, provenance]
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
    print('cv-builtin-union-iterable-return-front' if args.front else 'cv-builtin-union-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

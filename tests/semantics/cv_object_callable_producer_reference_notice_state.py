#!/usr/bin/env python3
"""Reach exact object/callable reception, real object edges and private Notice cells."""
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
import cv_int_callable_producer_reference_notice_state as prior
import cv_string_callable_producer_reference_notice_state as string_prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_object_callable_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('86', '91')
branches, raw = string_prior.branches, string_prior.raw


def reached(case, front):
    adapted = dict(case, value_kind='integer' if case['value_kind'] == 'object' else 'callable')
    lines = prior.reached(adapted, front)
    if case['value_kind'] == 'object':
        lines = [line.replace('pvalue_original = PINT 17', 'pvalue_original = POBJECT n_object') for line in lines]
        lines += ['S_pre.OBJECTS[n_object] = STDINSTANCE',
            '$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops_pre)',
            'pobjectprops_pre.MATERIALIZED',
            'pobjectprops_pre.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PINT 17)))}]',
            '$named_reference_notice_object(S_pre, pvalue_original)',
            '$node_children(S_pre, HOBJECT n_object) = eps',
            '$task_nodes(RETURN_UNWIND (KNOWN pvalue_original) porigin_return?) = [HOBJECT n_object]']
    return lines


def completed(case):
    adapted = dict(case, value_kind='integer' if case['value_kind'] == 'object' else 'callable')
    lines = prior.completed(adapted)
    if case['value_kind'] == 'object':
        lines = [line.replace('$named_reference_notice_root_value(S_pre, pvalue_original)', '$named_reference_notice_object(S_pre, pvalue_original)')
            .replace('$node_children(S_notice, HCELL n_private) = eps', '$node_children(S_notice, HCELL n_private) = [HOBJECT n_object]') for line in lines]
        lines += ['$node_children(S_resume, HCELL n_private) = [HOBJECT n_object]',
            'S_resume.OBJECTPROPS = S_pre.OBJECTPROPS',
            'S_resume.OBJECTS[n_object] = STDINSTANCE',
            '$node_children(S_full, HCELL n_private) = eps']
    return lines


def controls(case):
    lines = [line for line in string_prior.controls(case) if not line.startswith('$typed_conversion_at(')]
    for members in (['callable', 'object'], ['object', 'callable']):
        normalized = branches(members)
        lines += ['$ptmasks(' + normalized + ') = [' + ', '.join(json.dumps(kind) for kind in members) + ']']
        for strict in ('false', 'true'):
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original']
            for value in ('PNULL', 'PBOOL false', 'PBOOL true', 'PINT 0', 'PINT 17', 'PFLOAT $float_of_int(2)', 'PSTRING eps', 'PSTRING ($ptascii("17"))', 'PSTRING ($ptascii("notRegistered91"))'):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEREJECT']
            if case['value_kind'] == 'object':
                lines += ['$typed_exact(' + normalized + ', pvalue_original)',
                    '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps][.CLASSES = eps], ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original']
            else:
                for field in ('CALLABLES', 'FUNCTIONS'):
                    lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', pvalue_original, ' + strict + ') = TYPEREJECT']
        atoms = ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_first' for kind in members)
        changed = 'NUnionType (SEQUENCE ([' + atoms + '])) metadata_union_return'
        lines += ['$reference_notice_producer_header(phpType6_producer, phpType16, ' + changed + ', pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
    if case['value_kind'] == 'object':
        lines += ['~$named_reference_notice_object(S_pre[.OBJECTPROPS = eps], pvalue_original)',
            '~$named_reference_notice_object(S_pre[.ALLOCATIONS = eps], pvalue_original)',
            '~$named_reference_notice_object(S_pre, POBJECT (|S_pre.OBJECTS|))']
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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.union_prior.__file__), Path(string_prior.__file__), CATALOGUE, provenance]
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
            specs.append('dec $cn_case' + str(index) + '() : bool\ndef $cn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cn_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-object-callable-front' if args.front else 'cv-object-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

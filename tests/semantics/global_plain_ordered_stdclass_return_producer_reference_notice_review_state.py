#!/usr/bin/env python3
"""Ground ordered bare-class BOOL/STRING returns and named private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import global_plain_union_float_stdclass_return_producer_reference_notice_review_state as previous
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_ordered_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = '\n'.join(line for line in previous.PREFIX.splitlines() if not line.startswith('  -- if S.RESULT = KNOWN (PFLOAT')) + '\n'
PREFIX = PREFIX.replace('F:29:17:1;', 'F:29::1;')


def encoded(text):
    return json.dumps(base64.b64encode(text.encode()).decode())


def normalized(kinds, name='stdClass'):
    return '[' + ', '.join('(PTBRANCH ([PTCLASS ($base64(' + encoded(name) + '))]))' if kind == 'class' else '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in kinds) + ']'


def raw_members(kinds, name='stdClass', tag='NName', dynamic=False, spellings=None):
    nodes = []
    for index, kind in enumerate(kinds):
        field = 'class' if kind == 'class' else str(index)
        text = 'text_return_' + field if dynamic else encoded(name if kind == 'class' else (spellings[index] if spellings else kind.upper()))
        metadata = 'metadata_return_' + field if dynamic else 'eps'
        nodes.append((tag if kind == 'class' else 'NIdentifier') + ' (BYTES ' + text + ') ' + metadata)
    return '[' + ', '.join(nodes) + ']'


def raw_union(kinds, name='stdClass', tag='NName', dynamic=False, spellings=None):
    return 'NUnionType (SEQUENCE (' + raw_members(kinds, name, tag, dynamic, spellings) + ')) ' + ('metadata_return_union' if dynamic else 'eps')


def normal(initial, case, index, front):
    compatibility = dict(case, return_kind='float', return_class_first=index == 0,
        value_bits=4625478292286210048 if index == 0 else 4630404104378646528)
    old, _ = previous.normal(initial, compatibility, index, front)
    result = '(PBOOL false)' if index == 0 else 'pvalue_saved'
    reached = []
    for line in old:
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case['return_members'], case['class_return']) + r' /\ ~pfunction_producer.SIGNATURE.BYREF'
        if line.startswith('phpType18_return = '):
            line = 'phpType18_return = ' + raw_union(case['return_members'], case['class_return'], dynamic=True)
            reached.append(line)
            for position, kind in enumerate(case['return_members']):
                field = 'class' if kind == 'class' else str(position)
                if kind == 'class':
                    reached.append('$base64(text_return_class) = $base64(' + encoded(case['class_return']) + ')')
                else:
                    reached.append('$ptlc($base64(text_return_' + field + ')) = $ptascii(' + json.dumps(kind) + ')')
            continue
        if line.startswith(('$base64(text_return_class)', '$ptlc($base64(text_return))')):
            continue
        if line.startswith('S_return.RESULT = '):
            line = 'S_return.RESULT = KNOWN ' + result if index == 0 else line
        if line.startswith('$resolve_at(S_return,') and index == 0:
            line = '$resolve_at(S_return, S_return.RESULT, z_return) = S_return'
        if line.startswith('$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS,'):
            line = '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, ' + result + ', false) = TYPEVALUE ' + result
        if line.startswith('$typed_return_value(S_return,'):
            line = '$typed_return_value(S_return, z_return) = S_return[.RESULT = KNOWN ' + result + ']'
        for start in ('S_pre.RESULT = KNOWN ', 'S_notice.STORE[n_private] = DEFINED ', 'S_resume.STORE[n_private] = DEFINED '):
            if line.startswith(start):
                line = start + result
        reached.append(line)
        if index == 1:
            for state in ('S_pre', 'S_notice', 'S_resume'):
                if line == (state + '.RESULT = KNOWN ' + result if state == 'S_pre' else state + '.STORE[n_private] = DEFINED ' + result):
                    reached.append('$string_carrier_valid(' + state + ', pvalue_saved)')
    if front:
        return reached, []
    actuals = 'SEQUENCE ([phpType7_first, phpType7_last])'
    parameters = 'SEQUENCE ([phpType17_first, phpType17_last])'
    header = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, ' + actuals + ', ' + parameters + ', '
    def proof(kinds, name='stdClass', tag='NName', normalized_kinds=None):
        return header + raw_union(kinds, name, tag) + ', pfunction_producer.SIGNATURE[.RETURNS = ' + normalized(kinds if normalized_kinds is None else normalized_kinds, name) + '])'
    derived = ['~$error_call_valid(S_notice, perrorcall[.LINE = 10])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    valid = [(kind, 'class') if first else ('class', kind) for kind in ('int', 'null', 'float', 'bool', 'string', 'array', 'false', 'true', 'iterable', 'callable') for first in (False, True)]
    valid += [('bool', 'class', 'string'), ('int', 'float', 'class'),
        ('iterable', 'class', 'string', 'bool'), ('array', 'int', 'class', 'float', 'string', 'null', 'bool', 'callable'),
        ('int', 'iterable', 'float', 'class', 'string', 'null', 'false', 'callable')]
    for name in ('stdClass', 'STDCLASS', 'sTdClAsS'):
        for kinds in valid:
            good = proof(kinds, name)
            derived += [good, proof(kinds, name, 'NNameFullyQualified'),
                '$reference_notice_producer_global_union_view(' + raw_members(kinds, name) + ', false) = (' + raw_members(kinds, name, 'NNameFullyQualified') + ')',
                '$reference_notice_producer_global_union_view(' + raw_members(kinds, name, 'NNameFullyQualified') + ', false) = eps',
                '~' + good.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
                '~' + good.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]],', 1),
                '~' + proof(kinds, name, normalized_kinds=kinds[::-1])]
    for kinds in [('class', 'object'), ('class', 'mixed'), ('class', 'void'), ('class', 'never'),
            ('class', 'bool', 'false'), ('class', 'false', 'true'), ('class', 'int', 'int'), ('class', 'iterable', 'array')]:
        derived.append('~' + proof(kinds))
    for kinds, name, tag in [(('bool', 'string'), 'stdClass', 'NName'), (('class', 'class'), 'stdClass', 'NName'),
            (('class', 'bool'), 'Other', 'NName'), (('class', 'bool'), 'stdClass', 'NNameRelative'),
            (('class', 'bool'), 'stdClass', 'NIdentifier')]:
        derived.append('$reference_notice_producer_global_union_view(' + raw_members(kinds, name, tag) + ', false) = eps')
    derived += ['$reference_notice_producer_global_union_view(eps, false) = eps',
        '$reference_notice_producer_global_union_view(eps, true) = (eps)',
        'S_zero = $drive(S_notice, 0)', r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)']
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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(previous.__file__), Path(previous.previous.__file__), Path(previous.previous.prior.__file__), Path(previous.retained.__file__), CATALOGUE, provenance]
    specs, reached, derived = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:2]):
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
            conditions, extra = normal(initial, case, index, args.front)
            specs.append('dec $gpic_case' + str(index) + '() : bool\ndef $gpic_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
            reached += conditions
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $gpic_case0()\n  -- if $gpic_case1()\n')
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases[:2]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-ordered-stdclass-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

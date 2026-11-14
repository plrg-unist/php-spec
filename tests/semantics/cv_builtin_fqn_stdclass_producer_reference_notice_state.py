#!/usr/bin/env python3
"""Ground strict class/builtin reception and quiet stdClass Notice ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import multi_cv_scalar_formal_producer_reference_notice_state as scalar
import cv_union_fqn_stdclass_producer_reference_notice_state as objects
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_builtin_fqn_stdclass_producer_reference_notice_cases.json')
PREFIX = scalar.PREFIX.replace('MultiCvScalarFormalString57', 'StrictBuiltinFqnStdClass80')
PREFIX += objects.PREFIX.replace('SingletonUnionFqnStdClass79', 'SingletonBuiltinFqnStdClass80')


def normalized(kind, class_first, name='sTdClAsS'):
    members = ['(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))]))',
        '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))']
    return '[' + ', '.join(members if class_first else members[::-1]) + ']'


def raw_union(kind, class_first, name='sTdClAsS', field=None):
    encoded = lambda value: '"' + base64.b64encode(value.encode()).decode() + '"'
    class_text, builtin_text = (encoded(name), encoded(kind)) if field is None else ('text_' + field + '_class', 'text_' + field + '_builtin')
    metadata = lambda member: 'metadata_function' if field is None else 'metadata_' + field + '_' + member
    members = ['NNameFullyQualified (BYTES ' + class_text + ') ' + metadata('class'),
        'NIdentifier (BYTES ' + builtin_text + ') ' + metadata('builtin')]
    return 'NUnionType (SEQUENCE ([' + ', '.join(members if class_first else members[::-1]) + '])) ' + metadata('union')


def scalar_front(case):
    lines = scalar.front_lines(1, case)
    result = []
    for line in lines:
        for field, kind, first in zip(('first', 'last'), case['formal_kinds'], case['formal_class_first']):
            if line.startswith('phpType17_' + field + ' = NParam'):
                line = line.replace('(NIdentifier (BYTES text_' + field + '_type) metadata_' + field + '_type)', '(' + raw_union(kind, first, field=field) + ')')
            if line.startswith('psparam_' + field + '.TYPE ='):
                line = 'psparam_' + field + '.TYPE = ' + normalized(kind, first)
            line = line.replace('text_' + field + '_type', 'text_' + field + '_builtin')
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS ='):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized('int', True, 'stdClass') + r' /\ ~pfunction_producer.SIGNATURE.BYREF'
        if line.startswith('phpType18_return ='):
            line = 'phpType18_return = ' + raw_union('int', True, field='return')
        if line.startswith('$ptlc($base64(text_return)) ='):
            line = line.replace('text_return', 'text_return_builtin')
        if line.startswith('~$typed_caller_strict('):
            line = line[1:]
        if line.startswith('pvalue_saved ='):
            line = 'pvalue_saved = PINT 37'
        if line == '$string_carrier_valid(S_receive_last, pvalue_saved)':
            continue
        line = line.replace('= TYPESTRING (PINT 37)', '= TYPEVALUE (PINT 37)')
        result.append(line)
    result += ['pfunction_producer.CODE.STRICT',
        '$base64(text_first_class) = $ptascii("sTdClAsS")',
        '$base64(text_last_class) = $ptascii("sTdClAsS")',
        '$base64(text_return_class) = $ptascii("stdClass")']
    return result


def object_front(case):
    prior_case = dict(class_formals=['sTdClAsS'], class_return='StDcLaSs', class_first=True)
    lines = objects.front_lines(0, prior_case)
    result = []
    for line in lines:
        line = line.replace('SingletonUnionFqnStdClass79', 'SingletonBuiltinFqnStdClass80')
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS ='):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized('string', False, 'StDcLaSs')
        if line.startswith('~psparam.BYREF /\\ psparam.TYPE ='):
            line = r'~psparam.BYREF /\ psparam.TYPE = ' + normalized('array', True)
        result.append(line)
    result += ['phpType18_parameter = ' + raw_union('array', True, field='parameter'),
        '$base64(text_parameter_class) = $ptascii("sTdClAsS")',
        '$ptlc($base64(text_parameter_builtin)) = $ptascii("array")',
        'phpType18 = ' + raw_union('string', False, field='return'),
        '$base64(text_return_class) = $ptascii("StDcLaSs")',
        '$ptlc($base64(text_return_builtin)) = $ptascii("string")']
    return result


def controls(index):
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    for first in (False, True):
        for strict in ('false', 'true'):
            for kind, boolean in (('false', 'false'), ('true', 'true')):
                norm = normalized(kind, first)
                lines += ['$typed_conversion_at(S_return, ' + norm + ', PBOOL ' + boolean + ', ' + strict + ') = TYPEVALUE (PBOOL ' + boolean + ')']
                for bad in ('PINT 0', 'PBOOL ' + ('true' if boolean == 'false' else 'false'), 'PNULL'):
                    lines += ['$typed_conversion_at(S_return, ' + norm + ', ' + bad + ', ' + strict + ') = TYPEREJECT']
            lines += ['$typed_conversion_at(S_return, ' + normalized('float', first) + ', PINT 17, ' + strict + ') = TYPEVALUE (PFLOAT 4625478292286210048)',
                '$typed_conversion_at(S_return, ' + normalized('int', first) + ', PINT 37, ' + strict + ') = TYPEVALUE (PINT 37)']
            if index == 1:
                for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'false', 'true'):
                    lines += ['$typed_conversion_at(S_return, ' + normalized(kind, first) + ', POBJECT n_object, ' + strict + ') = TYPEVALUE (POBJECT n_object)']
    if index == 1:
        header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
        signature = 'pfunction_producer.SIGNATURE'
        for first in (False, True):
            for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'false', 'true'):
                norm, raw = normalized(kind, first), raw_union(kind.upper(), first)
                lines += [header + raw + ', ' + signature + '[.RETURNS = ' + norm + '])',
                    '~' + header + raw + ', ' + signature + '[.RETURNS = ' + normalized(kind, not first) + '])']
        for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged class/builtin default"'):
            lines += ['~$reference_notice_producer_arguments(phpType6_producer, phpType16, ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]])']
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
    paths = [Path(__file__), Path(scalar.__file__), Path(objects.__file__), Path(objects.prior.__file__),
        Path(objects.compatibility.__file__), ROOT / 'tests/semantics/cv_fqn_stdclass_producer_reference_notice_state.py', CATALOGUE, provenance]
    specs, reached, derived = [], [], []
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
            current = [initial] + (scalar_front(case) if index == 0 else object_front(case))
            extra = []
            if not args.front:
                current = [line.removeprefix('~') if line.startswith(('~$reference_notice_producer_header(', '~$reference_notice_producer_arguments(')) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in current]
                current += scalar.full_lines(1, case) if index == 0 else objects.full_lines(0, case)
                extra = controls(index)
            specs.append('dec $bfn_case' + str(index) + '() : bool\ndef $bfn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached += current
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $bfn_case0()\n  -- if $bfn_case1()\n')
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
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases[:2]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-builtin-fqn-stdclass-front' if args.front else 'cv-builtin-fqn-stdclass-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

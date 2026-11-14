#!/usr/bin/env python3
"""Ground one-class larger unions on quiet stdClass and retained array producers."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_union_fqn_stdclass_producer_reference_notice_state as objects
import multi_cv_union_array_return_producer_reference_notice_state as arrays
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_primitive_fqn_stdclass_producer_reference_notice_cases.json')
PREFIX = objects.PREFIX.replace('SingletonUnionFqnStdClass79', 'SingletonPrimitiveFqnStdClass81')
PREFIX += arrays.PREFIX.replace('MultiCvUnionArray53', 'ArrayPrimitiveFqnStdClass81')


def normalized(members, name='sTdClAsS'):
    class_bytes = '[' + ', '.join(map(str, name.encode())) + ']' if '\x00' in name else '$ptascii(' + json.dumps(name) + ')'
    return '[' + ', '.join('(PTBRANCH ([PTCLASS (' + class_bytes + ')]))' if kind == 'stdClass' else '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw_union(members, name='sTdClAsS', field=None, class_tag='NNameFullyQualified'):
    nodes = []
    for index, kind in enumerate(members):
        encoded = '"' + base64.b64encode((name if kind == 'stdClass' else kind.upper()).encode()).decode() + '"'
        text = encoded if field is None else 'text_' + field + '_' + str(index)
        metadata = 'metadata_function' if field is None else 'metadata_' + field + '_' + str(index)
        nodes.append((class_tag if kind == 'stdClass' else 'NIdentifier') + ' (BYTES ' + text + ') ' + metadata)
    metadata = 'metadata_function' if field is None else 'metadata_' + field + '_union'
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) ' + metadata


def type_bytes(members, name, field):
    return [('$base64(text_' + field + '_' + str(index) + ') = $ptascii(' + json.dumps(name) + ')' if kind == 'stdClass' else '$ptlc($base64(text_' + field + '_' + str(index) + ')) = $ptascii(' + json.dumps(kind) + ')') for index, kind in enumerate(members)]


def object_front(case):
    prior_case = dict(class_formals=['sTdClAsS'], class_return='StDcLaSs', class_first=True)
    lines = objects.front_lines(0, prior_case)
    result = []
    for line in lines:
        line = line.replace('SingletonUnionFqnStdClass79', 'SingletonPrimitiveFqnStdClass81')
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS ='):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case['return_members'], case['class_return'])
        if line.startswith('~psparam.BYREF /\\ psparam.TYPE ='):
            line = r'~psparam.BYREF /\ psparam.TYPE = ' + normalized(case['formal_members'][0], case['class_formals'][0])
        if line == 'pfunction_producer.CODE.STRICT':
            line = '~' + line
        result.append(line)
    result += ['phpType18_parameter = ' + raw_union(case['formal_members'][0], field='parameter'),
        'phpType18 = ' + raw_union(case['return_members'], field='return')]
    result += type_bytes(case['formal_members'][0], case['class_formals'][0], 'parameter')
    result += type_bytes(case['return_members'], case['class_return'], 'return')
    return result


def array_front(case):
    result = []
    for line in arrays.BASE + arrays.VERIFY + arrays.CONTINUE + arrays.COPY:
        if line == 'psparam_first.TYPE = eps /\\ psparam_last.TYPE = eps':
            line = 'psparam_first.TYPE = ' + normalized(case['formal_members'][0]) + r' /\ psparam_last.TYPE = eps'
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS ='):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case['return_members'], case['class_return']) + r' /\ ~pfunction_producer.SIGNATURE.BYREF'
        if line.startswith('phpType18_return ='):
            line = 'phpType18_return = ' + raw_union(case['return_members'], field='return')
        if line.startswith('$ptlc($base64(text_return_first)) ='):
            continue
        if line.startswith('$reference_notice_producer_arguments(') and '.RETURNS = eps' in line:
            line = '~' + line
        for old, new in (('ARG_OWNERS', '3'), ('FORMAL_OWNERS', '2'), ('RETURN_OWNERS', '3'), ('PRE_OWNERS', '2')):
            line = line.replace(old, new)
        result.append(line)
    result += ['~pfunction_producer.CODE.STRICT',
        'phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (' + raw_union(case['formal_members'][0], field='parameter') + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter',
        'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter',
        '$typed_conversion_at(S_return, psparam_first.TYPE, PARRAY n_root, false) = TYPEVALUE (PARRAY n_root)',
        '$mcu_output(S_pre.EVENTS) = $ptascii("A;M:17:23:0;")']
    result += type_bytes(case['formal_members'][0], case['class_formals'][0], 'parameter')
    result += type_bytes(case['return_members'], case['class_return'], 'return')
    return result


def array_full(case):
    lines = ['~((HCELL n_original_x) <- S_pre.ALLOCATIONS)', '$heap_owners($heap_graph(S_pre), HCELL n_original_x) = 0']
    lines += arrays.PRIVATE + arrays.NORMAL
    lines += ['~$named_reference_notice_array(S_written, PARRAY n_current)', '$mcu_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    return [line.replace('PRE_OWNERS', '2') for line in lines]


def controls(index, case):
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    for strict in ('false', 'true'):
        for members, value in ((['null', 'stdClass', 'array'], 'PNULL'), (['true', 'stdClass', 'array'], 'PBOOL true')):
            lines += ['$typed_conversion_at(S_return, ' + normalized(members) + ', ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
            for bad in ('PINT 0', 'PBOOL false', 'PSTRING eps'):
                lines += ['$typed_conversion_at(S_return, ' + normalized(members) + ', ' + bad + ', ' + strict + ') = TYPEREJECT']
        value = 'POBJECT n_object' if index == 0 else 'PARRAY n_root'
        lines += ['$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
    if index == 0:
        signature = 'pfunction_producer.SIGNATURE'
        header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
        variants = []
        for pair in (['array', 'null'], ['int', 'float'], ['string', 'int'], ['false', 'array'], ['true', 'null'], ['bool', 'int']):
            for position in range(3):
                members = pair[:]
                members.insert(position, 'stdClass')
                variants.append(members)
        for boolean in ('bool', 'false', 'true'):
            for position in range(7):
                members = ['array', 'int', 'float', 'string', 'null', boolean]
                members.insert(position, 'stdClass')
                variants.append(members)
        for members in variants:
            norm, raw = normalized(members), raw_union(members)
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
            proof = '$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + parameter + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + norm + ']]])'
            lines += [header + raw + ', ' + signature + '[.RETURNS = ' + norm + '])', proof,
                '~' + header + raw + ', ' + signature + '[.RETURNS = ' + normalized(members[::-1]) + '])']
        for members in (['stdClass', 'stdClass', 'int'], ['stdClass', 'bool', 'false'], ['false', 'stdClass', 'true'], ['stdClass', 'int', 'int'], ['stdClass', 'object', 'int'], ['stdClass', 'callable', 'int'], ['stdClass', 'mixed', 'null'], ['stdClass', 'void', 'null'], ['stdClass', 'never', 'null'], ['stdClass', 'iterable', 'null']):
            lines += [('' if members == ['stdClass', 'callable', 'int'] else '~') + header + raw_union(members) + ', ' + signature + '[.RETURNS = ' + normalized(members) + '])']
        members = ['int', 'stdClass', 'float']
        for tag in ('NName', 'NNameRelative', 'NIdentifier'):
            lines += ['~' + header + raw_union(members, class_tag=tag) + ', ' + signature + '[.RETURNS = ' + normalized(members) + '])']
        lines += ['~' + header + raw_union(members) + ', ' + signature + '[.RETURNS = ' + normalized(members, 'STDCLASS') + '])',
            '~' + header + raw_union(members) + ', ' + signature + '[.RETURNS = ' + normalized(members + ['null']) + '])']
        for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00'):
            lines += ['~' + header + raw_union(members, name=name) + ', ' + signature + '[.RETURNS = ' + normalized(members, name) + '])']
        for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged larger class union default"'):
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
    paths = [Path(__file__), Path(objects.__file__), Path(objects.prior.__file__), Path(objects.compatibility.__file__),
        ROOT / 'tests/semantics/cv_fqn_stdclass_producer_reference_notice_state.py', Path(arrays.__file__), CATALOGUE, provenance]
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
            current = [initial] + (object_front(case) if index == 0 else array_front(case))
            extra = []
            if not args.front:
                current = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in current]
                current += objects.full_lines(0, case) if index == 0 else array_full(case)
                extra = controls(index, case)
            specs.append('dec $pfn_case' + str(index) + '() : bool\ndef $pfn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $pfn_case0()\n  -- if $pfn_case1()\n')
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
    print('cv-primitive-fqn-stdclass-front' if args.front else 'cv-primitive-fqn-stdclass-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

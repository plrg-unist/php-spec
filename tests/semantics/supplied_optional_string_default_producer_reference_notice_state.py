#!/usr/bin/env python3
"""Ground string defaults with authentic weak reception and live default identity."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import supplied_optional_int_default_producer_reference_notice_state as integer
import supplied_optional_float_default_producer_reference_notice_state as floating

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('supplied_optional_string_default_producer_reference_notice_cases.json')


def namespaces(text):
    return (text.replace('SingletonScalarFormal59', 'StringDefault145')
        .replace('UntypedArrayReturnProducer35', 'StringArrayDefault145'))


PREFIX = namespaces(floating.PREFIX)


def default_parts(case):
    encoded = json.dumps(base64.b64encode(case['default'].encode()).decode())
    return '(NScalarString (BYTES ' + encoded + ') metadata_default)'


def replacements(case, lines):
    default = default_parts(case)
    return [namespaces(line.replace(integer.DEFAULT, default)
        .replace('PSDEFAULT ' + default + ' "int"', 'PSDEFAULT ' + default + ' "string"')
        .replace('U;V:3;M:17;', 'U;V:3:0;M:17;')) for line in lines]


def front_lines(case, front):
    kind = case['kind']
    if kind == 'invalid':
        return ['S_initial.COMPLETION = STATICBYTES ($ptascii("Cannot use string as default value for parameter $input of type int")) 2',
            'S_initial.EVENTS = eps']
    lines = replacements(case, integer.front_lines(case, front))
    if kind == 'omitted':
        return [line.replace('psparam_default.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
            'psparam_default.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]') for line in lines]
    if kind == 'singleton':
        result = []
        for line in lines:
            if line in ('$string_carrier_valid(S_args, pvalue_original)', '$string_carrier_valid(S_pre, pvalue_original)'):
                continue
            line = line.replace('pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))', 'pvalue_original = PINT 17')
            line = line.replace('psparam.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]', 'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]')
            line = line.replace('$ptlc($base64(text_type)) = $ptascii("int")', '$ptlc($base64(text_type)) = $ptascii("string")')
            line = line.replace('= TYPEINTEGER pvalue_original', '= TYPESTRING pvalue_original')
            line = line.replace('S_received.STORE[n_formal] = DEFINED (PINT 17)', 'S_received.STORE[n_formal] = DEFINED pvalue_received')
            line = line.replace('S_return.STORE[n_formal] = DEFINED (PINT 17)', 'S_return.STORE[n_formal] = DEFINED pvalue_received')
            result.append(line)
        lines = result + ['pvalue_received = PSTRING_CARRIER (REQUEST_STRING n_received_string) ($ptascii("17"))',
            '$string_carrier_valid(S_received, pvalue_received)',
            'n_received_string = |S_receive.STRINGDATA|',
            'S_received.STRINGDATA = S_receive.STRINGDATA ++ [$ptascii("17")]']
    else:
        lines += ['phpType16 = SEQUENCE ([phpType17])']
    lines += ['~$reference_notice_producer_arguments(phpType6_producer, phpType16_producer, pfunction_producer.SIGNATURE)']
    return lines


def full_lines(case):
    lines = replacements(case, integer.full_lines(case))
    if case['kind'] == 'singleton':
        lines = [line for line in lines if line != '$string_carrier_valid(S_full, pvalue_original)']
    return lines


def controls(case):
    return replacements(case, integer.controls(case))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native, cases = json.loads(native_path.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths = [CATALOGUE, native_path] + sorted({Path(module.__file__).absolute() for module in sys.modules.values()
        if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    frontend = adapter = None
    specs, reached, derived = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == case['native_exit'] and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == case['native_stderr'].replace('{source}', str(source)).encode()
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked_value = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked_value['ok'] and checked_value['fixture']
            current = ['S_initial = $php_run(' + checked_value['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + front_lines(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += full_lines(case)
            specs.append('dec $string_default_case' + str(index) + '() : bool\ndef $string_default_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $string_default_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('supplied-optional-string-default-front' if args.front else 'supplied-optional-string-default-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

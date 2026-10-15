#!/usr/bin/env python3
"""Reached scalar reception, immutable input authority and API trace values."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

import class_constant_call_protocol as common
import error_handler_run as recorder
import global_constant_scalar_name_sources as sources
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
sha = sources.family.sha
text = lambda value: '$ptascii(' + json.dumps(value) + ')'

PREFIX = r"""
dec $test_scalar_front(pstate, pintrinsic, pvalue) : bool
def $test_scalar_front(S, pintrinsic, pvalue) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
def $test_scalar_front(S, pintrinsic, pvalue) = false -- otherwise
dec $test_scalar_seek(pstate, pintrinsic, pvalue, nat) : pstate
def $test_scalar_seek(S, pintrinsic, pvalue, 0) = S
def $test_scalar_seek(S, pintrinsic, pvalue, n) = S
  -- if $(n > 0)
  -- if $test_scalar_front(S,pintrinsic,pvalue) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_scalar_seek(S, pintrinsic, pvalue, n) = $test_scalar_seek($drive_steps($test_running(S),1),pintrinsic,pvalue,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_scalar_front(S,pintrinsic,pvalue)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, kind, value):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_scalar_seek(' + start + ',' + kind + ',' + value + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_scalar_front(' + state + ',' + kind + ',' + value + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = ' + kind, call + '.SENT = [NAMED_SENT (KNOWN (' + value + '))]',
        call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_constant_call(' + call + ')',
        '$dynamic_scalar_constant_valid(' + state + ',' + call + ')', *common.public(state)]


def weak(state, value, query, result):
    call, converted, after = 'pconfigcall_' + state, state + '_converted', state + '_value'
    values = ['~$config_strict(' + state + ',' + call + ')',
        '$config_conversion(' + state + ',' + call + ',' + value + ') = TYPESTRING (' + value + ')',
        converted + ' = $typed_apply(' + state + ',TYPESTRING (' + value + '),' + call + '.LINE)',
        converted + '.COMPLETION = NORMAL', converted + '.RESULT = KNOWN pvalue_' + converted,
        '$string_bytes(pvalue_' + converted + ') = (' + text(query) + ')',
        '$string_carrier_valid(' + converted + ',pvalue_' + converted + ')',
        *common.step(after, state, result), after + '.TODO = ptask_' + state + '*',
        after + '.BASE = BASE_VALUE (KNOWN PNULL)', after + '.STRINGDATA = ' + converted + '.STRINGDATA']
    values += [after + '.' + field + ' = ' + state + '.' + field for field in (
        'STORE', 'ENV', 'USERCONSTANTS', 'ARRAYS', 'OBJECTS', 'OBJECTPROPS', 'REFCELLS',
        'ALLOCATIONS', 'SELECTEDCALLS', 'SOURCES', 'POOLS', 'FILES', 'STATICS')]
    return values


def error(state, source, api, kind, argument, message):
    call = 'pconfigcall_' + source
    n, throwable = 'n_error_' + state, 'pthrowable_' + state
    trace, frame, args = 'n_trace_' + state, 'n_frame_' + state, 'n_args_' + state
    return [*common.step(state, source),
        state + '.TODO = (THROW_SEARCH ' + n + ') :: ptask_' + state + '*',
        state + '.OBJECTS[' + n + '] = THROWABLE ' + throwable,
        throwable + '.KIND = ' + json.dumps(kind), throwable + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + state + ',' + n + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + state + ',' + n + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + state + ',' + n + ',"file")) = ($call_sourcefile(' + state + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + state + ',' + n + ',"trace") = PARRAY ' + trace,
        state + '.ARRAYS[' + trace + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY ' + frame + '))]',
        '$trace_array_field(' + state + ',' + frame + ',' + text('function') + ') = PSTRING ' + text(api),
        '$trace_array_field(' + state + ',' + frame + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + state + ',' + frame + ',' + text('args') + ') = PARRAY ' + args,
        state + '.ARRAYS[' + args + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + argument + '))]',
        state + '.STORE = ' + source + '.STORE', state + '.USERCONSTANTS = ' + source + '.USERCONSTANTS',
        state + '.SELECTEDCALLS = ' + source + '.SELECTEDCALLS',
        state + '.EVENTS = ' + source + '.EVENTS', *common.public(state)]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial', 'INTRINSIC_CONSTANT', 'PINT 37')]
    if name == 'weak-scalar-name-lookups':
        values += ['pconfigcall_S.SELECTION = eps', 'pconfigcall_S.NAMED',
            '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression,false,preqbytes?,porigin_argument,z))',
            '$compiled_read(S,porigin_argument) = (PINT 37)', *weak('S', 'PINT 37', '37', 'PINT 137'),
            *front('S_false', 'S_value', 'INTRINSIC_DEFINED', 'PBOOL false'),
            *weak('S_false', 'PBOOL false', '', 'PBOOL false'),
            'pconfigcall_bad_value = pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (PINT 38))]]',
            '$config_invoke_valid(S,pconfigcall_bad_value)',
            '~$dynamic_scalar_constant_valid(S,pconfigcall_bad_value)',
            'S_bad_value = S[.TODO = (CONFIG_INVOKE pconfigcall_bad_value) :: ptask_S*]',
            'S_bad_value_after = $drive_steps(S_bad_value,1)',
            'S_bad_value_after.COMPLETION = UNSUPPORTED "scalar constant name reception"']
        for label, change in (
            ('site', '.SITE = PORIGIN 0 eps'), ('line', '.LINE = $(pconfigcall_S.LINE + 1)'),
            ('nonce', '.SELECTION = (0)'), ('kind', '.KIND = INTRINSIC_DEFINED')):
            values += ['~$dynamic_scalar_constant_valid(S,pconfigcall_S[' + change + '])']
        for value in ('PNULL', 'PSTRING ' + text('37'), 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_scalar_constant_call(pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (' + value + '))]])']
        values += ['~$dynamic_scalar_constant_call(pconfigcall_S[.OWNER = (0)])']
    elif name == 'captured-scalar-query-and-converted-error-arg':
        values += ['pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            '$lookup(S.ENV,' + text('call') + ') = (n_callee_cell)',
            'S.STORE[n_callee_cell] = DEFINED pvalue_callee',
            '$string_bytes(pvalue_callee) = (' + text('defined') + ')',
            *weak('S', 'PINT 37', '37', 'PINT 137'),
            *front('S_missing', 'S_value', 'INTRINSIC_CONSTANT', 'PINT 404'),
            '~$config_strict(S_missing,pconfigcall_S_missing)',
            '$lookup(S_missing.ENV,' + text('result') + ') = (n_result_cell)',
            'S_missing.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_missing_converted = $typed_apply(S_missing,TYPESTRING (PINT 404),pconfigcall_S_missing.LINE)',
            'S_missing_converted.RESULT = KNOWN pvalue_trace',
            '$string_bytes(pvalue_trace) = (' + text('404') + ')',
            '$string_carrier_valid(S_missing_converted,pvalue_trace)',
            *error('S_error', 'S_missing', 'constant', 'Error', 'pvalue_trace', 'Undefined constant "404"'),
            'S_error.STRINGDATA = S_missing_converted.STRINGDATA',
            'S_error.STORE[n_result_cell] = DEFINED (PINT 99)']
    else:
        assert name == 'strict-scalar-name-type-errors'
        values += ['$config_strict(S,pconfigcall_S)', 'pconfigcall_S.SELECTION = eps',
            '$config_conversion(S,pconfigcall_S,PINT 37) = TYPEREJECT',
            '$lookup(S.ENV,' + text('result') + ') = (n_result_cell)',
            'S.STORE[n_result_cell] = DEFINED (PINT 99)',
            *error('S_error', 'S', 'constant', 'TypeError', 'PINT 37',
                'constant(): Argument #1 ($name) must be of type string, int given'),
            'S_error.STRINGDATA = S.STRINGDATA',
            *front('S_defined', 'S_error', 'INTRINSIC_DEFINED', 'PBOOL true'),
            '$config_strict(S_defined,pconfigcall_S_defined)',
            '$config_conversion(S_defined,pconfigcall_S_defined,PBOOL true) = TYPEREJECT',
            *error('S_defined_error', 'S_defined', 'defined', 'TypeError', 'PBOOL true',
                'defined(): Argument #1 ($constant_name) must be of type string, true given'),
            'S_defined_error.STRINGDATA = S_defined.STRINGDATA',
            'S_defined_error.STORE[n_result_cell] = DEFINED (PINT 99)']
    values += ['S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)']
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out, originals = args.output.resolve(), args.sources.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / (args.phase + '-report.json'); assert not report_path.exists()
    native_path = originals / 'native-report.json'
    native = json.loads(native_path.read_bytes())
    assert native['passed'] and native['inputs_stable'] and native['head_stable']
    names = list(sources.family.CASES)
    paths = {name: originals / name / 'main.php' for name in names}
    for name, path in paths.items():
        assert path.read_bytes() == sources.family.CASES[name]
        row, = [row for row in native['records'] if row['id'] == name]
        assert row['source_sha256'] == sha(path)
    watched = [Path(__file__), Path(common.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/static_types.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        native_path, *paths.values()]
    if args.phase == 'check':
        watched += [out / 'prepare-report.json']
        watched += [out / name / item for name in names for item in ('protocol.watsup', 'assertions.json')]
    pins = lambda: dict(sources.family.fingerprint(), **{str(path): sha(path) for path in watched})
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'phase': args.phase, 'revision': head, 'inputs': pins(), 'records': [], 'passed': False}
    try:
        if args.phase == 'prepare':
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                try:
                    for name, path in paths.items():
                        parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())}); assert parsed['accepted']
                        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                        values = checks(checked['fixture'], path, name)
                        target = out / name; target.mkdir()
                        fixture = target / 'protocol.watsup'
                        (target / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
                        fixture.write_text(common.PREFIX + PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                            ''.join('  -- if ' + value + '\n' for value in values))
                        report['records'].append({'id': name, 'fixture_sha256': sha(fixture), 'premises': len(values)})
                finally:
                    adapter.close()
            finally:
                frontend.close()
        else:
            prepared = json.loads((out / 'prepare-report.json').read_bytes())
            assert prepared['passed'] and prepared['inputs_stable'] and prepared['head_stable']
            assert all(report['inputs'][key] == value for key, value in prepared['inputs'].items())
            assert [row['id'] for row in prepared['records']] == names
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
            for row in prepared['records']:
                target = out / row['id']; fixture = target / 'protocol.watsup'
                assert sha(fixture) == row['fixture_sha256']
                record = dict(row); report['records'].append(record)
                record['process'] = recorder.recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    '--sl', *modules, str(fixture)], target / 'check', 90)
                assert record['process']['exit'] == 0 and not record['process']['timeout'] and not record['process']['group_after']
                assert (target / 'check.stdout').read_bytes() == b'true\n' and (target / 'check.stderr').read_bytes() == b''
                assert sha(fixture) == row['fixture_sha256']
                record['passed'] = True
                print(record['id'], record['premises'], 'PASS', flush=True)
        report['passed'] = True
    finally:
        report['inputs_stable'] = report['inputs'] == pins()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()

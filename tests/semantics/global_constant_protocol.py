#!/usr/bin/env python3
"""Original-derived global constant() fronts, captured values and API Error trace."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import class_constant_call_protocol as common
import error_handler_run as recorder
import global_constant_sources as sources
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
text = lambda value: '$ptascii(' + json.dumps(value) + ')'


def front(state, start, query):
    return [*common.reach(state, start, 0, query),
        state + '.TODO = (CONFIG_INVOKE pconfigcall_' + state + ') :: ptask_' + state + '*',
        '$dynamic_global_constant_call(pconfigcall_' + state + ')',
        '$dynamic_global_constant_valid(' + state + ',pconfigcall_' + state + ')',
        *common.public(state)]


def unchanged(before, after):
    return [after + '.' + key + ' = ' + before + '.' + key for key in (
        'USERCONSTANTS', 'EVENTS', 'STORE', 'SELECTEDCALLS', 'FILES', 'SOURCES',
        'EVALCONTEXTS', 'FILECONTEXTS', 'FILESEQ', 'POOLS')]


def checks(program, path, identity, stdout):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    query = {'names-and-scalars': 'OutsideGlobal21',
        'captured-query-and-strings': 'GlobalRequest21',
        'missing-api-error': '\\MissingGlobal21'}[identity]
    values += front('S', 'S_initial', query)
    values += ['pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN pvalue_query)]',
        '$string_bytes(pvalue_query) = (' + text(query) + ')',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)',
        'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)']
    for label, change in [('site', '.SITE = PORIGIN 0 eps'), ('line', '.LINE = $(pconfigcall_S.LINE + 1)'),
            ('owner', '.OWNER = (0)'), ('selection', '.SELECTION = (|S.SELECTEDCALLS|)')]:
        values += ['~$dynamic_global_constant_valid(S,pconfigcall_S[' + change + '])']
    values += ['~$dynamic_global_constant_call(pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (PSTRING ' + text('Unknown::VALUE') + '))]])']
    if identity == 'names-and-scalars':
        values += ['pconfigcall_S.SELECTION = eps',
            '$dynamic_global_constant_known(S,pconfigcall_S.SITE) = (pvalue_known)',
            '$string_bytes(pvalue_known) = (' + text(query) + ')',
            '~$dynamic_global_constant_valid(S,pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (PSTRING ' + text('GlobalQuery21\\Mixed') + '))]])',
            '$dynamic_global_constant_value(S,' + text(query) + ') = (PINT 31)',
            'S.USERCONSTANTS[6].NAME = ' + text(query),
            'S_bad_class = S[.USERCONSTANTS[6].CLASS = PVSTRING true]',
            '$dynamic_global_constant_value(S_bad_class,' + text(query) + ') = eps',
            '~$call_descriptors_valid(S_bad_class)']
        values += common.step('S_value', 'S', 'PINT 31') + unchanged('S', 'S_value')
        values += front('S_float', 'S_value', 'GlobalQuery21\\UserFloat')
        values += common.step('S_float_value', 'S_float', 'PFLOAT 4609434218613702656') + unchanged('S_float', 'S_float_value')
        values += front('S_false', 'S_float_value', 'GlobalQuery21\\UserFalse')
        values += common.step('S_false_value', 'S_false', 'PBOOL false') + unchanged('S_false', 'S_false_value')
        values += front('S_null', 'S_false_value', 'GlobalQuery21\\UserNull')
        values += ['$dynamic_global_constant_value(S_null,' + text('GlobalQuery21\\UserNull') + ') = (PNULL)']
        values += common.step('S_null_value', 'S_null', 'PNULL') + unchanged('S_null', 'S_null_value')
        values += front('S_special', 'S_null_value', 'TrUe')
        values += common.step('S_special_value', 'S_special', 'PBOOL true') + unchanged('S_special', 'S_special_value')
        finish = 'S_special_value'
    elif identity == 'captured-query-and-strings':
        values += ['pconfigcall_S.SELECTION = (n_selection)',
            '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            '$lookup(S.ENV,' + text('call') + ') = (n_callee)',
            'S.STORE[n_callee] = DEFINED pvalue_callee',
            '$string_bytes(pvalue_callee) = (' + text('defined') + ')',
            '$user_constant_at(S.USERCONSTANTS,' + text('GlobalRequest21') + ') = (puserconstant)',
            'puserconstant.CLASS = PVSTRING false',
            'puserconstant.VALUE = PSTRING_CARRIER (REQUEST_STRING n_string) ' + text('request-value'),
            '$dynamic_global_constant_value(S,' + text('GlobalRequest21') + ') = (puserconstant.VALUE)',
            'S.USERCONSTANTS[1] = puserconstant',
            'S_bad_class = S[.USERCONSTANTS[1].CLASS = PVSTRING true]',
            '$dynamic_global_constant_value(S_bad_class,' + text('GlobalRequest21') + ') = eps',
            '~$call_descriptors_valid(S_bad_class)']
        values += common.step('S_value', 'S', 'puserconstant.VALUE') + unchanged('S', 'S_value')
        values += front('S_literal', 'S_value', 'GlobalLiteral21')
        values += common.step('S_literal_value', 'S_literal', 'PSTRING_CARRIER INTERNED_STRING ' + text('literal'))
        finish = 'S_literal_value'
    else:
        values += ['pconfigcall_S.NAMED',
            '$dynamic_global_constant_known(S,pconfigcall_S.SITE) = (pvalue_known)',
            '$string_bytes(pvalue_known) = (' + text(query) + ')',
            '~$dynamic_global_constant_valid(S,pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (PSTRING ' + text('OtherGlobal21') + '))]])']
        values += common.step('S_error', 'S')
        values += ['S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
            'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('Undefined constant "MissingGlobal21"') + ')',
            '$throwable_field(S_error,n_error,"line") = PINT 5',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
            '$trace_array_field(S_error,n_frame,' + text('function') + ') = PSTRING ' + text('constant'),
            '$trace_array_field(S_error,n_frame,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_query)]',
            'S_error.EVENTS = S.EVENTS', 'S_error.USERCONSTANTS = S.USERCONSTANTS', *common.public('S_error')]
        finish = 'S_error'
    values += ['S_done = $drive_steps(' + finish + ',10000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', '$test_outputs(S_done.EVENTS) = ($base64(' + json.dumps(stdout) + '))',
        *common.public('S_done')]
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
    native = json.loads((originals / 'native-report.json').read_bytes())
    assert native['passed'] and native['inputs_stable'] and native['head_stable']
    names = [name for name in sources.CASES if name != 'array-result-boundary']
    extra = [Path(__file__), Path(common.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', originals / 'native-report.json']
    extra += [originals / name / 'main.php' for name in names]
    if args.phase == 'check':
        extra += [out / name / item for name in names for item in ('protocol.watsup', 'assertions.json')]
    pins = lambda: dict(sources.fingerprint(), **{str(p): sources.sha(p) for p in extra})
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'inputs': pins(), 'records': [], 'source_agreements': 0, 'passed': False}
    try:
        if args.phase == 'prepare':
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            adapter = None
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                for name in names:
                    path = originals / name / 'main.php'; assert path.read_bytes() == sources.CASES[name]
                    row, = [r for r in native['records'] if r['id'] == name]
                    assert sources.sha(path) == row['source_sha256']
                    parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())}); assert parsed['accepted']
                    program = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
                    assertions = checks(program, path, name, row['stdout'])
                    target = out / name; target.mkdir()
                    (target / 'assertions.json').write_text(json.dumps(assertions, indent=2) + '\n')
                    (target / 'protocol.watsup').write_text(common.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + assertion + '\n' for assertion in assertions))
            finally:
                if adapter: adapter.close()
                frontend.close()
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
            for name in names:
                target = out / name
                run = recorder.recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    '--sl', *modules, str(target / 'protocol.watsup')], target / 'check', 90)
                assert run['exit'] == 0 and not run['timeout'] and not run['group_after']
                assert (target / 'check.stdout').read_bytes() == b'true\n' and (target / 'check.stderr').read_bytes() == b''
                report['records'].append({'id': name, 'premises': len(json.loads((target / 'assertions.json').read_bytes())), 'passed': True})
                print(report['records'][-1], flush=True)
        report['passed'] = True
    finally:
        report['inputs_stable'] = report['inputs'] == pins()
        report['passed'] = report['passed'] and report['inputs_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()

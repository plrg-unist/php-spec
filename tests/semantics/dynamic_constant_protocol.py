#!/usr/bin/env python3
"""Reached scalar define/defined rows, immutable literals and mutable inputs."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
STAGES = {'literal': ('static-native-v39', 'direct-dynamic-constant', 'V39_CREATED', 41),
    'selection': ('static-native-v39', 'namespace-dynamic-constant', 'V39Lookup\\RUNTIME', 17),
    'capture': ('static-native-v39-capture', 'string-capture', 'V39_SNAPSHOT', None),
    'interned': ('static-native-v39-interned', 'interned-value', 'V39_INTERNED', None)}
b64 = lambda data: base64.b64encode(data).decode()
PREFIX = r'''
dec $test_output_item(pevent) : nat*
def $test_output_item(OUTPUT n*) = n*
def $test_output_item(pevent) = eps -- otherwise
dec $test_outputs(pevent*) : nat*
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output_item(pevent) ++ $test_outputs(pevent_tail*)
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_define_front(pstate) : bool
def $test_define_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
def $test_define_front(S) = false -- otherwise
dec $test_define_seek(pstate, nat) : pstate
def $test_define_seek(S, 0) = S
def $test_define_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_define_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_seek(S, n) = $test_define_seek($drive_steps($test_running(S), 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(name):
    return ['$call_descriptors_valid(' + name + ')', '$declaration_entry_check(' + name + ') = ' + name,
        '$heap_valid($heap_graph(' + name + '))']


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in names:
            suite, case_name, constant, number = STAGES[name]
            case = sources / suite / case_name
            native = json.loads((case.parent / 'report.json').read_text())
            row, = [item for item in native['records'] if item['id'] == case_name]
            assert native['result'] == 'native_observation' and native['stable_inputs']
            assert native['target'] == types.PROFILE and row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted'], parsed
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
                'S_found = $test_define_seek(S_initial,1000)',
                r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                'S = S_found[.COMPLETION = NORMAL]', '$test_define_front(S)',
                'S.FILEINCLUDEPATH = eps', 'S.USERCONSTANTS = eps',
                'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
                '$config_invoke_valid(S,pconfigcall)', '$dynamic_define_source(S,pconfigcall.SITE)',
                '$dynamic_define_values(pconfigcall) = ((preqbytes_name,pvalue_actual))',
                'preqbytes_name = $ptascii(' + json.dumps(constant) + ')', *public('S'),
                'S_after = $drive_steps(S,1)',
                r'S_after.COMPLETION = NORMAL \/ S_after.COMPLETION = BUDGET',
                'S_row = S_after[.COMPLETION = NORMAL]', 'S_row.USERCONSTANTS = [puserconstant]',
                'puserconstant.ORIGIN = pconfigcall.SITE',
                'puserconstant.NAME = $user_constant_key(preqbytes_name)',
                'puserconstant.VALUE = pvalue_actual', 'puserconstant.READS = eps',
                'puserconstant.RECEIVES = eps', 'S_row.RESULT = KNOWN (PBOOL true)',
                'S_row.EVENTS = S.EVENTS',
                '$source_constant_lookup(S_row,preqbytes_name) = (VALUE pvalue_actual)',
                '$dynamic_constant_exists(S_row,preqbytes_name)', *public('S_row')]
            if number is not None:
                checks += ['pvalue_actual = PINT ' + str(number), 'puserconstant.CLASS = PVSCALAR']
            elif name == 'capture':
                checks += ['puserconstant.CLASS = PVSTRING false',
                    'pvalue_actual = PSTRING_CARRIER (REQUEST_STRING n_string) n_bytes*',
                    'n_bytes* = $ptascii("old")', '$string_carrier_valid(S_row,pvalue_actual)']
            else:
                checks += ['puserconstant.CLASS = PVSTRING true',
                    'pvalue_actual = PSTRING_CARRIER INTERNED_STRING n_bytes*',
                    'n_bytes* = $ptascii("kept")', '$string_carrier_valid(S_row,pvalue_actual)']
            variants = [
                '[puserconstant[.ORIGIN = PORIGIN 0 eps]]',
                '[puserconstant[.NAME = $ptascii("E_WARNING")]]',
                '[puserconstant[.CLASS = PVARRAY false eps]]',
                '[puserconstant[.READS = [{ORIGIN puserconstant.ORIGIN, VALUE (PINT 0), CLASS PVSCALAR, LOOKUP eps}]]]',
                '[puserconstant[.RECEIVES = [{OWNER 0, INDEX 0, FRONTIER (RECEIVE_METHOD puserconstant.ORIGIN puserconstant.ORIGIN puserconstant.ORIGIN 0), CAUSE {UNIT 0, CALLS eps, AUTOLOAD eps}}]]]',
                '[puserconstant,puserconstant]']
            if name == 'literal':
                variants += ['[puserconstant[.NAME = $ptascii("V39_FORGED")]]',
                    '[puserconstant[.VALUE = PINT 42]]']
            if name == 'selection':
                checks += ['pconfigcall.SELECTION = (n_selection)',
                    'S.SELECTEDCALLS[n_selection] = pselectedcall',
                    'pselectedcall.KIND = INTRINSIC_DEFINE',
                    '~$dynamic_define_source(S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0],puserconstant.ORIGIN)',
                    '~$call_descriptors_valid(S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0])']
                variants += ['[puserconstant[.NAME = preqbytes_name]]']
            if name == 'capture':
                variants += ['[puserconstant[.VALUE = PSTRING_CARRIER (REQUEST_STRING (|S_row.STRINGDATA|)) n_bytes*]]',
                    '[puserconstant[.CLASS = PVSTRING true]]']
            if name == 'interned':
                variants += ['[puserconstant[.CLASS = PVSTRING false]]',
                    '[puserconstant[.NAME = $ptascii("V39_FORGED")]]',
                    '[puserconstant[.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("changed"))]]']
            checks += ['~$user_constants_valid(S_row[.USERCONSTANTS = ' + variant + '],' + variant + ')' for variant in variants]
            checks += ['~$call_descriptors_valid(S_row[.USERCONSTANTS = ' + variant + '])' for variant in variants]
            checks += ['S_final = $drive_steps(S_row,2000)', 'S_final.COMPLETION = NORMAL',
                'S_final.FILEINCLUDEPATH = eps', 'S_final.TODO = eps',
                'S_final.USERCONSTANTS = [puserconstant]',
                '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(row['stdout']) + ')', *public('S_final')]
            if name == 'capture':
                checks += ['S_name = $read_name(S_final,$ptascii("name"),1)',
                    'S_name.RESULT = KNOWN pvalue_name_after', '$string_bytes(pvalue_name_after) = ($ptascii("V39_CHANGED"))',
                    'S_value = $read_name(S_final,$ptascii("value"),1)',
                    'S_value.RESULT = KNOWN pvalue_value_after', '$string_bytes(pvalue_value_after) = ($ptascii("new"))',
                    '$string_bytes(puserconstant.VALUE) = ($ptascii("old"))',
                    '$user_constants_valid(S_final[.USERCONSTANTS = [puserconstant[.VALUE = PINT 7][.CLASS = PVSCALAR]]],[puserconstant[.VALUE = PINT 7][.CLASS = PVSCALAR]])']
            if name == 'literal':
                checks += ['S_array = $allocate_array(S,$array_empty())', 'S_array.RESULT = KNOWN (PARRAY n_array)',
                    'pconfigcall_array = pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING preqbytes_name)), NAMED_SENT (KNOWN (PARRAY n_array))]]',
                    'S_array_call = S_array[.TODO = (CONFIG_INVOKE pconfigcall_array) :: ptask_tail*]',
                    'S_refused = $dynamic_constant_receive(S_array_call,pconfigcall_array)',
                    'S_refused.COMPLETION = UNSUPPORTED "dynamic constant call domain"',
                    'S_refused.USERCONSTANTS = eps']
            if name == 'interned':
                checks += ['$dynamic_constant_class(PSTRING n_bytes*) = eps',
                    'pconfigcall_legacy = pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING preqbytes_name)), NAMED_SENT (KNOWN (PSTRING n_bytes*))]]',
                    'S_legacy_call = S[.TODO = (CONFIG_INVOKE pconfigcall_legacy) :: ptask_tail*]',
                    'S_legacy = $dynamic_constant_receive(S_legacy_call,pconfigcall_legacy)',
                    'S_legacy.COMPLETION = UNSUPPORTED "dynamic constant call domain"',
                    'S_legacy.USERCONSTANTS = eps']
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names, out, sources = args.stage or list(STAGES), args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for name in names:
        suite, case, _, _ = STAGES[name]
        paths += [sources / suite / 'report.json', sources / suite / 'run.py', sources / suite / case / 'main.php']
        paths += [sources / suite / case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    assert not (out / (label + '-report.json')).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())), 'inputs': before,
        'implementation_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'records': [], 'agreement_credit': 0, 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
        else:
            mods = [str(ROOT / item) for item in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                target = out / name
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *mods,
                    str(target / 'protocol.watsup')], target / label, 90, ROOT)
                passed = runner.returncode == 0 and runner.stdout.strip() == b'true' and not runner.stderr
                report['records'].append({'id': name, 'pass': passed, 'runner_exit': runner.returncode,
                    'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]), flush=True)
                if not passed:
                    break
        report['result'] = 'pass' if args.phase == 'fixtures' or len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'], record['premises'] = False, 0
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['result'] == 'pass' else 1)


if __name__ == '__main__':
    main()

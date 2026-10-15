#!/usr/bin/env python3
"""Reached stdClass constant() values, shared identity and RESULT ownership."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import class_constant_call_protocol as common
import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = {'literal': ('static-native-v59', 'literal-stdclass', 'native_observation'),
         'selected': ('static-native-v59', 'selected-stdclass', 'native_observation')}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
text = lambda value: '$ptascii(' + json.dumps(value) + ')'
PREFIX = common.PREFIX


def property_value(state, obj, value, suffix):
    return [f'$property_slot_at($object_table_slots_at({state},{obj}),$ptascii("value")) = (ppropertyslot_{suffix})',
            f'ppropertyslot_{suffix}.STATE = PROP_VALUE pitem_{suffix}',
            f'$entry_value({state},pitem_{suffix}) = PINT {value}']


def receive(state, previous, suffix, query, value, budget=False):
    call, row = 'pconfigcall_' + suffix, 'puserconstant_' + suffix
    obj, site, birth = 'n_object_' + suffix, 'porigin_site_' + suffix, 'pconstantstdobject_' + suffix
    values = [*common.reach(state,previous,0,query), *common.public(state),
        f'{state}.TODO = (CONFIG_INVOKE {call}) :: ptask_{suffix}*',
        f'$dynamic_global_constant_valid({state},{call})',
        f'{call}.SENT = [NAMED_SENT (KNOWN pvalue_query_{suffix})]',
        f'$string_carrier_valid({state},pvalue_query_{suffix})',
        f'$user_constant_at({state}.USERCONSTANTS,{text(query)}) = ({row})',
        f'{row}.CLASS = PVSTDCLASS {obj} {site}', f'{row}.VALUE = POBJECT {obj}',
        f'$global_std_record({state}.CONSTANTSTDOBJECTS,{obj}) = ({birth})',
        f'$global_std_completed({state},{birth})', f'{state}.OBJECTS[{obj}] = STDINSTANCE',
        f'$dynamic_global_constant_value({state},{text(query)}) = (POBJECT {obj})',
        f'n_owners_{suffix} = $heap_owners($heap_graph({state}),HOBJECT {obj})',
        f'$(n_owners_{suffix} > 0)', *property_value(state,obj,value,suffix)]
    start = state
    if budget:
        values += ['S_pause = $drive_steps(' + state + ',0)',
                   'S_pause = ' + state + '[.COMPLETION = BUDGET]',
                   'S_resumed = S_pause[.COMPLETION = NORMAL]', 'S_resumed = ' + state]
        start = 'S_resumed'
    after = state + '_value'
    values += common.step(after,start,'POBJECT ' + obj)
    values += [f'{after}.TODO = ptask_{suffix}*', f'{after}.BASE = BASE_VALUE (KNOWN PNULL)',
               f'$heap_owners($heap_graph({after}),HOBJECT {obj}) = $(n_owners_{suffix} + 1)']
    values += [f'{after}.{field} = {state}.{field}' for field in
               ['OBJECTS','OBJECTPROPS','OBJECTTABLES','ALLOCATIONS','USERCONSTANTS','CONSTANTSTDOBJECTS','STORE']]
    return values


def assertions(main, case, stage, stdout):
    values = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
              'S_initial.COMPLETION = BUDGET']
    if stage == 'literal':
        values += receive('S_first','S_initial','first','V59_LITERAL',17,True)
        values += ['pconfigcall_first.SELECTION = eps', 'n_owners_first = 2']
        # These certificate projections are helper-only; no forged state is driven.
        for label, change in [('missing','[.CONSTANTSTDOBJECTS = eps]'),
                              ('incomplete','[.CONSTANTSTDOBJECTS[0].COMPLETE = false]'),
                              ('dead','[.ALLOCATIONS = eps]')]:
            values += [f'S_{label} = S_first{change}',
                       f'$dynamic_global_constant_value(S_{label},$ptascii("V59_LITERAL")) = eps']
        values += receive('S_again','S_first_value','again','V59_LITERAL',31)
        values += ['n_object_again = n_object_first', 'puserconstant_again = puserconstant_first',
                   'pconstantstdobject_again = pconstantstdobject_first',
                   'pconfigcall_again.SITE =/= pconfigcall_first.SITE',
                   'n_owners_again = 2']
        start = 'S_again_value'
    else:
        values += receive('S_left','S_initial','left','V59_LEFT',17)
        values += receive('S_right','S_left_value','right','V59_RIGHT',29)
        values += ['pconfigcall_left.SELECTION = (n_selection_left)',
                   'pconfigcall_right.SELECTION = (n_selection_right)',
                   'n_selection_left =/= n_selection_right',
                   'S_left.SELECTEDCALLS[n_selection_left].KIND = INTRINSIC_CONSTANT',
                   'S_right.SELECTEDCALLS[n_selection_right].KIND = INTRINSIC_CONSTANT',
                   'pconfigcall_right.SITE = pconfigcall_left.SITE',
                   'n_object_left =/= n_object_right',
                   'S_right.USERCONSTANTS = S_left.USERCONSTANTS',
                   'S_right.CONSTANTSTDOBJECTS = S_left.CONSTANTSTDOBJECTS',
                   '$dynamic_global_constant_value(S_right,$ptascii("V59_LEFT")) = (POBJECT n_object_left)']
        values += property_value('S_right','n_object_left',31,'left_changed')
        start = 'S_right_value'
    values += [f'S_final = $drive_steps({start},5000)', 'S_final.COMPLETION = NORMAL',
               'S_final.TODO = eps', 'S_final.FRAMES = eps', 'S_final.CURRENT = eps',
               '$test_outputs(S_final.EVENTS) = ' + term(stdout.encode()), *common.public('S_final')]
    for suffix,query,value in ([('first','V59_LITERAL',31)] if stage=='literal' else [('left','V59_LEFT',31),('right','V59_RIGHT',37)]):
        values += [f'$dynamic_global_constant_value(S_final,{text(query)}) = (POBJECT n_object_{suffix})',
                   f'$heap_owners($heap_graph(S_final),HOBJECT n_object_{suffix}) = 2',
                   *property_value('S_final','n_object_' + suffix,value,suffix + '_final')]
    return values


def prepare(out, sources):
    out.mkdir(parents=True, exist_ok=True)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *types.FLAGS,
                       '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for stage,(suite,name,expected) in CASES.items():
            case = sources / suite / name
            native = json.loads((case.parent / 'report.json').read_text())
            assert native['result'] == expected and native['stable_inputs']
            row, = [row for row in native['records'] if row['id'] == name]
            assert row['exit'] == 0 and not row['stderr']
            assert all(hashlib.sha256((case/filename).read_bytes()).hexdigest()==pin for filename,pin in row['originals'].items())
            parsed = frontend.request({'op':'parse','source':b64((case/'main.php').read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            checks = assertions(main,case,stage,row['stdout'])
            target = out/stage; target.mkdir()
            (target/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
            (target/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+item+'\n' for item in checks))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = list(CASES)
    sources, out = args.sources.resolve(), args.output.resolve()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py', Path(common.__file__),
             ROOT / 'tests/semantics/global_constant_stdclass_protocol.py',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for suite, name, _ in CASES.values():
        case = sources / suite / name
        paths += [case.parent / 'run.py', case.parent / 'report.json', *sorted(case.glob('*.php')),
                  *[case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
    if args.phase == 'check':
        for stage in selected:
            paths += [out / stage / 'protocol.watsup', out / stage / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    assert not (out / (args.phase + '-report.json')).exists()
    report = {'phase': args.phase, 'selected': selected, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
              'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
              'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'sl_timeout': 90, 'result': 'fail', 'records': [], 'agreement_credit': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for stage in selected:
                target = out / stage
                assert not (target / 'check').exists()
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules,
                                  str(target / 'protocol.watsup')], target / 'check', 90, ROOT)
                passed = runner.returncode == 0 and runner.stdout == b'true\n' and not runner.stderr
                report['records'].append({'id': stage, 'pass': passed, 'runner_exit': runner.returncode,
                                          'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]), flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(selected) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'], record['premises'] = False, 0
        (out / (args.phase + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

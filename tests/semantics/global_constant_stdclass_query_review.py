#!/usr/bin/env python3
"""Independent reached selected-call and stdClass birth-certificate checks."""
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
b64 = lambda data: base64.b64encode(data).decode()


def assertions(main, source, stdout):
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(str(source).encode())) + ')',
              'S_initial.COMPLETION = BUDGET', *common.reach('S_left','S_initial',0,'V59_LEFT'),
              *common.public('S_left'),
              'S_left.TODO = (CONFIG_INVOKE pconfigcall_left) :: ptask_left*',
              '$dynamic_global_constant_valid(S_left,pconfigcall_left)',
              'pconfigcall_left.SELECTION = (n_selection_left)',
              'pconfigcall_left.SENT = [NAMED_SENT (KNOWN pvalue_left_query)]',
              '$string_bytes(pvalue_left_query) = ($ptascii("V59_LEFT"))',
              '$string_carrier_valid(S_left,pvalue_left_query)']
    for side in ['left','right']:
        checks += [f'$user_constant_at(S_left.USERCONSTANTS,$ptascii("V59_{side.upper()}")) = (puserconstant_{side})',
                   f'puserconstant_{side}.VALUE = POBJECT n_object_{side}',
                   f'puserconstant_{side}.CLASS = PVSTDCLASS n_object_{side} porigin_{side}',
                   f'$global_std_record(S_left.CONSTANTSTDOBJECTS,n_object_{side}) = (pconstantstdobject_{side})',
                   f'$global_std_completed(S_left,pconstantstdobject_{side})',
                   f'S_left.OBJECTS[n_object_{side}] = STDINSTANCE',
                   f'$heap_owners($heap_graph(S_left),HOBJECT n_object_{side}) = 2']
    checks += ['n_object_left =/= n_object_right', 'porigin_left =/= porigin_right',
               '$dynamic_global_constant_value(S_left,$ptascii("V59_LEFT")) = (POBJECT n_object_left)',
               '~$constant_value_class_valid(S_left,POBJECT n_object_right,puserconstant_left.CLASS)',
               '~$constant_value_class_valid(S_left,POBJECT n_object_left,PVSTDCLASS n_object_left porigin_right)',
               '~$constant_value_class_valid(S_left,POBJECT n_object_left,PVINSTANCE n_object_left porigin_left)',
               'S_bad_tag = S_left[.USERCONSTANTS = [puserconstant_left[.CLASS = PVOBJECT]]]',
               '$dynamic_global_constant_value(S_bad_tag,$ptascii("V59_LEFT")) = eps',
               'S_bad_identity = S_left[.USERCONSTANTS = [puserconstant_left[.VALUE = POBJECT n_object_right]]]',
               '$dynamic_global_constant_value(S_bad_identity,$ptascii("V59_LEFT")) = eps']
    # These projections establish refusals only; no malformed state is driven.
    projections = {
        'missing': '[.CONSTANTSTDOBJECTS = eps]',
        'pending': '[.CONSTANTSTDOBJECTS = $global_std_record_put(S_left.CONSTANTSTDOBJECTS,pconstantstdobject_left[.COMPLETE = false])]',
        'site': '[.CONSTANTSTDOBJECTS = $global_std_record_put(S_left.CONSTANTSTDOBJECTS,pconstantstdobject_left[.SITE = pconfigcall_left.SITE])]',
        'decl': '[.CONSTANTSTDOBJECTS = $global_std_record_put(S_left.CONSTANTSTDOBJECTS,pconstantstdobject_left[.DECL = pconfigcall_left.SITE])]',
        'prefix': '[.CONSTANTSTDOBJECTS = $global_std_record_put(S_left.CONSTANTSTDOBJECTS,pconstantstdobject_left[.PREFIX = $(|S_left.DECLARATIONS| + 1)])]',
        'kind': '[.OBJECTS[n_object_left] = INSTANCE porigin_left]',
        'dead': '[.ALLOCATIONS = eps]',
    }
    for label, change in projections.items():
        checks += [f'S_bad_{label} = S_left{change}',
                   f'$dynamic_global_constant_value(S_bad_{label},$ptascii("V59_LEFT")) = eps']
    checks += common.step('S_left_value','S_left','POBJECT n_object_left')
    checks += ['S_left_value.TODO = ptask_left*',
               '$heap_owners($heap_graph(S_left_value),HOBJECT n_object_left) = 3',
               '$heap_owners($heap_graph(S_left_value),HOBJECT n_object_right) = 2']
    unchanged = ['ALLOCATIONS','OBJECTS','OBJECTPROPS','OBJECTTABLES','ARRAYS','STORE',
                 'USERCONSTANTS','CONSTANTSTDOBJECTS','SELECTEDCALLS','SELECTSEQ','GLOBALTABLE']
    checks += [f'S_left_value.{field} = S_left.{field}' for field in unchanged]
    checks += [*common.reach('S_right','S_left_value',0,'V59_RIGHT'), *common.public('S_right'),
               'S_right.TODO = (CONFIG_INVOKE pconfigcall_right) :: ptask_right*',
               '$dynamic_global_constant_valid(S_right,pconfigcall_right)',
               'pconfigcall_right.SELECTION = (n_selection_right)',
               'n_selection_right =/= n_selection_left',
               'pconfigcall_right.SITE = pconfigcall_left.SITE',
               'pconfigcall_right.SENT = [NAMED_SENT (KNOWN pvalue_right_query)]',
               '$string_bytes(pvalue_right_query) = ($ptascii("V59_RIGHT"))',
               'pvalue_right_query =/= pvalue_left_query',
               'S_right.SELECTEDCALLS[n_selection_right].KIND = INTRINSIC_CONSTANT',
               '$selected_newer_same_owner(S_right.SELECTEDCALLS,S_right.SELECTEDCALLS[n_selection_left])',
               '~$dynamic_global_constant_valid(S_right,pconfigcall_left)',
               'S_right.USERCONSTANTS = S_left.USERCONSTANTS',
               'S_right.CONSTANTSTDOBJECTS = S_left.CONSTANTSTDOBJECTS',
               '$dynamic_global_constant_value(S_right,$ptascii("V59_RIGHT")) = (POBJECT n_object_right)',
               '$heap_owners($heap_graph(S_right),HOBJECT n_object_left) = 4',
               '$heap_owners($heap_graph(S_right),HOBJECT n_object_right) = 2']
    for label, change in {
        'old': '[.SELECTION = (n_selection_left)]',
        'absent': '[.SELECTION = (|S_right.SELECTEDCALLS|)]',
        'line': '[.LINE = $(pconfigcall_right.LINE + 1)]',
        'site': '[.SITE = porigin_right]',
        'carrier': '[.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_right.STRINGDATA|)) ($ptascii("V59_RIGHT"))))]]',
    }.items():
        checks += [f'pconfigcall_bad_{label} = pconfigcall_right{change}',
                   f'~$dynamic_global_constant_valid(S_right,pconfigcall_bad_{label})']
    checks += common.step('S_right_value','S_right','POBJECT n_object_right')
    checks += ['S_right_value.TODO = ptask_right*',
               '$heap_owners($heap_graph(S_right_value),HOBJECT n_object_right) = 3',
               '$heap_owners($heap_graph(S_right_value),HOBJECT n_object_left) = 4']
    checks += [f'S_right_value.{field} = S_right.{field}' for field in unchanged]
    checks += ['S_final = $drive_steps(S_right_value,5000)', 'S_final.COMPLETION = NORMAL',
               'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
               '$test_outputs(S_final.EVENTS) = $base64(' + json.dumps(b64(stdout.encode())) + ')',
               *common.public('S_final'),
               '$heap_owners($heap_graph(S_final),HOBJECT n_object_left) = 2',
               '$heap_owners($heap_graph(S_final),HOBJECT n_object_right) = 2']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    case = args.sources.resolve() / 'static-native-v59/selected-stdclass'
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths = [Path(__file__), Path(common.__file__), ROOT / 'tests/semantics/recorded_worker.py',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php',
             ROOT / 'adapter/wire.ml', case / 'main.php', case.parent / 'run.py', case.parent / 'report.json']
    paths += [case / 'native' / name for name in ['stdout','stderr','process.json','command.json']]
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    native = json.loads((case.parent / 'report.json').read_text())
    row, = [item for item in native['records'] if item['id'] == case.name]
    assert native['result'] == 'native_observation' and native['stable_inputs'] and native['target'] == types.PROFILE
    assert native['runtime_sha256'] == before['.tools/php/bin/php']
    assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
    assert row['exit'] == 0 and not row['stderr'] and (case / 'native/stdout').read_bytes() == row['stdout'].encode()
    report = {'revision': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
              'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','spec/semantics'], cwd=ROOT)).hexdigest(),
              'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
              'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL':'C','TZ':'UTC'},
              'agreement_credit': 0, 'result': 'fail'}
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *types.FLAGS, '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        try:
            parsed = frontend.request({'op':'parse', 'source':b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            fixture = adapter.request({'op':'check', 'ast':parsed['ast'], 'fixture':True})['fixture']
        finally:
            adapter.close()
        checks = assertions(fixture, case / 'main.php', row['stdout'])
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        target = out / 'protocol.watsup'
        target.write_text(common.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
        modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(target)], out / 'check', 90, ROOT)
        passed = runner.returncode == 0 and runner.stdout == b'true\n' and not runner.stderr
        report.update(result='pass' if passed else 'fail', runner_exit=runner.returncode,
                      premises=len(checks) if passed else 0, actual_steps=2, driven_forged_states=0)
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report.update(result='fail', premises=0)
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['result','stable_inputs','premises'] if key in report}))
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

#!/usr/bin/env python3
"""Reach ordered interface autoload in checked eval declarations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import interface_dependency_autoload_protocol as prior
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = ('eval-two-autoloads', 'eval-second-missing')
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def response(frontend, adapter, code, unit):
    parsed = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval',
        'profile': 'cli-raw-85', 'source': b64(code)})
    assert parsed['accepted']
    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
    assert checked['ok']
    return 'SOURCE_ACCEPT ' + str(unit) + ' ' + term(code) + ' ' + checked['fixture']


def public(state):
    return prior.public(state)


def assertions(case, main, responses, code, expected, success):
    a, b, target = ('$ptascii("I113A")', '$ptascii("I113B")', '$ptascii("C113")')
    checks = [
        'S_wait0 = $php_run(' + main + ',5000,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
        'S_wait0.COMPLETION = SOURCE_PENDING', 'S_wait0.EVALCONTEXTS = pevalcontext_0 :: eps',
        'pevalcontext_0.UNIT = 1', 'pevalcontext_0.BYTES = ' + term(code['class']),
        *public('S_wait0'), '$eval_response_valid(S_wait0,' + responses['class'] + ')',
        'S_body = $eval_resume(S_wait0,' + responses['class'] + ')',
        *prior.reach('S_decl', 'S_body', 3, 'C113'),
        'S_decl.ORIGIN = (porigin_target)',
        'porigin_target = PORIGIN 1 pcpath_target',
        '$class_at(S_decl.CLASSES,porigin_target) = (pclassdesc_target)',
        'pclassdesc_target.NAME = ' + target,
        'pclassdesc_target.KIND = "class"',
        'pclassdesc_target.PARENT = eps',
        'pclassdesc_target.INTERFACES = [' + a + ',' + b + ']',
        '$trait_plan(S_decl,pclassdesc_target).TRAITS = eps',
        '~$autoload_parent_pending(S_decl,pclassdesc_target)',
        '~$autoload_trait_pending(S_decl,pclassdesc_target)',
        '$autoload_interface_missing(S_decl,pclassdesc_target.INTERFACES) = (' + a + ')',
        '$autoload_interface_source(S_decl,porigin_target,' + a + ')',
        '~$autoload_interface_source(S_decl,porigin_target,' + b + ')',
        '$class_named(S_decl.CLASSNAMES,$ptlc(' + target + ')) = eps',
        *prior.step('S_nextA', 'S_decl'),
        'S_nextA.TODO = (AUTO_NEXT pautoloadcall_A) :: ptask_A*',
        'pautoloadcall_A.RESUME = AUTO_INTERFACE porigin_target ' + a,
        '$autoload_resume_valid(S_nextA,pautoloadcall_A)',
        *public('S_nextA'),
        'S_budget = $drive_steps(S_nextA,0)',
        'S_budget = S_nextA[.COMPLETION = BUDGET]',
        'S_resume = S_budget[.COMPLETION = NORMAL]',
        'S_resume = S_nextA',
        # This forged second-name resume is locally rejected while A is absent.
        'pautoloadcall_early = pautoloadcall_A[.NAME = ' + b + '][.KEY = $ptascii("i113b")][.RESUME = AUTO_INTERFACE porigin_target ' + b + ']',
        'S_early = S_nextA[.TODO = (AUTO_NEXT pautoloadcall_early) :: ptask_A*]',
        '~$autoload_interface_source(S_early,porigin_target,' + b + ')',
        '~$autoload_resume_valid(S_early,pautoloadcall_early)',
        '~$call_descriptors_valid(S_early)',
        # A forged list can pass the local prefix test, but fails public replay.
        'pclassdesc_fake = pclassdesc_target[.INTERFACES = [' + b + ',' + a + ']]',
        'S_fake = S_nextA[.CLASSES = $test_iface_replace(S_nextA.CLASSES,pclassdesc_fake)]',
        '$autoload_interface_source(S_fake,porigin_target,' + b + ')',
        '$declaration_entry_check(S_fake).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
        '~$call_descriptors_valid(S_fake)',
        'pclassdesc_parent = pclassdesc_target[.PARENT = ($ptascii("MissingParent"))]',
        'S_parent = S_decl[.CLASSES = $test_iface_replace(S_decl.CLASSES,pclassdesc_parent)]',
        '$autoload_parent_pending(S_parent,pclassdesc_parent)',
        '~$autoload_interface_pending(S_parent,pclassdesc_parent)',
        '~$autoload_interface_source(S_parent,porigin_target,' + a + ')',
        'S_waitA = $drive_steps(S_resume,5000)',
        'S_waitA.COMPLETION = SOURCE_PENDING',
        'S_waitA.EVALCONTEXTS = pevalcontext_A :: pevalcontext_outer_A :: eps',
        'pevalcontext_A.UNIT = 2', 'pevalcontext_A.BYTES = ' + term(code['A']),
        'pevalcontext_outer_A.UNIT = 1',
        *public('S_waitA'), '$eval_response_valid(S_waitA,' + responses['A'] + ')',
        'S_bodyA = $eval_resume(S_waitA,' + responses['A'] + ')',
        *prior.reach('S_postA', 'S_bodyA', 2, 'C113'),
        'S_postA.TODO = (AUTO_INTERFACE porigin_target ' + a + ') :: ptask_postA*',
        '$dynamic_new_known(S_postA,' + a + ')',
        '~$dynamic_new_known(S_postA,' + b + ')',
        '$autoload_interface_source(S_postA,porigin_target,' + a + ')',
        '$autoload_interface_source(S_postA,porigin_target,' + b + ')',
        '$autoload_interface_missing(S_postA,pclassdesc_target.INTERFACES) = (' + b + ')',
        '$class_named(S_postA.CLASSNAMES,$ptlc(' + target + ')) = eps',
        *prior.step('S_nextB', 'S_postA'),
        'S_nextB.TODO = (AUTO_NEXT pautoloadcall_B) :: ptask_B*',
        'pautoloadcall_B.RESUME = AUTO_INTERFACE porigin_target ' + b,
        '$autoload_resume_valid(S_nextB,pautoloadcall_B)',
        *public('S_nextB'),
        'S_nextB.SOURCES = S_postA.SOURCES',
        'S_nextB.CLASSNAMES = S_postA.CLASSNAMES',
    ]
    if success:
        checks += [
            'S_waitB = $drive_steps(S_nextB,5000)',
            'S_waitB.COMPLETION = SOURCE_PENDING',
            'S_waitB.EVALCONTEXTS = pevalcontext_B :: pevalcontext_outer_B :: eps',
            'pevalcontext_B.UNIT = 3', 'pevalcontext_B.BYTES = ' + term(code['B']),
            'pevalcontext_outer_B.UNIT = 1',
            *public('S_waitB'), '$eval_response_valid(S_waitB,' + responses['B'] + ')',
            'S_bodyB = $eval_resume(S_waitB,' + responses['B'] + ')',
            *prior.reach('S_postB', 'S_bodyB', 2, 'C113'),
            'S_postB.TODO = (AUTO_INTERFACE porigin_target ' + b + ') :: ptask_postB*',
            '$dynamic_new_known(S_postB,' + a + ')', '$dynamic_new_known(S_postB,' + b + ')',
            '$autoload_interface_source(S_postB,porigin_target,' + b + ')',
            '$class_named(S_postB.CLASSNAMES,$ptlc(' + target + ')) = eps',
            *prior.step('S_linked', 'S_postB'),
            '$class_named(S_linked.CLASSNAMES,$ptlc(' + target + ')) = (porigin_target)',
            *public('S_linked'),
            'S_finish = $drive_steps(S_linked,5000)',
        ]
    else:
        checks += [
            *prior.reach('S_postB', 'S_nextB', 2, 'C113'),
            'S_postB.TODO = (AUTO_INTERFACE porigin_target ' + b + ') :: ptask_postB*',
            '$dynamic_new_known(S_postB,' + a + ')', '~$dynamic_new_known(S_postB,' + b + ')',
            '$autoload_interface_source(S_postB,porigin_target,' + b + ')',
            'S_throw_budget = $drive_steps(S_postB,1)',
            'S_throw_budget.COMPLETION = BUDGET',
            'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
            'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
            'S_throw.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "Error"',
            '$string_bytes($throwable_field(S_throw,n_error,"message")) = ' + term(b'Interface "I113B" not found'),
            '$class_named(S_throw.CLASSNAMES,$ptlc(' + target + ')) = eps',
            *public('S_throw'),
            'S_finish = $drive_steps(S_throw,5000)',
        ]
    checks += [
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', 'S_finish.CURRENT = eps', 'S_finish.FRAMES = eps',
        '$test_iface_outputs(S_finish.EVENTS) = ' + term(expected),
        *public('S_finish'),
    ]
    return checks


def prepare(out, sources, selected):
    out.mkdir()
    freeze = json.loads((sources / 'freeze.json').read_text())
    native = json.loads((sources / 'native-report.json').read_text())
    changed = json.loads((sources / 'changed-v2-report.json').read_text())
    assert native['stable_inputs'] and changed['stable_inputs']
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in selected:
            case = sources / name
            row, = [item for item in freeze['cases'] if item['id'] == name]
            native_row, = [item for item in native['records'] if item['id'] == name]
            changed_row, = [item for item in changed['records'] if item['id'] == name]
            assert native_row['exact'] and changed_row['exact'] and changed_row['status'] == 'normal'
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['main_sha256']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            strings = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                if node['node'] == 'Scalar_String']
            code = {
                'class': next(value for value in strings if value.startswith(b'function mark113(){')),
                'A': next(value for value in strings if value == b'interface I113A {}'),
            }
            if name == 'eval-two-autoloads':
                code['B'] = next(value for value in strings if value == b'interface I113B {}')
            responses = {label: response(frontend, adapter, data, unit)
                for unit, (label, data) in enumerate(code.items(), 1)}
            checks = assertions(case, checked['fixture'], responses, code,
                base64.b64decode(row['expected_stdout']), name == 'eval-two-autoloads')
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(prior.PREFIX +
                '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
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
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    sources, out = args.sources.resolve(), args.output.resolve()
    freeze = json.loads((sources / 'freeze.json').read_text())
    paths = [Path(__file__), Path(prior.__file__), ROOT / 'spec/semantics/modules.json',
        ROOT / 'spec/semantics/277-autoload.watsup',
        ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/typed_static_invoke_set_protocol.py',
        ROOT / 'tests/semantics/static_types.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe',
        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
        ROOT / 'tests/semantics/profile.json', sources / 'freeze.py',
        sources / 'freeze.json', sources / 'native-report.json',
        sources / 'changed-v2-report.json']
    for name in selected:
        paths += [sources / name / 'main.php',
            sources / name / 'native.stdout', sources / name / 'native.stderr',
            sources / name / 'changed-v2.stdout', sources / name / 'changed-v2.stderr']
        if args.phase == 'check':
            paths += [out / name / 'assertions.json', out / name / 'protocol.watsup']
    pins = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = pins()
    report = {'phase': args.phase, 'selected': selected,
        'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(
            ['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'result': 'fail', 'records': []}
    try:
        assert before[str(sources / 'freeze.json')] == hashlib.sha256((sources / 'freeze.json').read_bytes()).hexdigest()
        assert freeze['base'] == report['revision']
        if args.phase == 'fixtures':
            prepare(out, sources, selected)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in selected:
                target = out / name
                command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    '--sl', *modules, str(target / 'protocol.watsup')]
                result = process(command, target / 'check', 120, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                report['records'].append({'id': name, 'pass': passed,
                    'runner_exit': result.returncode, 'command': command, 'cwd': str(ROOT),
                    'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(name, 'pass' if passed else 'fail', flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(selected) and all(
                item['pass'] for item in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (args.phase + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

#!/usr/bin/env python3
"""Check fixed NEW during and after a source-backed class-link autoload window."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import static_types as types
from recorded_worker import Worker


ROOT = Path(__file__).resolve().parents[2]
CASES = ('outer-target-during-dependency', 'reentry-then-missing-dependency')
RUNNER = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def term(data):
    return '$base64(' + json.dumps(b64(data)) + ')'


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


PREFIX = r'''
dec $s117_running(pstate) : pstate
def $s117_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $s117_running(S) = S -- otherwise
dec $s117_front(pstate) : bool
def $s117_front(S) = true
  -- if S.TODO = (EVAL (NExprNew name (SEQUENCE eps) metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin_new)
  -- if $new_source_name(S,porigin_new) = ($ptascii("C117"))
def $s117_front(S) = false -- otherwise
dec $s117_seek(pstate, nat) : pstate
def $s117_seek(S, 0) = S
def $s117_seek(S, n) = S
  -- if $(n > 0)
  -- if $s117_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $s117_seek(S, n) = $s117_seek($drive_steps($s117_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$s117_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $s117_output_item(pevent) : ptbytes
def $s117_output_item(OUTPUT ptbytes) = ptbytes
def $s117_output_item(pevent) = eps -- otherwise
dec $s117_output(pevent*) : ptbytes
def $s117_output(eps) = eps
def $s117_output(pevent :: pevent_tail*) = $s117_output_item(pevent) ++ $s117_output(pevent_tail*)
'''


def assertions(case, main, code, responses, expected):
    source = case / 'main.php'
    checks = [
        'S_wait0 = $php_run(' + main + ',5000,' + json.dumps(b64(str(source).encode())) + ')',
        'S_wait0.COMPLETION = SOURCE_PENDING',
        'S_wait0.EVALCONTEXTS = pevalcontext_outer :: eps',
        'pevalcontext_outer.UNIT = 1',
        'pevalcontext_outer.BYTES = ' + term(code['outer']),
        '$eval_response_valid(S_wait0,' + responses['outer'] + ')',
        'S_body0 = $eval_resume(S_wait0,' + responses['outer'] + ')',
        'S_waitP = $drive_steps(S_body0,5000)',
        'S_waitP.COMPLETION = SOURCE_PENDING',
        'S_waitP.EVALCONTEXTS = pevalcontext_parent :: pevalcontext_outer2 :: eps',
        'pevalcontext_parent.UNIT = 2',
        'pevalcontext_parent.BYTES = ' + term(code['parent']),
        '$eval_response_valid(S_waitP,' + responses['parent'] + ')',
        'S_bodyP = $eval_resume(S_waitP,' + responses['parent'] + ')',
        'S_found = $s117_seek(S_bodyP,5000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_front = S_found[.COMPLETION = NORMAL]',
        '$s117_front(S_front)',
        'S_front.TODO = (EVAL (NExprNew name (SEQUENCE eps) metadata)) :: ptask_tail*',
        'S_front.ORIGIN = (porigin_new)',
        '$origin_node(S_front.SOURCES,porigin_new) = (NExprNew name (SEQUENCE eps) metadata)',
        '$new_source_name(S_front,porigin_new) = ($ptascii("C117"))',
        'S_front.FRAMES = pframe_Q :: pframe_P :: eps',
        'pframe_P.TODO = (AUTO_RESULT pautoloadcall_C pautoloadentry_C poperand_C) :: ptask_P*',
        'pautoloadcall_C.RESUME = AUTO_PUBLISH porigin_C',
        'S_saved = $constant_frame_scope(S_front,pframe_P,eps)',
        '$autoload_selected_valid(S_saved,pautoloadcall_C,pautoloadentry_C)',
        '$autoload_new_unlinked_call(S_saved,pautoloadcall_C,$ptascii("C117"))',
        '$class_at(S_front.CLASSES,porigin_C) = (pclassdesc_C)',
        'pclassdesc_C.KIND = "class"',
        'pclassdesc_C.NAME = $ptascii("C117")',
        '$class_named(S_front.CLASSNAMES,$ptascii("c117")) = eps',
        '$autoload_pending(S_front,$ptascii("C117"))',
        '$autoload_new_unlinked_frames(S_front,S_front.FRAMES,$ptascii("C117"))',
        '~$autoload_new_pending(S_front,$ptascii("C117"))',
        'pautoloadcall_wrong = pautoloadcall_C[.RESUME = AUTO_PUBLISH porigin_new]',
        '~$autoload_new_unlinked_call(S_saved,pautoloadcall_wrong,$ptascii("C117"))',
        '$call_descriptors_valid(S_front)',
        'S_budget0 = $drive_steps(S_front,0)',
        'S_budget0 = S_front[.COMPLETION = BUDGET]',
        'S_resume = S_budget0[.COMPLETION = NORMAL]',
        'S_resume = S_front',
        'PhpStep: S_resume ~> S_raw',
        'S_raw.COMPLETION = THROWN "Error" ($ptascii("Class \\"C117\\" not found")) z_error',
        'z_error = $runtime_line(S_resume,eps,NExprNew name (SEQUENCE eps) metadata)',
        'S_raw.TODO = ptask_tail*',
        'S_raw.AUTOLOAD = S_front.AUTOLOAD',
        'S_raw.SOURCES = S_front.SOURCES',
        'S_raw.CLASSNAMES = S_front.CLASSNAMES',
        'S_raw.FRAMES = S_front.FRAMES',
        'S_raw.EVENTS = S_front.EVENTS',
        'S_step_budget = $drive_steps(S_resume,1)',
        'S_step_budget.COMPLETION = BUDGET',
        'S_after = S_step_budget[.COMPLETION = NORMAL]',
    ]
    if 'Q' in code:
        checks += [
            'S_waitQ = $drive_steps(S_after,5000)',
            'S_waitQ.COMPLETION = SOURCE_PENDING',
            'S_waitQ.EVALCONTEXTS = pevalcontext_Q :: pevalcontext_tail*',
            'pevalcontext_Q.UNIT = 3',
            'pevalcontext_Q.BYTES = ' + term(code['Q']),
            '$eval_response_valid(S_waitQ,' + responses['Q'] + ')',
            'S_finish = $drive_steps($eval_resume(S_waitQ,' + responses['Q'] + '),5000)',
        ]
    else:
        checks += [
            'S_retry_found = $s117_seek(S_after,5000)',
            r'S_retry_found.COMPLETION = NORMAL \/ S_retry_found.COMPLETION = BUDGET',
            'S_retry = S_retry_found[.COMPLETION = NORMAL]',
            '$s117_front(S_retry)',
            'S_retry.FRAMES = eps',
            '$class_named(S_retry.CLASSNAMES,$ptascii("c117")) = eps',
            '~$autoload_new_unlinked_frames(S_retry,S_retry.FRAMES,$ptascii("C117"))',
            '$autoload_new_pending(S_retry,$ptascii("C117"))',
            'PhpStep: S_retry ~> S_begin',
            'S_begin.TODO = (AUTO_NEXT pautoloadcall_retry) :: ptask_retry*',
            'pautoloadcall_retry.RESUME = AUTO_NEW $ptascii("C117") eps z_retry z_retry',
            '$autoload_call_valid(S_begin,pautoloadcall_retry)',
            'S_finish = $drive_steps(S_begin,5000)',
        ]
    checks += [
        'S_finish.COMPLETION = NORMAL',
        'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps',
        'S_finish.FRAMES = eps',
        '$s117_output(S_finish.EVENTS) = ' + term(expected),
        '$call_descriptors_valid(S_finish)',
    ]
    return checks


def tracked(sources, selected, out, check):
    paths = [Path(__file__), ROOT / 'spec/semantics/modules.json',
             ROOT / 'spec/semantics/30-storage.watsup',
             ROOT / 'spec/semantics/127-class-runtime.watsup',
             ROOT / 'spec/semantics/184-class-constants.watsup',
             ROOT / 'spec/semantics/277-autoload.watsup',
             ROOT / 'tests/semantics/recorded_worker.py',
             ROOT / 'tests/semantics/static_types.py',
             ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe',
             ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', RUNNER,
             ROOT / 'tests/semantics/profile.json',
             sources / 'freeze.py', sources / 'freeze.json', sources / 'native-report.json',
             sources / 'changed-report.json']
    for name in selected:
        paths += [sources / name / 'main.php', sources / name / 'native.stdout',
                  sources / name / 'native.stderr', sources / name / 'changed.stdout',
                  sources / name / 'changed.stderr']
        if check:
            paths.append(out / name / 'protocol.watsup')
    return paths


def prepare(sources, out, selected):
    freeze = json.loads((sources / 'freeze.json').read_text())
    native = json.loads((sources / 'native-report.json').read_text())
    changed = json.loads((sources / 'changed-report.json').read_text())
    assert native['stable_inputs'] and changed['stable_inputs']
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         out / 'adapter')
        for name in selected:
            row, = [x for x in freeze['cases'] if x['id'] == name]
            nrow, = [x for x in native['records'] if x['id'] == name]
            crow, = [x for x in changed['records'] if x['id'] == name]
            assert nrow['exit'] == 0 and crow['exact'] and crow['status'] == 'normal'
            case = sources / name
            assert sha(case / 'main.php') == row['main_sha256']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            strings = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                       if node['node'] == 'Scalar_String']
            code = {'outer': next(x for x in strings if x.startswith(b'function mark117(){')),
                    'parent': next(x for x in strings if x == b'class P117 extends Q117 {}')}
            if name == 'outer-target-during-dependency':
                code['Q'] = next(x for x in strings if x.startswith(b'class Q117 {function q()'))
            responses = {label: response(frontend, adapter, text, unit)
                         for unit, (label, text) in enumerate(code.items(), 1)}
            checks = assertions(case, checked['fixture'], code, responses,
                                (case / 'native.stdout').read_bytes())
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX +
                '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join(('  -- ' if item.startswith('PhpStep:') else '  -- if ') + item + '\n'
                        for item in checks))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('fixtures', 'check'), required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    sources = args.sources.resolve()
    out = args.output.resolve()
    if args.phase == 'fixtures':
        out.mkdir()
    before = {str(p): sha(p) for p in tracked(sources, selected, out, args.phase == 'check')}
    report = {'phase': args.phase, 'selected': selected, 'inputs': before,
              'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
              'records': [], 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            prepare(sources, out, selected)
        else:
            modules = [str(ROOT / x) for x in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in selected:
                target = out / name
                command = [str(RUNNER), '--sl', *modules, str(target / 'protocol.watsup')]
                result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120)
                (target / 'check.stdout').write_bytes(result.stdout)
                (target / 'check.stderr').write_bytes(result.stderr)
                passed = result.returncode == 0 and result.stdout == b'true\n' and result.stderr == b''
                report['records'].append({'case': name, 'command': command,
                    'exit': result.returncode, 'passed': passed,
                    'stdout_sha256': sha(target / 'check.stdout'),
                    'stderr_sha256': sha(target / 'check.stderr')})
                print(name, 'pass' if passed else 'fail', flush=True)
                if not passed:
                    break
        report['stable_inputs'] = before == {str(p): sha(p) for p in tracked(sources, selected, out, args.phase == 'check')}
        report['result'] = 'pass' if report['stable_inputs'] and all(
            x['passed'] for x in report['records']) else 'fail'
    finally:
        (out / (args.phase + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

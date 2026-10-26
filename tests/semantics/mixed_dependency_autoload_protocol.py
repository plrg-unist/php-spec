#!/usr/bin/env python3
"""Reach parent, trait and ordered interface autoload from checked eval source."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import multi_interface_autoload_protocol as previous
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = ('eval-full-order', 'eval-wrongkind-trait-priority')
b64 = previous.b64
term = previous.term
public = previous.public

PREFIX = previous.prior.PREFIX + r'''
dec $test_mixed_front(pstate, nat) : bool
def $test_mixed_front(S,0) = true
  -- if S.TODO = (AUTO_PUBLISH porigin) :: ptask_tail*
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C114")
def $test_mixed_front(S,1) = true
  -- if S.TODO = (AUTO_TRAIT porigin preqbytes) :: ptask_tail*
  -- if preqbytes = $ptascii("T114")
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C114")
def $test_mixed_front(S,2) = true
  -- if S.TODO = (AUTO_INTERFACE porigin preqbytes) :: ptask_tail*
  -- if preqbytes = $ptascii("I114A")
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C114")
def $test_mixed_front(S,3) = true
  -- if S.TODO = (AUTO_INTERFACE porigin preqbytes) :: ptask_tail*
  -- if preqbytes = $ptascii("I114B")
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C114")
def $test_mixed_front(S,n) = false -- otherwise
dec $test_mixed_seek(pstate, nat, nat) : pstate
def $test_mixed_seek(S,n_phase,0) = S
def $test_mixed_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_mixed_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_mixed_seek(S,n_phase,n) = $test_mixed_seek($drive_steps($test_iface_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_mixed_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, previous_state, phase):
    return [f'{state}_found = $test_mixed_seek({previous_state},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$test_mixed_front({state},{phase})', *public(state)]


def step(state, previous_state):
    return previous.prior.step(state, previous_state)


def eval_stage(checks, label, prior_state, unit, code, response, phase):
    wait, body, post = 'S_wait' + label, 'S_body' + label, 'S_post' + label
    inner, outer = 'pevalcontext_' + label, 'pevalcontext_outer_' + label
    checks += [f'{wait} = $drive_steps({prior_state},5000)',
        f'{wait}.COMPLETION = SOURCE_PENDING',
        f'{wait}.EVALCONTEXTS = {inner} :: {outer} :: eps',
        f'{inner}.UNIT = {unit}', f'{inner}.BYTES = ' + term(code),
        f'{outer}.UNIT = 1', *public(wait),
        f'$eval_response_valid({wait},{response})',
        f'{body} = $eval_resume({wait},{response})',
        *reach(post, body, phase)]
    return post


def assertions(case, main, code, responses, expected, success):
    parent, trait, a, b, target = [f'$ptascii("{name}")' for name in
        ('P114', 'T114', 'I114A', 'I114B', 'C114')]
    interfaces = '[' + a + ',' + b + ']' if success else '[' + a + ']'
    checks = [
        'S_wait0 = $php_run(' + main + ',5000,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
        'S_wait0.COMPLETION = SOURCE_PENDING',
        'S_wait0.EVALCONTEXTS = pevalcontext_0 :: eps',
        'pevalcontext_0.UNIT = 1', 'pevalcontext_0.BYTES = ' + term(code['class']),
        *public('S_wait0'), '$eval_response_valid(S_wait0,' + responses['class'] + ')',
        'S_body = $eval_resume(S_wait0,' + responses['class'] + ')',
        *previous.prior.reach('S_decl', 'S_body', 3, 'C114'),
        'S_decl.ORIGIN = (porigin_target)',
        'porigin_target = PORIGIN 1 pcpath_target',
        '$class_at(S_decl.CLASSES,porigin_target) = (pclassdesc_target)',
        'pclassdesc_target.KIND = "class"',
        'pclassdesc_target.NAME = ' + target,
        'pclassdesc_target.PARENT = (' + parent + ')',
        'pclassdesc_target.INTERFACES = ' + interfaces,
        '$trait_plan(S_decl,pclassdesc_target) = ptraitplan',
        'ptraitplan.TRAITS = [' + trait + ']',
        'ptraitplan.PRECEDENCES = eps', 'ptraitplan.ALIASES = eps',
        '$autoload_parent_pending(S_decl,pclassdesc_target)',
        '~$trait_parent_available(S_decl,pclassdesc_target)',
        '~$autoload_trait_pending(S_decl,pclassdesc_target)',
        '~$autoload_interface_pending(S_decl,pclassdesc_target)',
        '~$autoload_trait_source(S_decl,porigin_target,' + trait + ')',
        '~$autoload_interface_source(S_decl,porigin_target,' + a + ')',
        '$class_named(S_decl.CLASSNAMES,$ptlc(' + target + ')) = eps',
        *step('S_nextP', 'S_decl'),
        'S_nextP.TODO = (AUTO_NEXT pautoloadcall_P) :: ptask_P*',
        'pautoloadcall_P.RESUME = AUTO_PUBLISH porigin_target',
        '$autoload_resume_valid(S_nextP,pautoloadcall_P)',
        *public('S_nextP'),
        'S_budget = $drive_steps(S_nextP,0)',
        'S_budget = S_nextP[.COMPLETION = BUDGET]',
        'S_resume = S_budget[.COMPLETION = NORMAL]',
        'S_resume = S_nextP',
        'pclassdesc_fake_parent = pclassdesc_target[.PARENT = (' + a + ')]',
        'S_fake_parent = S_nextP[.CLASSES = $test_iface_replace(S_nextP.CLASSES,pclassdesc_fake_parent)]',
        '$declaration_entry_check(S_fake_parent).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
        '~$call_descriptors_valid(S_fake_parent)',
    ]
    post = eval_stage(checks, 'P', 'S_resume', 2, code['P'], responses['P'], 0)
    checks += [
        post + '.TODO = (AUTO_PUBLISH porigin_target) :: ptask_postP*',
        '$dynamic_new_known(' + post + ',' + parent + ')',
        '$trait_parent_available(' + post + ',pclassdesc_target)',
        '~$autoload_interface_pending(' + post + ',pclassdesc_target)',
        '$autoload_trait_source(' + post + ',porigin_target,' + trait + ')',
        '$class_named(' + post + '.CLASSNAMES,$ptlc(' + target + ')) = eps',
    ]
    if not success:
        checks += [
            '$trait_fetch(' + post + ',ptraitplan.TRAITS,eps) = TRAITWRONG ' + trait,
            '~$autoload_trait_pending(' + post + ',pclassdesc_target)',
            '~$autoload_interface_source(' + post + ',porigin_target,' + a + ')',
            'S_throw_budget = $drive_steps(' + post + ',1)',
            'S_throw_budget.COMPLETION = BUDGET',
            'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
            'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
            'S_throw.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "Error"',
            '$string_bytes($throwable_field(S_throw,n_error,"message")) = ' +
                term(b'C114 cannot use T114 - it is not a trait'),
            '$class_named(S_throw.CLASSNAMES,$ptlc(' + target + ')) = eps',
            *public('S_throw'),
            'S_final = $drive_steps(S_throw,5000)',
        ]
    else:
        checks += [
            '$trait_fetch(' + post + ',ptraitplan.TRAITS,eps) = TRAITMISSING ' + trait,
            '$autoload_trait_pending(' + post + ',pclassdesc_target)',
            *step('S_nextT', post),
            'S_nextT.TODO = (AUTO_NEXT pautoloadcall_T) :: ptask_T*',
            'pautoloadcall_T.RESUME = AUTO_TRAIT porigin_target ' + trait,
            '$autoload_resume_valid(S_nextT,pautoloadcall_T)', *public('S_nextT'),
        ]
        post = eval_stage(checks, 'T', 'S_nextT', 3, code['T'], responses['T'], 1)
        checks += [
            post + '.TODO = (AUTO_TRAIT porigin_target ' + trait + ') :: ptask_postT*',
            '$trait_fetch(' + post + ',ptraitplan.TRAITS,eps) = TRAITFETCHED ([pclassdesc_trait])',
            'pclassdesc_trait.KIND = "trait"',
            '$autoload_interface_pending(' + post + ',pclassdesc_target)',
            '$autoload_interface_source(' + post + ',porigin_target,' + a + ')',
            '~$autoload_interface_source(' + post + ',porigin_target,' + b + ')',
            '$class_named(' + post + '.CLASSNAMES,$ptlc(' + target + ')) = eps',
            *step('S_nextA', post),
            'S_nextA.TODO = (AUTO_NEXT pautoloadcall_A) :: ptask_A*',
            'pautoloadcall_A.RESUME = AUTO_INTERFACE porigin_target ' + a,
            '$autoload_resume_valid(S_nextA,pautoloadcall_A)', *public('S_nextA'),
            'pclassdesc_fake_order = pclassdesc_target[.INTERFACES = [' + b + ',' + a + ']]',
            'S_fake_order = S_nextA[.CLASSES = $test_iface_replace(S_nextA.CLASSES,pclassdesc_fake_order)]',
            '$declaration_entry_check(S_fake_order).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
            '~$call_descriptors_valid(S_fake_order)',
        ]
        post = eval_stage(checks, 'A', 'S_nextA', 4, code['A'], responses['A'], 2)
        checks += [
            post + '.TODO = (AUTO_INTERFACE porigin_target ' + a + ') :: ptask_postA*',
            '$autoload_interface_source(' + post + ',porigin_target,' + b + ')',
            '$autoload_interface_missing(' + post + ',pclassdesc_target.INTERFACES) = (' + b + ')',
            *step('S_nextB', post),
            'S_nextB.TODO = (AUTO_NEXT pautoloadcall_B) :: ptask_B*',
            'pautoloadcall_B.RESUME = AUTO_INTERFACE porigin_target ' + b,
            '$autoload_resume_valid(S_nextB,pautoloadcall_B)', *public('S_nextB'),
        ]
        post = eval_stage(checks, 'B', 'S_nextB', 5, code['B'], responses['B'], 3)
        checks += [
            post + '.TODO = (AUTO_INTERFACE porigin_target ' + b + ') :: ptask_postB*',
            '$autoload_interface_source(' + post + ',porigin_target,' + b + ')',
            '$class_named(' + post + '.CLASSNAMES,$ptlc(' + target + ')) = eps',
            *step('S_linked', post),
            '$class_named(S_linked.CLASSNAMES,$ptlc(' + target + ')) = (porigin_target)',
            *public('S_linked'),
            'S_final = $drive_steps(S_linked,5000)',
        ]
    checks += [
        'S_final.COMPLETION = NORMAL', 'S_final.EXITSTATUS = 0',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '$test_iface_outputs(S_final.EVENTS) = ' + term(expected), *public('S_final'),
    ]
    return checks


def prepare(out, sources, selected):
    out.mkdir()
    freeze = json.loads((sources / 'freeze.json').read_text())
    native = json.loads((sources / 'native-report.json').read_text())
    changed = json.loads((sources / 'changed-report.json').read_text())
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
            strings = [base64.b64decode(node['fields'][0]['bytes']) for node in previous.nodes(parsed['ast'])
                if node['node'] == 'Scalar_String']
            codes = {'class': next(value for value in strings if value.startswith(b'function mark114(){')),
                     'P': next(value for value in strings if value.startswith(b'class P114 '))}
            if name == 'eval-full-order':
                codes.update(T=next(value for value in strings if value == b'trait T114 {}'),
                    A=next(value for value in strings if value == b'interface I114A {}'),
                    B=next(value for value in strings if value == b'interface I114B {}'))
            responses = {label: previous.response(frontend, adapter, value, unit)
                for unit, (label, value) in enumerate(codes.items(), 1)}
            checks = assertions(case, checked['fixture'], codes, responses,
                base64.b64decode(row['predicted_stdout']), name == 'eval-full-order')
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX +
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
    paths = [Path(__file__), Path(previous.__file__), Path(previous.prior.__file__),
        ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/277-autoload.watsup',
        ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/typed_static_invoke_set_protocol.py',
        ROOT / 'tests/semantics/static_types.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe',
        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
        ROOT / 'tests/semantics/profile.json', sources / 'freeze.py',
        sources / 'freeze.json', sources / 'native-report.json', sources / 'changed-report.json']
    for name in selected:
        paths += [sources / name / 'main.php', sources / name / 'native.stdout',
            sources / name / 'native.stderr', sources / name / 'changed.stdout',
            sources / name / 'changed.stderr']
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
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'result': 'fail', 'records': []}
    try:
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
                    'runner_exit': result.returncode, 'cwd': str(ROOT), 'command': command,
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

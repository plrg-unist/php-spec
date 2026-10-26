#!/usr/bin/env python3
"""Reach ordered two-trait autoload from checked eval declarations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import mixed_dependency_autoload_protocol as previous
import multi_interface_autoload_protocol as iface
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = ('ordered-methods', 'second-trait-missing', 'adapted-methods')
b64, term, public = iface.b64, iface.term, iface.public

PREFIX = previous.PREFIX + r'''
dec $test_two_trait_front(pstate, nat) : bool
def $test_two_trait_front(S,0) = true
  -- if S.TODO = (AUTO_PUBLISH porigin) :: ptask_tail*
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C116")
def $test_two_trait_front(S,1) = true
  -- if S.TODO = (AUTO_TRAIT porigin preqbytes) :: ptask_tail*
  -- if preqbytes = $ptascii("T116A")
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C116")
def $test_two_trait_front(S,2) = true
  -- if S.TODO = (AUTO_TRAIT porigin preqbytes) :: ptask_tail*
  -- if preqbytes = $ptascii("T116B")
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C116")
def $test_two_trait_front(S,3) = true
  -- if S.TODO = (AUTO_INTERFACE porigin preqbytes) :: ptask_tail*
  -- if preqbytes = $ptascii("I116")
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("C116")
def $test_two_trait_front(S,n) = false -- otherwise
dec $test_two_trait_seek(pstate, nat, nat) : pstate
def $test_two_trait_seek(S,n_phase,0) = S
def $test_two_trait_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_two_trait_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_two_trait_seek(S,n_phase,n) = $test_two_trait_seek($drive_steps($test_iface_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_two_trait_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, prior, phase):
    return [f'{state}_found = $test_two_trait_seek({prior},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$test_two_trait_front({state},{phase})', *public(state)]


def step(state, prior):
    return iface.prior.step(state, prior)


def eval_stage(checks, label, prior, unit, source, response, phase):
    wait, body, post = 'S_wait' + label, 'S_body' + label, 'S_post' + label
    inner, outer = 'pevalcontext_' + label, 'pevalcontext_outer_' + label
    checks += [f'{wait} = $drive_steps({prior},5000)',
        f'{wait}.COMPLETION = SOURCE_PENDING',
        f'{wait}.EVALCONTEXTS = {inner} :: {outer} :: eps',
        f'{inner}.UNIT = {unit}', f'{inner}.BYTES = ' + term(source),
        f'{outer}.UNIT = 1', *public(wait),
        f'$eval_response_valid({wait},{response})',
        f'{body} = $eval_resume({wait},{response})',
        *reach(post, body, phase)]
    return post


def assertions(case, main, code, response, expected, mode):
    p, a, b, i, c = [f'$ptascii("{name}")' for name in
        ('P116', 'T116A', 'T116B', 'I116', 'C116')]
    checks = [
        'S_wait0 = $php_run(' + main + ',5000,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
        'S_wait0.COMPLETION = SOURCE_PENDING',
        'S_wait0.EVALCONTEXTS = pevalcontext_0 :: eps',
        'pevalcontext_0.UNIT = 1', 'pevalcontext_0.BYTES = ' + term(code['class']),
        *public('S_wait0'), '$eval_response_valid(S_wait0,' + response['class'] + ')',
        'S_body = $eval_resume(S_wait0,' + response['class'] + ')',
        *iface.prior.reach('S_decl', 'S_body', 3, 'C116'),
        'S_decl.ORIGIN = (porigin_target)',
        'porigin_target = PORIGIN 1 pcpath_target',
        '$class_at(S_decl.CLASSES,porigin_target) = (pclassdesc_target)',
        'pclassdesc_target.KIND = "class"',
        'pclassdesc_target.NAME = ' + c,
        'pclassdesc_target.PARENT = (' + p + ')',
        'pclassdesc_target.INTERFACES = [' + i + ']',
        '$trait_plan(S_decl,pclassdesc_target) = ptraitplan',
        'ptraitplan.TRAITS = [' + a + ',' + b + ']',
        '$autoload_two_trait_plan(ptraitplan)',
        '~$trait_parent_available(S_decl,pclassdesc_target)',
        '~$autoload_trait_source(S_decl,porigin_target,' + a + ')',
        '~$autoload_interface_source(S_decl,porigin_target,' + i + ')',
        '$class_named(S_decl.CLASSNAMES,$ptlc(' + c + ')) = eps',
    ]
    if mode == 'adapted-methods':
        checks += [
            'ptraitplan.PRECEDENCES = [ptraitprecedence_checked]',
            'ptraitprecedence_checked.TRAIT = ' + a,
            'ptraitprecedence_checked.EXCLUDES = [' + b + ']',
            'ptraitplan.ALIASES = [ptraitalias_checked]',
            'ptraitalias_checked.TRAIT = (' + b + ')',
            'ptraitalias_checked.METHOD = ptraitprecedence_checked.METHOD',
            'ptraitalias_checked.MODIFIERS = 0',
            'ptraitalias_checked.NAME = ($ptascii("f2"))',
        ]
    else:
        checks += ['ptraitplan.PRECEDENCES = eps', 'ptraitplan.ALIASES = eps']
    checks += [
        *step('S_nextP', 'S_decl'),
        'S_nextP.TODO = (AUTO_NEXT pautoloadcall_P) :: ptask_P*',
        'pautoloadcall_P.RESUME = AUTO_PUBLISH porigin_target',
        '$autoload_resume_valid(S_nextP,pautoloadcall_P)', *public('S_nextP'),
        'pclassdesc_fake_parent = pclassdesc_target[.PARENT = (' + i + ')]',
        'S_fake_parent = S_nextP[.CLASSES = $test_iface_replace(S_nextP.CLASSES,pclassdesc_fake_parent)]',
        '$declaration_entry_check(S_fake_parent).COMPLETION = UNSUPPORTED "invalid declaration publication history"',
        '~$call_descriptors_valid(S_fake_parent)',
    ]
    post = eval_stage(checks, 'P', 'S_nextP', 2, code['P'], response['P'], 0)
    checks += [
        post + '.TODO = (AUTO_PUBLISH porigin_target) :: ptask_postP*',
        '$trait_parent_available(' + post + ',pclassdesc_target)',
        '$autoload_trait_pending(' + post + ',pclassdesc_target)',
        '$autoload_trait_source(' + post + ',porigin_target,' + a + ')',
        '~$autoload_two_trait_target(' + post + ',ptraitplan.TRAITS,' + b + ')',
        '~$autoload_interface_pending(' + post + ',pclassdesc_target)',
        '$class_named(' + post + '.CLASSNAMES,$ptlc(' + c + ')) = eps',
    ]
    if mode == 'adapted-methods':
        checks += ['S_final = $drive_steps(' + post + ',5000)',
            'S_final.COMPLETION = SOURCE_PENDING',
            '$declaration_entry_check(' + post + ') = ' + post]
        return checks
    checks += [
        *step('S_nextA', post),
        'S_nextA.TODO = (AUTO_NEXT pautoloadcall_A) :: ptask_A*',
        'pautoloadcall_A.RESUME = AUTO_TRAIT porigin_target ' + a,
        '$autoload_resume_valid(S_nextA,pautoloadcall_A)', *public('S_nextA'),
        'pautoloadcall_early = pautoloadcall_A[.NAME = ' + b + '][.KEY = $ptascii("t116b")][.RESUME = AUTO_TRAIT porigin_target ' + b + ']',
        'S_early = S_nextA[.TODO = (AUTO_NEXT pautoloadcall_early) :: ptask_A*]',
        '~$autoload_trait_source(S_early,porigin_target,' + b + ')',
        '~$autoload_resume_valid(S_early,pautoloadcall_early)',
        '~$call_descriptors_valid(S_early)',
    ]
    post = eval_stage(checks, 'A', 'S_nextA', 3, code['A'], response['A'], 1)
    checks += [
        post + '.TODO = (AUTO_TRAIT porigin_target ' + a + ') :: ptask_postA*',
        '$trait_fetch(' + post + ',ptraitplan.TRAITS,eps) = TRAITMISSING ' + b,
        '$autoload_two_trait_target(' + post + ',ptraitplan.TRAITS,' + b + ')',
        '$autoload_trait_source(' + post + ',porigin_target,' + b + ')',
        '$autoload_trait_pending(' + post + ',pclassdesc_target)',
        '~$autoload_interface_pending(' + post + ',pclassdesc_target)',
        '$class_named(' + post + '.CLASSNAMES,$ptlc(' + c + ')) = eps',
        *step('S_nextB', post),
        'S_nextB.TODO = (AUTO_NEXT pautoloadcall_B) :: ptask_B*',
        'pautoloadcall_B.RESUME = AUTO_TRAIT porigin_target ' + b,
        '$autoload_resume_valid(S_nextB,pautoloadcall_B)', *public('S_nextB'),
        'S_budgetB = $drive_steps(S_nextB,0)',
        'S_budgetB = S_nextB[.COMPLETION = BUDGET]',
        'S_resumeB = S_budgetB[.COMPLETION = NORMAL]',
        'S_resumeB = S_nextB',
    ]
    if mode == 'second-trait-missing':
        checks += [
            *reach('S_postB', 'S_resumeB', 2),
            'S_postB.TODO = (AUTO_TRAIT porigin_target ' + b + ') :: ptask_postB*',
            '$autoload_trait_source(S_postB,porigin_target,' + b + ')',
            '~$autoload_interface_pending(S_postB,pclassdesc_target)',
            'S_throw_budget = $drive_steps(S_postB,1)',
            'S_throw_budget.COMPLETION = BUDGET',
            'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
            'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
            'S_throw.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "Error"',
            '$string_bytes($throwable_field(S_throw,n_error,"message")) = ' +
                term(b'Trait "T116B" not found'),
            '$class_named(S_throw.CLASSNAMES,$ptlc(' + c + ')) = eps',
            *public('S_throw'),
            'S_final = $drive_steps(S_throw,5000)',
        ]
    else:
        post = eval_stage(checks, 'B', 'S_resumeB', 4, code['B'], response['B'], 2)
        checks += [
            post + '.TODO = (AUTO_TRAIT porigin_target ' + b + ') :: ptask_postB*',
            '$trait_fetch(' + post + ',ptraitplan.TRAITS,eps) = TRAITFETCHED ([pclassdesc_first,pclassdesc_second])',
            'pclassdesc_first.KIND = "trait"', 'pclassdesc_second.KIND = "trait"',
            '$autoload_interface_pending(' + post + ',pclassdesc_target)',
            '$autoload_interface_source(' + post + ',porigin_target,' + i + ')',
            '$class_named(' + post + '.CLASSNAMES,$ptlc(' + c + ')) = eps',
            *step('S_nextI', post),
            'S_nextI.TODO = (AUTO_NEXT pautoloadcall_I) :: ptask_I*',
            'pautoloadcall_I.RESUME = AUTO_INTERFACE porigin_target ' + i,
            '$autoload_resume_valid(S_nextI,pautoloadcall_I)', *public('S_nextI'),
        ]
        post = eval_stage(checks, 'I', 'S_nextI', 5, code['I'], response['I'], 3)
        checks += [post + '.TODO = (AUTO_INTERFACE porigin_target ' + i + ') :: ptask_postI*',
            '$autoload_interface_source(' + post + ',porigin_target,' + i + ')',
            *step('S_linked', post),
            '$class_named(S_linked.CLASSNAMES,$ptlc(' + c + ')) = (porigin_target)',
            *public('S_linked'), 'S_final = $drive_steps(S_linked,5000)']
    checks += ['S_final.COMPLETION = NORMAL', 'S_final.EXITSTATUS = 0',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '$test_iface_outputs(S_final.EVENTS) = ' + term(expected), *public('S_final')]
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
            strings = [base64.b64decode(node['fields'][0]['bytes']) for node in iface.nodes(parsed['ast'])
                if node['node'] == 'Scalar_String']
            codes = {'class': next(value for value in strings if value.startswith(
                b'function mark116(){') or value.startswith(b'class C116 extends')),
                'P': next(value for value in strings if value.startswith(b'class P116 ')),
                'A': next(value for value in strings if value.startswith(b'trait T116A '))}
            if name == 'ordered-methods':
                codes.update(B=next(value for value in strings if value.startswith(b'trait T116B ')),
                    I=next(value for value in strings if value == b'interface I116 {}'))
            responses = {label: iface.response(frontend, adapter, value, unit)
                for unit, (label, value) in enumerate(codes.items(), 1)}
            checks = assertions(case, checked['fixture'], codes, responses,
                base64.b64decode(row['predicted_stdout']), name)
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
    paths = [Path(__file__), Path(previous.__file__), Path(iface.__file__),
        Path(iface.prior.__file__),
        ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/277-autoload.watsup',
        ROOT / 'spec/semantics/228-trait-methods.watsup',
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

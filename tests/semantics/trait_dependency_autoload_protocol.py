#!/usr/bin/env python3
"""Reached trait-dependency autoload before composition and publication."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
CASES = {'class': 'class-uses-trait', 'trait': 'composed-trait-uses-trait'}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'

PREFIX = r'''
dec $test_trait_outputs(pevent*) : nat*
dec $test_trait_output(pevent) : nat*
def $test_trait_output(OUTPUT n*) = n*
def $test_trait_output(pevent) = eps -- otherwise
def $test_trait_outputs(eps) = eps
def $test_trait_outputs(pevent :: pevent_tail*) = $test_trait_output(pevent) ++ $test_trait_outputs(pevent_tail*)
dec $test_trait_running(pstate) : pstate
def $test_trait_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_trait_running(S) = S -- otherwise
dec $test_trait_descriptor(pclassdesc*, preqbytes) : pclassdesc?
def $test_trait_descriptor(eps, preqbytes) = eps
def $test_trait_descriptor(pclassdesc :: pclassdesc_tail*, preqbytes) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptlc(preqbytes)
def $test_trait_descriptor(pclassdesc :: pclassdesc_tail*, preqbytes) = $test_trait_descriptor(pclassdesc_tail*,preqbytes)
  -- if $ptlc(pclassdesc.NAME) =/= $ptlc(preqbytes)
dec $test_trait_replace(pclassdesc*, pclassdesc) : pclassdesc*
def $test_trait_replace(eps, pclassdesc) = eps
def $test_trait_replace(pclassdesc :: pclassdesc_tail*, pclassdesc_new) = pclassdesc_new :: pclassdesc_tail*
  -- if pclassdesc.ORIGIN = pclassdesc_new.ORIGIN
def $test_trait_replace(pclassdesc :: pclassdesc_tail*, pclassdesc_new) = pclassdesc :: $test_trait_replace(pclassdesc_tail*,pclassdesc_new)
  -- if pclassdesc.ORIGIN =/= pclassdesc_new.ORIGIN
dec $test_trait_front(pstate, nat, preqbytes) : bool
def $test_trait_front(S,0,preqbytes_target) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.RESUME = AUTO_TRAIT porigin preqbytes
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
def $test_trait_front(S,1,preqbytes_target) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))
  -- if pautoloadcall.RESUME = AUTO_TRAIT porigin preqbytes
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
def $test_trait_front(S,2,preqbytes_target) = true
  -- if S.TODO = (AUTO_TRAIT porigin preqbytes) :: ptask_tail*
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
def $test_trait_front(S,3,preqbytes_target) = true
  -- if S.TODO = (STMT statement) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
  -- if $origin_node(S.SOURCES,porigin) = (statement)
def $test_trait_front(S,n,preqbytes_target) = false -- otherwise
dec $test_trait_seek(pstate, nat, preqbytes, nat) : pstate
def $test_trait_seek(S,n_phase,preqbytes,0) = S
def $test_trait_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_trait_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_trait_seek(S,n_phase,preqbytes,n) = $test_trait_seek($drive_steps($test_trait_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_trait_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return [f'$call_descriptors_valid({state})', f'$declaration_entry_check({state}) = {state}',
        f'$heap_valid($heap_graph({state}))']


def reach(state, previous, phase, target):
    args = str(phase) + ',$ptascii(' + json.dumps(target) + ')'
    return [f'{state}_found = $test_trait_seek({previous},{args},4000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$test_trait_front({state},{args})', *public(state)]


def step(state, previous):
    return [f'{state}_found = $drive_steps({previous},1)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]']


def assertions(initial, target, dependency, kind, stdout):
    checks = [*initial, *reach('S_decl','S_initial',3,target),
        'S_decl.ORIGIN = (porigin_target)', '$class_at(S_decl.CLASSES,porigin_target) = (pclassdesc_target)',
        'pclassdesc_target.KIND = ' + json.dumps(kind), 'pclassdesc_target.METHODS = eps',
        'pclassdesc_target.PARENT = eps', 'pclassdesc_target.INTERFACES = eps',
        '$trait_plan(S_decl,pclassdesc_target) = ptraitplan',
        'ptraitplan.TRAITS = [$ptascii(' + json.dumps(dependency) + ')]',
        'ptraitplan.PRECEDENCES = eps', 'ptraitplan.ALIASES = eps',
        '$test_trait_descriptor(S_decl.CLASSES,$ptascii(' + json.dumps(dependency) + ')) = (pclassdesc_dependency)',
        'pclassdesc_dependency.KIND = "trait"', 'porigin_dependency = pclassdesc_dependency.ORIGIN',
        'pclassdesc_dependency.METHODS = [pmethoddesc_value_raw,pmethoddesc_origin_raw]',
        'pmethoddesc_value_raw.NAME = $ptascii("value")', 'pmethoddesc_origin_raw.NAME = $ptascii("origin")',
        'pmethoddesc_value_raw.OWNER = porigin_dependency', 'pmethoddesc_origin_raw.OWNER = porigin_dependency',
        'porigin_value_raw = pmethoddesc_value_raw.FUNCTION.ORIGIN',
        'porigin_origin_raw = pmethoddesc_origin_raw.FUNCTION.ORIGIN',
        '$origin_source(porigin_value_raw) = porigin_value_raw', '$origin_source(porigin_origin_raw) = porigin_origin_raw',
        '$class_named(S_decl.CLASSNAMES,$ptlc(pclassdesc_dependency.NAME)) = eps',
        '$class_named(S_decl.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = eps',
        '$trait_fetch(S_decl,ptraitplan.TRAITS,eps) = TRAITMISSING pclassdesc_dependency.NAME',
        '$autoload_trait_pending(S_decl,pclassdesc_target)', '~$autoload_parent_pending(S_decl,pclassdesc_target)',
        '~$autoload_interface_pending(S_decl,pclassdesc_target)',
        '$autoload_trait_source(S_decl,porigin_target,pclassdesc_dependency.NAME)',
        '$test_trait_outputs(S_decl.EVENTS) = ' + term(b'B|'),
        'pclassdesc_role = pclassdesc_target[.KIND = ' + json.dumps('trait' if kind == 'class' else 'class') + ']',
        'S_role = S_decl[.CLASSES = $test_trait_replace(S_decl.CLASSES,pclassdesc_role)]',
        '$autoload_trait_pending(S_role,pclassdesc_role)',
        '~$autoload_trait_source(S_role,porigin_target,pclassdesc_dependency.NAME)',
        '$activate_class(S_role,pclassdesc_role) = S_role[.COMPLETION = UNSUPPORTED "trait autoload declaration source domain"]',
        *step('S_next','S_decl'), '$test_trait_front(S_next,0,$ptascii(' + json.dumps(target) + '))',
        *public('S_next'), 'S_next.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*',
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadcall.SITE = porigin_target',
        'pautoloadcall.RESUME = AUTO_TRAIT porigin_target pclassdesc_dependency.NAME',
        'pautoloadcall.NAME = pclassdesc_dependency.NAME', 'pautoloadcall.KEY = $ptlc(pautoloadcall.NAME)',
        'pautoloadcall.LINE = pclassdesc_target.LINE', 'pautoloadcall.INDEX = 0', 'pautoloadcall.BIRTH = eps',
        '$autoload_call_valid(S_next,pautoloadcall)', '$autoload_declaration_resume(S_next,pautoloadcall)',
        '$task_nodes(pautoloadcall.RESUME) = eps', 'S_next.CLASSES = S_decl.CLASSES',
        'S_next.CLASSNAMES = S_decl.CLASSNAMES', 'S_next.OBJECTS = S_decl.OBJECTS',
        'S_next.EVENTS = S_decl.EVENTS']
    if kind == 'class':
        checks += ['S_pause = $drive_steps(S_next,0)', 'S_pause = S_next[.COMPLETION = BUDGET]',
            'S_resume = S_pause[.COMPLETION = NORMAL]', 'S_resume = S_next']
        previous = 'S_resume'
    else:
        previous = 'S_next'
    # These are undriven local projections, never an asserted parent campaign.
    if kind == 'class':
        checks += ['pclassdesc_parent = pclassdesc_target[.PARENT = ($ptascii("OtherParent"))]',
            'S_parent = S_decl[.CLASSES = $test_trait_replace(S_decl.CLASSES,pclassdesc_parent)]',
            '$autoload_parent_pending(S_parent,pclassdesc_parent)',
            '~$autoload_trait_pending(S_parent,pclassdesc_parent)',
            'pautoloadcall_parent = pautoloadcall[.NAME = $ptascii("OtherParent")][.KEY = $ptascii("otherparent")]',
            'S_active_parent = S_next[.CLASSES = $test_trait_replace(S_next.CLASSES,pclassdesc_parent)][.TODO = (AUTO_NEXT pautoloadcall_parent) :: ptask_tail*]',
            '~$autoload_parent_pending(S_active_parent,pclassdesc_parent)',
            '~$trait_parent_available(S_active_parent,pclassdesc_parent)',
            '$autoload_pending(S_active_parent,pclassdesc_dependency.NAME)',
            '~$autoload_trait_pending(S_active_parent,pclassdesc_parent)',
            '~$call_descriptors_valid(S_active_parent)',
            'pclassdesc_interfaces = pclassdesc_target[.INTERFACES = [$ptascii("OtherInterface")]]',
            'S_interfaces = S_decl[.CLASSES = $test_trait_replace(S_decl.CLASSES,pclassdesc_interfaces)]',
            '$autoload_trait_pending(S_interfaces,pclassdesc_interfaces)',
            '~$autoload_interface_pending(S_interfaces,pclassdesc_interfaces)',
            '~$call_descriptors_valid(S_interfaces)',
            'pclassdesc_derived = pclassdesc_target[.INTERFACES = [$ptascii("Stringable")]]',
            'S_derived = S_decl[.CLASSES = $test_trait_replace(S_decl.CLASSES,pclassdesc_derived)]',
            '$autoload_trait_source(S_derived,porigin_target,pclassdesc_dependency.NAME)',
            '~$call_descriptors_valid(S_derived)']
    for label, call in [
        ('site','pautoloadcall[.SITE = porigin_dependency]'),
        ('name','pautoloadcall[.NAME = $ptascii("OtherTrait")]'),
        ('key','pautoloadcall[.KEY = $ptascii("wrong")]'),
        ('line','pautoloadcall[.LINE = $(pautoloadcall.LINE + 1)]'),
        ('resume','pautoloadcall[.RESUME = AUTO_INTERFACE porigin_target pclassdesc_dependency.NAME]'),
    ]:
        state = 'S_bad_' + label
        checks += [f'{state} = S_next[.TODO = (AUTO_NEXT {call}) :: ptask_tail*]',
            f'{state}.AUTOLOAD = S_next.AUTOLOAD', f'~$autoload_resume_valid({state},{call})',
            f'~$call_descriptors_valid({state})']
    checks += ['pclassdesc_line = pclassdesc_target[.LINE = $(pclassdesc_target.LINE + 1)]',
        'pautoloadcall_line = pautoloadcall[.LINE = pclassdesc_line.LINE]',
        'S_line = S_next[.CLASSES = $test_trait_replace(S_next.CLASSES,pclassdesc_line)][.TODO = (AUTO_NEXT pautoloadcall_line) :: ptask_tail*]',
        '$autoload_resume_valid(S_line,pautoloadcall_line)', '~$call_descriptors_valid(S_line)',
        *reach('S_loader',previous,1,target), 'S_loader.CURRENT = (pcallcontext)',
        '$autoload_context_call(pcallcontext,S_loader.CURRENT,S_loader.FRAMES) = ((pautoloadcall_entered,pautoloadentry,poperand))',
        'pautoloadcall_entered.SITE = pautoloadcall.SITE', 'pautoloadcall_entered.NAME = pautoloadcall.NAME',
        'pautoloadcall_entered.KEY = pautoloadcall.KEY', 'pautoloadcall_entered.LINE = pautoloadcall.LINE',
        'pautoloadcall_entered.MODE = pautoloadcall.MODE', 'pautoloadcall_entered.RESUME = pautoloadcall.RESUME',
        'pautoloadcall_entered.BIRTH = pautoloadentry.BIRTH', 'pautoloadcall_entered.BIRTH =/= eps',
        'poperand = KNOWN (PSTRING pclassdesc_dependency.NAME)',
        '$autoload_context_valid(S_loader,pcallcontext)',
        '$class_named(S_loader.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = eps',
        '$class_named(S_loader.CLASSNAMES,$ptlc(pclassdesc_dependency.NAME)) = eps',
        'S_loader.OBJECTS = S_next.OBJECTS',
        *reach('S_post','S_loader',2,target),
        'S_post.TODO = (AUTO_TRAIT porigin_target pclassdesc_dependency.NAME) :: ptask_post*',
        '$class_named(S_post.CLASSNAMES,$ptlc(pclassdesc_dependency.NAME)) = (porigin_dependency)',
        '$class_named(S_post.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = eps',
        '$autoload_trait_source(S_post,porigin_target,pclassdesc_dependency.NAME)',
        '$call_task_valid(S_post,pautoloadcall.RESUME)', '$autoload_resume_valid(S_post,pautoloadcall)',
        '$trait_fetch(S_post,ptraitplan.TRAITS,eps) = TRAITFETCHED ([pclassdesc_dependency])',
        'S_post.CLASSES = S_next.CLASSES', 'S_post.OBJECTS = S_next.OBJECTS',
        'S_post.AUTOLOAD = S_next.AUTOLOAD',
        '$test_trait_outputs(S_post.EVENTS) = ' + term(('B|L:' + dependency + '|').encode()),
        *step('S_imported','S_post'), *public('S_imported'),
        '$class_named(S_imported.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = (porigin_target)',
        '$class_at(S_imported.CLASSES,porigin_target) = (pclassdesc_imported)',
        'pclassdesc_imported.METHODS = [pmethoddesc_value,pmethoddesc_origin]',
        'pclassdesc_imported.KIND = pclassdesc_target.KIND', 'pclassdesc_imported.NAME = pclassdesc_target.NAME',
        '$class_at(S_imported.CLASSES,porigin_dependency) = (pclassdesc_dependency)',
        '$autoload_trait_source(S_imported,porigin_target,pclassdesc_dependency.NAME)',
        '$autoload_declaration_resume(S_imported,pautoloadcall)',
        'S_imported.OBJECTS = S_post.OBJECTS', 'S_imported.EVENTS = S_post.EVENTS']
    for name in ('value','origin'):
        method = 'pmethoddesc_' + name
        raw = method + '_raw'
        source = 'porigin_' + name + '_raw'
        checks += [method + '.NAME = ' + raw + '.NAME', method + '.OWNER = porigin_target',
            method + '.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_target ' + source + ' ' + raw + '.NAME',
            '$origin_source(' + method + '.FUNCTION.ORIGIN) = ' + source,
            method + '.FUNCTION.BODY = ' + raw + '.FUNCTION.BODY',
            method + '.FUNCTION.NAME = pclassdesc_target.NAME ++ $ptascii("::") ++ ' + raw + '.NAME',
            '$class_method_origin(S_imported.CLASSES,' + method + '.FUNCTION.ORIGIN) = (' + method + ')']
    consumer = target if kind == 'class' else 'V56NestedConsumer'
    checks += ['S_final = $drive_steps(S_imported,4000)',
        r'S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps',
        '$test_trait_outputs(S_final.EVENTS) = ' + term(stdout.encode()), *public('S_final'),
        '$class_named(S_final.CLASSNAMES,$ptascii(' + json.dumps(consumer.lower()) + ')) = (porigin_consumer)',
        '$class_at(S_final.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
        '$method_named(pclassdesc_consumer.METHODS,$ptascii("origin")) = (pmethoddesc_final)',
        'pmethoddesc_final.OWNER = porigin_consumer',
        'pmethoddesc_final.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_consumer porigin_origin_raw $ptascii("origin")',
        '$origin_source(pmethoddesc_final.FUNCTION.ORIGIN) = porigin_origin_raw']
    return checks


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def prepare(out, sources):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        native = json.loads((sources / 'static-native-v56/report.json').read_text())
        assert native['result'] == 'native_observation' and native['stable_inputs'] and native['target'] == types.PROFILE
        for stage, name in CASES.items():
            case = sources / 'static-native-v56' / name
            row, = [item for item in native['records'] if item['id'] == name]
            assert row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            initial = ['S_run = $php_run(' + main + ',0,' + json.dumps(b64(str(case / 'main.php').encode())) + ')']
            if stage == 'class':
                initial = ['S_wait = $php_run(' + main + ',2500,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
                    'S_wait.COMPLETION = SOURCE_PENDING', *public('S_wait')]
                code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                    if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'class V56Consumer ')]
                unit = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                    'profile': 'cli-raw-85', 'source': b64(code)})
                assert unit['accepted']
                checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
                response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked
                initial += ['$eval_response_valid(S_wait,' + response + ')',
                    'S_run = $eval_resume(S_wait,' + response + ')']
            initial += ['S_initial = $test_trait_running(S_run)', '~S_initial.COMPILESTOP']
            checks = assertions(initial, 'V56Consumer' if stage == 'class' else 'V56Outer',
                'V56Trait' if stage == 'class' else 'V56Inner', stage, row['stdout'])
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks,indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
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
    args = parser.parse_args()
    selected = list(CASES)
    sources, out = args.sources.resolve(), args.output.resolve()
    suite = sources / 'static-native-v56'
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php',
        ROOT / 'adapter/wire.ml', suite / 'run.py', suite / 'report.json']
    for name in CASES.values():
        case = suite / name
        paths += [case / 'main.php', *[case / 'native' / item for item in ['stdout','stderr','process.json','command.json']]]
    if args.phase == 'check':
        for stage in selected:
            paths += [out / stage / 'protocol.watsup', out / stage / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    assert not (out / (args.phase + '-report.json')).exists()
    report = {'phase': args.phase, 'selected': selected, 'revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','spec/semantics'],cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'sl_timeout': 90, 'result': 'fail', 'records': [], 'agreement_credit': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out,sources)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for stage in selected:
                target = out / stage
                assert not (target / 'check').exists()
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*modules,
                    str(target / 'protocol.watsup')],target / 'check',90,ROOT)
                passed = runner.returncode == 0 and runner.stdout == b'true\n' and not runner.stderr
                report['records'].append({'id': stage, 'pass': passed, 'runner_exit': runner.returncode,
                    'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]),flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(selected) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'],record['premises'] = False,0
        (out / (args.phase + '-report.json')).write_text(json.dumps(report,indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

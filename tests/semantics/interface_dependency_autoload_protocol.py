#!/usr/bin/env python3
"""Reached declaration-interface autoload before linking and publication."""
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
CASES = {'class': 'class-implements-interface', 'interface': 'interface-extends-interface'}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'

PREFIX = r'''
dec $test_iface_outputs(pevent*) : nat*
dec $test_iface_output(pevent) : nat*
def $test_iface_output(OUTPUT n*) = n*
def $test_iface_output(pevent) = eps -- otherwise
def $test_iface_outputs(eps) = eps
def $test_iface_outputs(pevent :: pevent_tail*) = $test_iface_output(pevent) ++ $test_iface_outputs(pevent_tail*)
dec $test_iface_running(pstate) : pstate
def $test_iface_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_iface_running(S) = S -- otherwise
dec $test_iface_descriptor(pclassdesc*, preqbytes) : pclassdesc?
def $test_iface_descriptor(eps, preqbytes) = eps
def $test_iface_descriptor(pclassdesc :: pclassdesc_tail*, preqbytes) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptlc(preqbytes)
def $test_iface_descriptor(pclassdesc :: pclassdesc_tail*, preqbytes) = $test_iface_descriptor(pclassdesc_tail*,preqbytes)
  -- if $ptlc(pclassdesc.NAME) =/= $ptlc(preqbytes)
dec $test_iface_replace(pclassdesc*, pclassdesc) : pclassdesc*
def $test_iface_replace(eps, pclassdesc) = eps
def $test_iface_replace(pclassdesc :: pclassdesc_tail*, pclassdesc_new) = pclassdesc_new :: pclassdesc_tail*
  -- if pclassdesc.ORIGIN = pclassdesc_new.ORIGIN
def $test_iface_replace(pclassdesc :: pclassdesc_tail*, pclassdesc_new) = pclassdesc :: $test_iface_replace(pclassdesc_tail*,pclassdesc_new)
  -- if pclassdesc.ORIGIN =/= pclassdesc_new.ORIGIN
dec $test_iface_front(pstate, nat, preqbytes) : bool
def $test_iface_front(S,0,preqbytes_target) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.RESUME = AUTO_INTERFACE porigin preqbytes
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
def $test_iface_front(S,1,preqbytes_target) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))
  -- if pautoloadcall.RESUME = AUTO_INTERFACE porigin preqbytes
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
def $test_iface_front(S,2,preqbytes_target) = true
  -- if S.TODO = (AUTO_INTERFACE porigin preqbytes) :: ptask_tail*
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
def $test_iface_front(S,3,preqbytes_target) = true
  -- if S.TODO = (STMT statement) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.NAME = preqbytes_target
  -- if $origin_node(S.SOURCES,porigin) = (statement)
def $test_iface_front(S,n,preqbytes_target) = false -- otherwise
dec $test_iface_seek(pstate, nat, preqbytes, nat) : pstate
def $test_iface_seek(S,n_phase,preqbytes,0) = S
def $test_iface_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_iface_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_iface_seek(S,n_phase,preqbytes,n) = $test_iface_seek($drive_steps($test_iface_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_iface_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return [f'$call_descriptors_valid({state})', f'$declaration_entry_check({state}) = {state}',
        f'$heap_valid($heap_graph({state}))']


def reach(state, previous, phase, target):
    args = str(phase) + ',$ptascii(' + json.dumps(target) + ')'
    return [f'{state}_found = $test_iface_seek({previous},{args},4000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$test_iface_front({state},{args})', *public(state)]


def step(state, previous):
    return [f'{state}_found = $drive_steps({previous},1)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]']


def assertions(initial, target, dependency, kind, stdout):
    checks = [*initial, *reach('S_decl','S_initial',3,target),
        'S_decl.ORIGIN = (porigin_target)', '$class_at(S_decl.CLASSES,porigin_target) = (pclassdesc_target)',
        'pclassdesc_target.KIND = ' + json.dumps(kind),
        'pclassdesc_target.INTERFACES = [$ptascii(' + json.dumps(dependency) + ')]',
        'pclassdesc_target.PARENT = eps', '$trait_plan(S_decl,pclassdesc_target).TRAITS = eps',
        '$test_iface_descriptor(S_decl.CLASSES,$ptascii(' + json.dumps(dependency) + ')) = (pclassdesc_dependency)',
        'pclassdesc_dependency.KIND = "interface"', 'porigin_dependency = pclassdesc_dependency.ORIGIN',
        '$class_named(S_decl.CLASSNAMES,$ptlc(pclassdesc_dependency.NAME)) = eps',
        '$class_named(S_decl.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = eps',
        '$pil_at(S_decl.LINKEDINTERFACES,porigin_target) = eps',
        '$autoload_interface_pending(S_decl,pclassdesc_target)', '~$autoload_parent_pending(S_decl,pclassdesc_target)',
        '$autoload_interface_missing(S_decl,pclassdesc_target.INTERFACES) = (pclassdesc_dependency.NAME)',
        '$autoload_interface_source(S_decl,porigin_target,pclassdesc_dependency.NAME)',
        '$test_iface_outputs(S_decl.EVENTS) = ' + term(b'B|')]
    # Pure source projections never enter the driver.
    checks += ['pclassdesc_list = pclassdesc_target[.INTERFACES = pclassdesc_target.INTERFACES ++ [$ptascii("OtherInterface")]]',
        'S_list = S_decl[.CLASSES = $test_iface_replace(S_decl.CLASSES,pclassdesc_list)]',
        '$autoload_interface_pending(S_list,pclassdesc_list)',
        '~$autoload_interface_source(S_list,porigin_target,pclassdesc_dependency.NAME)',
        'S_list_result = $activate_class(S_list,pclassdesc_list)',
        'S_list_result.COMPLETION = UNSUPPORTED "interface autoload declaration source domain"',
        'S_list_result = S_list[.COMPLETION = UNSUPPORTED "interface autoload declaration source domain"]',
        'pclassdesc_internal = pclassdesc_target[.NAME = $ptascii("Exception")]',
        'S_internal = S_decl[.CLASSES = $test_iface_replace(S_decl.CLASSES,pclassdesc_internal)]',
        '~$autoload_interface_source(S_internal,porigin_target,pclassdesc_dependency.NAME)']
    if kind == 'class':
        checks += ['pclassdesc_parent = pclassdesc_target[.PARENT = ($ptascii("OtherParent"))]',
            'S_parent = S_decl[.CLASSES = $test_iface_replace(S_decl.CLASSES,pclassdesc_parent)]',
            '$autoload_parent_pending(S_parent,pclassdesc_parent)',
            '~$autoload_interface_pending(S_parent,pclassdesc_parent)',
            '~$autoload_interface_source(S_parent,porigin_target,pclassdesc_dependency.NAME)']
    checks += [*step('S_next','S_decl'), '$test_iface_front(S_next,0,$ptascii(' + json.dumps(target) + '))',
        *public('S_next'), 'S_next.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*',
        'pautoloadcall.MODE = AUTO_LOOKUP', 'pautoloadcall.SITE = porigin_target',
        'pautoloadcall.RESUME = AUTO_INTERFACE porigin_target pclassdesc_dependency.NAME',
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
    for label, call in [
        ('site','pautoloadcall[.SITE = porigin_dependency]'),
        ('name','pautoloadcall[.NAME = $ptascii("OtherInterface")]'),
        ('key','pautoloadcall[.KEY = $ptascii("wrong")]'),
        ('line','pautoloadcall[.LINE = $(pautoloadcall.LINE + 1)]'),
        ('resume','pautoloadcall[.RESUME = AUTO_PUBLISH porigin_target]'),
    ]:
        state = 'S_bad_' + label
        checks += [f'{state} = S_next[.TODO = (AUTO_NEXT {call}) :: ptask_tail*]',
            f'{state}.AUTOLOAD = S_next.AUTOLOAD', f'~$autoload_resume_valid({state},{call})',
            f'~$call_descriptors_valid({state})']
    # These local certificates intentionally rely on the whole compiler image.
    checks += ['pclassdesc_line = pclassdesc_target[.LINE = $(pclassdesc_target.LINE + 1)]',
        'pautoloadcall_line = pautoloadcall[.LINE = pclassdesc_line.LINE]',
        'S_line = S_next[.CLASSES = $test_iface_replace(S_next.CLASSES,pclassdesc_line)][.TODO = (AUTO_NEXT pautoloadcall_line) :: ptask_tail*]',
        '$autoload_resume_valid(S_line,pautoloadcall_line)', '~$call_descriptors_valid(S_line)',
        'pclassdesc_name = pclassdesc_target[.INTERFACES = [$ptascii("OtherInterface")]]',
        'pautoloadcall_name = pautoloadcall[.NAME = $ptascii("OtherInterface")][.KEY = $ptascii("otherinterface")][.RESUME = AUTO_INTERFACE porigin_target $ptascii("OtherInterface")]',
        'S_name = S_next[.CLASSES = $test_iface_replace(S_next.CLASSES,pclassdesc_name)][.TODO = (AUTO_NEXT pautoloadcall_name) :: ptask_tail*]',
        '$autoload_resume_valid(S_name,pautoloadcall_name)', '~$call_descriptors_valid(S_name)',
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
        '$pil_at(S_loader.LINKEDINTERFACES,porigin_target) = eps',
        'S_loader.OBJECTS = S_next.OBJECTS',
        *reach('S_post','S_loader',2,target),
        'S_post.TODO = (AUTO_INTERFACE porigin_target pclassdesc_dependency.NAME) :: ptask_post*',
        '$class_named(S_post.CLASSNAMES,$ptlc(pclassdesc_dependency.NAME)) = (porigin_dependency)',
        '$class_named(S_post.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = eps',
        '$pil_at(S_post.LINKEDINTERFACES,porigin_target) = eps',
        '$autoload_interface_source(S_post,porigin_target,pclassdesc_dependency.NAME)',
        '$call_task_valid(S_post,pautoloadcall.RESUME)', '$autoload_resume_valid(S_post,pautoloadcall)',
        'S_post.CLASSES = S_next.CLASSES', 'S_post.OBJECTS = S_next.OBJECTS',
        'S_post.AUTOLOAD = S_next.AUTOLOAD',
        '$test_iface_outputs(S_post.EVENTS) = ' + term(('B|L:' + dependency + '|').encode()),
        *step('S_linked','S_post'), *public('S_linked'),
        '$class_named(S_linked.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = (porigin_target)',
        '$pil_at(S_linked.LINKEDINTERFACES,porigin_target) = (PILTARGETS ([PILSOURCE pclassdesc_dependency.NAME porigin_dependency]))',
        '$pil_proto_source(S_linked,porigin_dependency,|S_linked.CLASSES|) = [PPMINHERITED pmethoddesc pclassdesc_dependency]',
        'pmethoddesc.NAME = $ptascii("value")', 'pmethoddesc.OWNER = porigin_dependency', 'pmethoddesc.ABSTRACT',
        '$pil_contract_issue(S_linked,pclassdesc_target) = METHOD_OK',
        '$autoload_interface_source(S_linked,porigin_target,pclassdesc_dependency.NAME)',
        '$autoload_declaration_resume(S_linked,pautoloadcall)',
        'S_linked.OBJECTS = S_post.OBJECTS', 'S_linked.EVENTS = S_post.EVENTS']
    if kind == 'interface':
        checks += ['$pil_proto_source(S_linked,porigin_target,|S_linked.CLASSES|) = [PPMINHERITED pmethoddesc pclassdesc_dependency]']
    checks += ['S_final = $drive_steps(S_linked,4000)',
        r'S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps',
        '$test_iface_outputs(S_final.EVENTS) = ' + term(stdout.encode()), *public('S_final')]
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
        native = json.loads((sources / 'static-native-v55/report.json').read_text())
        assert native['result'] == 'native_observation' and native['stable_inputs'] and native['target'] == types.PROFILE
        for stage, name in CASES.items():
            case = sources / 'static-native-v55' / name
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
                    if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'class V55Implementation ')]
                unit = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                    'profile': 'cli-raw-85', 'source': b64(code)})
                assert unit['accepted']
                checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
                response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked
                initial += ['$eval_response_valid(S_wait,' + response + ')',
                    'S_run = $eval_resume(S_wait,' + response + ')']
            initial += ['S_initial = $test_iface_running(S_run)', '~S_initial.COMPILESTOP']
            checks = assertions(initial, 'V55Implementation' if stage == 'class' else 'V55Child',
                'V55Contract' if stage == 'class' else 'V55Parent', stage, row['stdout'])
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
    suite = sources / 'static-native-v55'
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

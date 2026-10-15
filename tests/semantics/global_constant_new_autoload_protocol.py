#!/usr/bin/env python3
"""Reached global AST NEW autoload before allocation, arguments and retry."""
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
CASES = {'success': 'autoload-before-argument', 'retry': 'autoload-miss-eval-retry'}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'

PREFIX = r'''
dec $test_outputs(pevent*) : nat*
dec $test_output_item(pevent) : nat*
def $test_output_item(OUTPUT n*) = n*
def $test_output_item(pevent) = eps -- otherwise
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output_item(pevent) ++ $test_outputs(pevent_tail*)
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_descriptor(pclassdesc*, preqbytes) : pclassdesc?
def $test_descriptor(eps, preqbytes) = eps
def $test_descriptor(pclassdesc :: pclassdesc_tail*, preqbytes) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptlc(preqbytes)
def $test_descriptor(pclassdesc :: pclassdesc_tail*, preqbytes) = $test_descriptor(pclassdesc_tail*,preqbytes)
  -- if $ptlc(pclassdesc.NAME) =/= $ptlc(preqbytes)
dec $test_new_front(pstate, nat, nat) : bool
def $test_new_front(S,0,n_unit) = true
  -- if S.TODO = (EVAL (NExprNew name phpType6 metadata)) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN n_unit pcpath)
  -- if $global_new_current(S)
def $test_new_front(S,1,n_unit) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.RESUME = AUTO_GLOBAL_NEW preqbytes phpType7* pconstantcontext
  -- if pautoloadcall.SITE = PORIGIN n_unit pcpath
def $test_new_front(S,2,n_unit) = true
  -- if S.TODO = (AUTO_GLOBAL_NEW preqbytes phpType7* pconstantcontext) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN n_unit pcpath)
def $test_new_front(S,3,n_unit) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if pdefaultnew.SITE = PORIGIN n_unit pcpath
def $test_new_front(S,4,n_unit) = true
  -- if S.TODO = (CONSTANT_BIND (PORIGIN n_unit pcpath)) :: ptask_tail*
def $test_new_front(S,5,n_unit) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))
  -- if pautoloadcall.RESUME = AUTO_GLOBAL_NEW preqbytes phpType7* pconstantcontext
  -- if pautoloadcall.SITE = PORIGIN n_unit pcpath
def $test_new_front(S,6,n_unit) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN n_unit pcpath)
def $test_new_front(S,n_kind,n_unit) = false -- otherwise
dec $test_new_seek(pstate, nat, nat, nat) : pstate
def $test_new_seek(S,n_kind,n_unit,0) = S
def $test_new_seek(S,n_kind,n_unit,n) = S
  -- if $(n > 0)
  -- if $test_new_front(S,n_kind,n_unit) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_new_seek(S,n_kind,n_unit,n) = $test_new_seek($drive_steps($test_running(S),1),n_kind,n_unit,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_new_front(S,n_kind,n_unit)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def reach(state, previous, kind, unit):
    args = str(kind) + ',' + str(unit)
    return [state + '_found = $test_new_seek(' + previous + ',' + args + ',6000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_new_front(' + state + ',' + args + ')', *public(state)]


def step(state, previous):
    return [state + '_found = $drive_steps(' + previous + ',1)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]']


def new_checks(state, target, unit):
    return [state + '.TODO = (EVAL (NExprNew name_' + state + ' (SEQUENCE phpType7_' + state + '*) metadata_' + state + ')) :: ptask_' + state + '*',
        state + '.ORIGIN = (porigin_' + state + ')', state + '.CONSTCONTEXT = (pconstantcontext_' + state + ')',
        'pconstantcontext_' + state + '.FACTS = eps',
        '$global_autoload_source(' + state + ',porigin_' + state + ',$ptascii(' + json.dumps(target) + '),phpType7_' + state + '*,pconstantcontext_' + state + ')',
        '$global_autoload_ready(' + state + ',$ptascii(' + json.dumps(target) + '),phpType7_' + state + '*,pconstantcontext_' + state + ')',
        '$global_new_autoload_pending(' + state + ',$ptascii(' + json.dumps(target) + '))',
        '$constant_bindings(' + state + ',' + state + '.TODO) = [pconstantcontext_' + state + '.ORIGIN]',
        '$class_named(' + state + '.CLASSNAMES,$ptascii(' + json.dumps(target.lower()) + ')) = eps',
        '~$dynamic_new_known(' + state + ',$ptascii(' + json.dumps(target) + '))',
        '$test_descriptor(' + state + '.CLASSES,$ptascii(' + json.dumps(target) + ')) = (pclassdesc_' + state + ')',
        '$class_at(' + state + '.CLASSES,pclassdesc_' + state + '.ORIGIN) = (pclassdesc_' + state + ')',
        state + '.CONSTANTOBJECTS = eps']


def auto_checks(state, previous, new_state, target, unit):
    ctx, args = 'pconstantcontext_' + new_state, 'phpType7_' + new_state + '*'
    checks = [*reach(state,previous,1,unit),
        state + '.TODO = (AUTO_NEXT pautoloadcall_' + state + ') :: ptask_' + state + '*',
        'pautoloadcall_' + state + '.MODE = AUTO_LOOKUP',
        'pautoloadcall_' + state + '.RESUME = AUTO_GLOBAL_NEW $ptascii(' + json.dumps(target) + ') ' + args + ' ' + ctx,
        'pautoloadcall_' + state + '.SITE = porigin_' + new_state,
        'pautoloadcall_' + state + '.LINE = ' + ctx + '.LINE',
        '$autoload_call_valid(' + state + ',pautoloadcall_' + state + ')',
        '$autoload_declaration_resume(' + state + ',pautoloadcall_' + state + ')',
        '$task_nodes(pautoloadcall_' + state + '.RESUME) = eps']
    checks += [state + '.' + field + ' = ' + new_state + '.' + field for field in
        ('OBJECTS','ALLOCATIONS','CONSTANTOBJECTS','USERCONSTANTS','EVENTS')]
    return checks


def post_loader(state, previous, new_state, target, argument, value, unit):
    ctx, args = 'pconstantcontext_' + new_state, 'phpType7_' + new_state + '*'
    return [*reach(state,previous,2,unit),
        state + '.TODO = (AUTO_GLOBAL_NEW $ptascii(' + json.dumps(target) + ') ' + args + ' ' + ctx + ') :: ptask_' + state + '*',
        state + '.CONSTCONTEXT = (' + ctx + ')',
        '~$global_new_autoload_pending(' + state + ',$ptascii(' + json.dumps(target) + '))',
        '$global_autoload_ready(' + state + ',$ptascii(' + json.dumps(target) + '),' + args + ',' + ctx + ')',
        '$class_named(' + state + '.CLASSNAMES,$ptascii(' + json.dumps(target.lower()) + ')) = (pclassdesc_' + new_state + '.ORIGIN)',
        '$user_constant_at(' + state + '.USERCONSTANTS,$ptascii(' + json.dumps(argument) + ')) = (puserconstant_' + state + ')',
        'puserconstant_' + state + '.VALUE = PINT ' + str(value),
        'puserconstant_' + state + '.CLASS = PVSCALAR',
        state + '.OBJECTS = ' + new_state + '.OBJECTS',
        state + '.CONSTANTOBJECTS = eps']


def completed_checks(previous, new_state, target, constant, unit):
    args = 'phpType7_' + new_state + '*'
    return [*reach('S_alloc',previous,3,unit),
        'S_alloc.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_alloc*',
        'pdefaultnew.SITE = porigin_' + new_state, 'pdefaultnew.INDEX = 0', 'pdefaultnew.VALUES = eps',
        'pdefaultnew.ARGUMENTS = ' + args,
        'S_alloc.OBJECTS = ' + previous + '.OBJECTS ++ [INSTANCE pclassdesc_' + new_state + '.ORIGIN]',
        'S_alloc.CONSTANTOBJECTS = [pconstantobject]',
        'pconstantobject.OBJECT = pdefaultnew.OBJECT', 'pconstantobject.SITE = porigin_' + new_state,
        'pconstantobject.DECL = pconstantcontext_' + new_state + '.ORIGIN', '~pconstantobject.COMPLETE',
        '$global_new_pending(S_alloc,pdefaultnew)',
        '$user_constant_at(S_alloc.USERCONSTANTS,$ptascii(' + json.dumps(constant) + ')) = eps',
        *reach('S_bind','S_alloc',4,unit), 'S_bind.RESULT = KNOWN (POBJECT pdefaultnew.OBJECT)',
        'S_bind.CONSTANTOBJECTS = [pconstantobject_done]',
        'pconstantobject_done = pconstantobject[.COMPLETE = true]',
        '$global_new_completed(S_bind,pconstantobject_done)',
        *step('S_bound','S_bind'),
        '$user_constant_at(S_bound.USERCONSTANTS,$ptascii(' + json.dumps(constant) + ')) = (puserconstant_bound)',
        'puserconstant_bound.VALUE = POBJECT pdefaultnew.OBJECT',
        'puserconstant_bound.ORIGIN = pconstantcontext_' + new_state + '.ORIGIN',
        'puserconstant_bound.CLASS = PVINSTANCE pdefaultnew.OBJECT porigin_' + new_state,
        *public('S_bound')]


def final(previous, stdout):
    return ['S_final = $drive_steps(' + previous + ',12000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.EVALCONTEXTS = eps',
        '$test_outputs(S_final.EVENTS) = ' + term(stdout.encode()), *public('S_final')]


def success_assertions(main, case, stdout):
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reach('S_new','S_initial',0,0), *new_checks('S_new','V53Target',0),
        '$user_constant_at(S_new.USERCONSTANTS,$ptascii("V53_ARG")) = eps',
        '$user_constant_at(S_new.USERCONSTANTS,$ptascii("V53_KEEP")) = eps',
        *auto_checks('S_auto','S_new','S_new','V53Target',0),
        'S_budget = $drive_steps(S_auto,0)', 'S_budget = S_auto[.COMPLETION = BUDGET]',
        'S_resumed = S_budget[.COMPLETION = NORMAL]', 'S_resumed = S_auto',
        *reach('S_loader','S_resumed',5,0), 'S_loader.CURRENT = (pcallcontext_loader)',
        '$autoload_context_valid(S_loader,pcallcontext_loader)',
        'S_loader.FRAMES = pframe_loader :: pframe_tail*',
        'pframe_loader.CONSTCONTEXT = (pconstantcontext_S_new)',
        'S_loader.CONSTCONTEXT = eps', 'S_loader.OBJECTS = S_new.OBJECTS',
        'S_loader.CONSTANTOBJECTS = eps',
        *post_loader('S_post','S_loader','S_new','V53Target','V53_ARG',17,0),
        'S_no_context = S_auto[.CONSTCONTEXT = eps]',
        '~$global_new_current(S_no_context)',
        '~$global_autoload_ready(S_no_context,$ptascii("V53Target"),phpType7_S_new*,pconstantcontext_S_new)',
        '~$autoload_ordinary_new_source(S_no_context,porigin_S_new)',
        'pautoloadcall_ordinary = pautoloadcall_S_auto[.RESUME = AUTO_NEW $ptascii("V53Target") phpType7_S_new* pconstantcontext_S_new.LINE pconstantcontext_S_new.LINE]',
        '~$autoload_resume_valid(S_auto,pautoloadcall_ordinary)',
        '~$autoload_declaration_resume(S_no_context,pautoloadcall_ordinary)',
        'pconstantcontext_wrong = pconstantcontext_S_new[.LINE = $(pconstantcontext_S_new.LINE + 1)]',
        '~$global_autoload_source(S_auto,porigin_S_new,$ptascii("V53Target"),phpType7_S_new*,pconstantcontext_wrong)',
        '~$call_task_valid(S_auto,AUTO_GLOBAL_NEW $ptascii("V53Target") phpType7_S_new* pconstantcontext_wrong)',
        'pautoloadcall_wrong = pautoloadcall_S_auto[.NAME = $ptascii("V53Other")]',
        '~$autoload_call_valid(S_auto,pautoloadcall_wrong)',
        'S_wrong_call = S_auto[.TODO = (AUTO_NEXT pautoloadcall_wrong) :: ptask_S_auto*]',
        '~$call_descriptors_valid(S_wrong_call)',
        *completed_checks('S_post','S_new','V53Target','V53_KEEP',0), *final('S_bound',stdout)]
    return checks


def retry_assertions(main, responses, code, case, stdout):
    response1, response2 = responses
    checks = ['S_wait1 = $php_run(' + main + ',5000,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        'S_wait1.COMPLETION = SOURCE_PENDING', 'S_wait1.EVALCONTEXTS = [pevalcontext_first]',
        'pevalcontext_first.UNIT = 1', 'pevalcontext_first.BYTES = ' + term(code),
        '$eval_response_valid(S_wait1,' + response1 + ')', 'S_body1 = $eval_resume(S_wait1,' + response1 + ')',
        *reach('S_new1','S_body1',0,1), *new_checks('S_new1','V53Late',1),
        *auto_checks('S_auto1','S_new1','S_new1','V53Late',1),
        *reach('S_miss','S_auto1',2,1),
        'S_miss.TODO = (AUTO_GLOBAL_NEW $ptascii("V53Late") phpType7_S_new1* pconstantcontext_S_new1) :: ptask_miss*',
        '$class_named(S_miss.CLASSNAMES,$ptascii("v53late")) = eps',
        'S_miss.OBJECTS = S_new1.OBJECTS', 'S_miss.CONSTANTOBJECTS = eps',
        '$user_constant_at(S_miss.USERCONSTANTS,$ptascii("V53_RETRY_ARG")) = eps',
        'S_throw_found = $test_new_seek(S_miss,6,1,6000)',
        'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$test_new_front(S_throw,6,1)',
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_throw.CONSTCONTEXT = eps',
        '$constant_bindings(S_throw,S_throw.TODO) = [pconstantcontext_S_new1.ORIGIN]',
        '$throwable_live(S_throw,n_error)', '$heap_valid($heap_graph(S_throw))',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
        'pthrowable.ORIGIN = (porigin_S_new1)',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = (' + term(b'Class "V53Late" not found') + ')',
        '$throwable_field(S_throw,n_error,"line") = PINT 1',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = (ENTRY (KINT 0) (DIRECT (PARRAY n_frame))) :: pentry_trace*',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING $ptascii("eval")',
        'S_throw.CONSTANTOBJECTS = eps',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V53_RETRY")) = eps',
        'S_wait2 = $drive_steps(S_throw,6000)', 'S_wait2.COMPLETION = SOURCE_PENDING',
        'S_wait2.EVALCONTEXTS = [pevalcontext_second]', 'pevalcontext_second.UNIT = 2',
        'pevalcontext_second.BYTES = pevalcontext_first.BYTES', 'pevalcontext_second.SITE = pevalcontext_first.SITE',
        'S_wait2.CONSTCONTEXT = eps', '$constant_bindings(S_wait2,S_wait2.TODO) = eps',
        'S_wait2.CONSTANTOBJECTS = eps', 'S_wait2.FAILEDSOURCES = eps',
        '$source_unit(S_wait2.SOURCES,1) =/= eps',
        '$user_constant_at(S_wait2.USERCONSTANTS,$ptascii("V53_RETRY")) = eps',
        '$test_outputs(S_wait2.EVENTS) = ' + term(b'B|L:V53Late|E:Class "V53Late" not found@1|T:eval|D:0|'),
        *public('S_wait2'), '$eval_response_valid(S_wait2,' + response2 + ')',
        'S_body2 = $eval_resume(S_wait2,' + response2 + ')',
        *reach('S_new2','S_body2',0,2), *new_checks('S_new2','V53Late',2),
        'pconstantcontext_S_new2.ORIGIN =/= pconstantcontext_S_new1.ORIGIN',
        'porigin_S_new2 =/= porigin_S_new1',
        '~$global_autoload_source(S_new2,porigin_S_new2,$ptascii("V53Late"),phpType7_S_new2*,pconstantcontext_S_new1)',
        *post_loader('S_post','S_new2','S_new2','V53Late','V53_RETRY_ARG',31,2),
        *completed_checks('S_post','S_new2','V53Late','V53_RETRY',2), *final('S_bound',stdout)]
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
        native = json.loads((sources / 'static-native-v53/report.json').read_text())
        assert native['result'] == 'native_observation' and native['stable_inputs'] and native['target'] == types.PROFILE
        for stage, name in CASES.items():
            case = sources / 'static-native-v53' / name
            row, = [item for item in native['records'] if item['id'] == name]
            assert row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            if stage == 'retry':
                literals = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                    if node['node'] == 'Scalar_String']
                code, = [value for value in literals if value.startswith(b'const V53_RETRY = new V53Late(')]
                responses = []
                for unit_id in (1,2):
                    unit = frontend.request({'op': 'parse-eval', 'id': str(unit_id), 'mode': 'eval',
                        'profile': 'cli-raw-85', 'source': b64(code)})
                    assert unit['accepted']
                    checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
                    responses.append('SOURCE_ACCEPT ' + str(unit_id) + ' ' + term(code) + ' ' + checked)
                checks = retry_assertions(main,responses,code,case,row['stdout'])
            else:
                checks = success_assertions(main,case,row['stdout'])
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks,indent=2) + '\n')
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
    parser.add_argument('--case', choices=list(CASES), help='Check one prepared front; default both')
    args = parser.parse_args()
    if args.case and args.phase != 'check':
        parser.error('--case is only valid with --phase check')
    selected = [args.case] if args.case else list(CASES)
    sources, out = args.sources.resolve(), args.output.resolve()
    suite = sources / 'static-native-v53'
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

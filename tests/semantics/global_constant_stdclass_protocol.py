#!/usr/bin/env python3
"""Genuine stdClass constant birth, alias roots and duplicate-candidate release."""
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
CASES = {'root': ('static-native-v57', 'global-stdclass', 'failed_probe'),
         'duplicate': ('static-native-v57-duplicate-v2', 'eval-duplicate-stdclass', 'native_observation')}
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'

PREFIX = r'''
dec $test_std_output(pevent) : nat*
dec $test_std_outputs(pevent*) : nat*
def $test_std_output(OUTPUT n*) = n*
def $test_std_output(pevent) = eps -- otherwise
def $test_std_outputs(eps) = eps
def $test_std_outputs(pevent :: pevent_tail*) = $test_std_output(pevent) ++ $test_std_outputs(pevent_tail*)
dec $test_std_running(pstate) : pstate
def $test_std_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_std_running(S) = S -- otherwise
dec $test_std_statement(pstate, int) : bool
def $test_std_statement(S,z) = true
  -- if S.TODO = (STMT statement) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (statement)
  -- if $plcompileline(statement) = z
def $test_std_statement(S,z) = false -- otherwise
dec $test_std_front(pstate, nat, int) : bool
def $test_std_front(S,0,z) = true
  -- if S.TODO = (EVAL (NExprNew name (SEQUENCE eps) metadata)) :: ptask_tail*
  -- if $global_new_current(S)
def $test_std_front(S,1,z) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if $global_std_pending(S,pdefaultnew)
def $test_std_front(S,2,z) = $test_std_statement(S,z)
def $test_std_front(S,3,z) = true
  -- if $test_std_statement(S,z)
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = GLOBAL_CONSTANT_DUPLICATE porigin pvalue pvalueclass n pconstantfact* z_line
def $test_std_front(S,4,z) = true
  -- if S.COMPLETION = SOURCE_PENDING
  -- if S.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*
  -- if pevalcontext.UNIT = 2
def $test_std_front(S,n,z) = false -- otherwise
dec $test_std_seek(pstate, nat, int, nat) : pstate
def $test_std_seek(S,n_phase,z,0) = S
def $test_std_seek(S,n_phase,z,n) = S
  -- if $(n > 0)
  -- if $test_std_front(S,n_phase,z) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_std_seek(S,n_phase,z,n) = $test_std_seek($drive_steps($test_std_running(S),1),n_phase,z,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_std_front(S,n_phase,z)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

def public(s):
    return [f'$call_descriptors_valid({s})', f'$declaration_entry_check({s}) = {s}',
            f'$heap_valid($heap_graph({s}))']


def reach(s, previous, phase, line=0):
    return [f'{s}_found = $test_std_seek({previous},{phase},{line},5000)',
            fr'{s}_found.COMPLETION = NORMAL \/ {s}_found.COMPLETION = BUDGET',
            f'{s} = {s}_found[.COMPLETION = NORMAL]',
            f'$test_std_front({s},{phase},{line})', *public(s)]


def step(s, previous):
    return [f'{s}_found = $drive_steps({previous},1)',
            fr'{s}_found.COMPLETION = NORMAL \/ {s}_found.COMPLETION = BUDGET',
            f'{s} = {s}_found[.COMPLETION = NORMAL]', *public(s)]


def property_value(s, obj, value, suffix):
    return [f'$property_slot_at($object_table_slots_at({s},{obj}),$ptascii("value")) = (ppropertyslot_{suffix})',
            f'ppropertyslot_{suffix}.STATE = PROP_VALUE pitem_{suffix}',
            f'$entry_value({s},pitem_{suffix}) = PINT {value}']


def root_checks(initial, stdout):
    checks = initial + reach('S_before', 'S_initial', 0)
    checks += [
        'S_before.CONSTCONTEXT = (pconstantcontext)',
        'porigin_decl = pconstantcontext.ORIGIN',
        'S_before.ORIGIN = (porigin_site)',
        'pconstantcontext.FACTS = eps', 'S_before.CONSTANTSTDOBJECTS = eps',
        '$global_std_ready(S_before,$ptascii("stdClass"))',
        '$global_std_source(S_before,porigin_site,porigin_decl,|S_before.DECLARATIONS|)',
        '~$global_std_source(S_before,porigin_decl,porigin_decl,|S_before.DECLARATIONS|)',
        '~$global_std_source(S_before,porigin_site,porigin_site,|S_before.DECLARATIONS|)',
        '~$global_std_source(S_before,porigin_site,porigin_decl,0)',
        '~$global_std_ready(S_before,$ptascii("Exception"))',
        '$global_new_unsupported_target(S_before,$ptascii("Exception"))',
        'S_dirty = S_before[.CONSTCONTEXT = (pconstantcontext[.FACTS = [{ORIGIN porigin_site, VALUE (PNULL), CLASS PVSCALAR, LOOKUP eps}]])]',
        '~$global_std_ready(S_dirty,$ptascii("stdClass"))',
        '$global_new_unsupported_target(S_dirty,$ptascii("stdClass"))',
    ]
    checks += step('S_born', 'S_before')
    checks += [
        'S_born.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*',
        'n_object = |S_before.OBJECTS|', 'pdefaultnew.OBJECT = n_object',
        'pdefaultnew.SITE = porigin_site', 'pdefaultnew.ARGUMENTS = eps',
        'pdefaultnew.INDEX = 0', 'pdefaultnew.VALUES = eps',
        'S_born.OBJECTS = S_before.OBJECTS ++ [STDINSTANCE]',
        'S_born.ALLOCATIONS = S_before.ALLOCATIONS ++ [HOBJECT n_object]',
        'S_born.CONSTANTSTDOBJECTS = [pconstantstdobject]',
        'n_prefix = |S_before.DECLARATIONS|',
        'pconstantstdobject = {OBJECT n_object, SITE porigin_site, DECL porigin_decl, PREFIX n_prefix, COMPLETE false}',
        '$global_std_header(S_born,pconstantstdobject)', '$global_std_pending(S_born,pdefaultnew)',
        '$default_new_object_valid(S_born,pdefaultnew)', '$default_new_valid(S_born,pdefaultnew)',
        '$heap_owners($heap_graph(S_born),HOBJECT n_object) = 1',
        '~$global_std_completed(S_born,pconstantstdobject)',
        'S_early = S_born[.CONSTANTSTDOBJECTS = [pconstantstdobject[.COMPLETE = true]]]',
        '~$global_std_records_valid(S_early,S_early.CONSTANTSTDOBJECTS)',
        '~$constant_value_class_valid(S_early,POBJECT n_object,PVSTDCLASS n_object porigin_site)',
    ]
    checks += step('S_complete', 'S_born')
    checks += [
        'S_complete.RESULT = KNOWN (POBJECT n_object)',
        'S_complete.CONSTANTSTDOBJECTS = [pconstantstdobject[.COMPLETE = true]]',
        '$global_std_completed(S_complete,pconstantstdobject[.COMPLETE = true])',
        '$global_new_value_class(S_complete,porigin_site) = PVSTDCLASS n_object porigin_site',
        '$constant_value_class_valid(S_complete,POBJECT n_object,PVSTDCLASS n_object porigin_site)',
        '~$constant_value_class_valid(S_complete,POBJECT n_object,PVINSTANCE n_object porigin_site)',
        '~$constant_value_class_valid(S_complete,POBJECT n_object,PVSTDCLASS $(n_object + 1) porigin_site)',
        '~$constant_class_tree_valid(PVSTDCLASS n_object porigin_site)',
        '~$default_cacheable(PVSTDCLASS n_object porigin_site)',
        '~$constant_callable_foldable(PVSTDCLASS n_object porigin_site)',
        '~$global_std_header(S_complete,pconstantstdobject[.SITE = porigin_decl])',
        '~$global_std_header(S_complete,pconstantstdobject[.PREFIX = 0])',
    ]
    checks += reach('S_aliases', 'S_complete', 2, 9)
    checks += [
        '$user_constant_at(S_aliases.USERCONSTANTS,$ptascii("V57_ROOT")) = (puserconstant)',
        'puserconstant.VALUE = POBJECT n_object',
        'puserconstant.CLASS = PVSTDCLASS n_object porigin_site',
        '$heap_owners($heap_graph(S_aliases),HOBJECT n_object) = 3',
    ]
    checks += property_value('S_aliases', 'n_object', 29, 'aliases')
    checks += reach('S_released', 'S_aliases', 2, 10)
    checks += [
        'S_released.USERCONSTANTS = S_aliases.USERCONSTANTS',
        'S_released.CONSTANTSTDOBJECTS = S_complete.CONSTANTSTDOBJECTS',
        '$heap_owners($heap_graph(S_released),HOBJECT n_object) = 1',
        '$constant_value_class_valid(S_released,puserconstant.VALUE,puserconstant.CLASS)',
        '$dynamic_global_constant_value(S_released,$ptascii("V57_ROOT")) = eps',
    ]
    checks += property_value('S_released', 'n_object', 29, 'released')
    return checks + final_checks('S_released', stdout)


def duplicate_checks(initial, response_second, code, stdout):
    checks = initial + [
        'S_wait2 = $test_std_seek(S_initial,4,0,5000)',
        '$test_std_front(S_wait2,4,0)', 'S_wait2.COMPLETION = SOURCE_PENDING',
        *public('S_wait2'),
        'S_wait2.EVALCONTEXTS = pevalcontext_second :: pevalcontext_tail*',
        'pevalcontext_second.BYTES = ' + term(code),
        'pevalcontext_second.SITE = pevalcontext_first.SITE',
        '$eval_binding_at(S_wait2.EVALBINDINGS,1) = (pevalbinding_first)',
        'pevalbinding_first.SITE = pevalcontext_first.SITE',
        'S_wait2.CONSTCONTEXT = eps', 'S_wait2.CONSTANTSTDOBJECTS = [pconstantstdobject_old]',
        '$global_std_completed(S_wait2,pconstantstdobject_old)',
        'n_original = pconstantstdobject_old.OBJECT',
        '$user_constant_at(S_wait2.USERCONSTANTS,$ptascii("V57_EVAL")) = (puserconstant)',
        'puserconstant.VALUE = POBJECT n_original',
        'puserconstant.CLASS = PVSTDCLASS n_original pconstantstdobject_old.SITE',
        '$eval_response_valid(S_wait2,' + response_second + ')',
    ]
    checks += property_value('S_wait2', 'n_original', 17, 'first')
    checks += ['S_second_start = $test_std_running($eval_resume(S_wait2,' + response_second + '))']
    checks += reach('S_before', 'S_second_start', 0)
    checks += step('S_born', 'S_before')
    checks += [
        'S_born.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*',
        'n_candidate = |S_before.OBJECTS|', 'n_candidate = pdefaultnew.OBJECT',
        'n_candidate =/= n_original',
        'S_born.OBJECTS = S_before.OBJECTS ++ [STDINSTANCE]',
        'S_born.ALLOCATIONS = S_before.ALLOCATIONS ++ [HOBJECT n_candidate]',
        '$global_std_record(S_born.CONSTANTSTDOBJECTS,n_candidate) = (pconstantstdobject_new)',
        '~pconstantstdobject_new.COMPLETE',
        'pconstantstdobject_new.DECL = PORIGIN 2 pcpath_decl',
        '$heap_owners($heap_graph(S_born),HOBJECT n_candidate) = 1',
    ]
    checks += reach('S_handler', 'S_born', 3, 9)
    checks += [
        'S_handler.CURRENT = (pcallcontext)',
        '$error_context_call(S_handler,pcallcontext) = (perrorcall)',
        'perrorcall.RESUME = GLOBAL_CONSTANT_DUPLICATE porigin_decl (POBJECT n_candidate) (PVSTDCLASS n_candidate porigin_site) n_constants pconstantfact_read* z_line',
        'perrorcall.LEVEL = 2', 'z_line = 1', 'n_constants = 1',
        'perrorcall.MESSAGE = $ptascii("Constant V57_EVAL already defined, this will be an error in PHP 9")',
        'S_handler.USERCONSTANTS = S_wait2.USERCONSTANTS',
        'S_handler.CONSTANTSTDOBJECTS = [pconstantstdobject_old, pconstantstdobject_new[.COMPLETE = true]]',
        '$global_std_completed(S_handler,pconstantstdobject_new[.COMPLETE = true])',
        '$constant_value_class_valid(S_handler,POBJECT n_candidate,PVSTDCLASS n_candidate porigin_site)',
        '$heap_owners($heap_graph(S_handler),HOBJECT n_candidate) = 1',
        '$task_nodes(perrorcall.RESUME) = [HOBJECT n_candidate]',
        '$constant_value_class_valid(S_handler,puserconstant.VALUE,puserconstant.CLASS)',
    ]
    checks += property_value('S_handler', 'n_original', 31, 'handler')
    checks += [
        'S_budget = $drive_steps(S_handler,0)', 'S_budget = S_handler[.COMPLETION = BUDGET]',
        'S_resumed = S_budget[.COMPLETION = NORMAL]', 'S_resumed = S_handler',
    ]
    checks += reach('S_discarded', 'S_resumed', 2, 18)
    checks += [
        'S_discarded.USERCONSTANTS = S_wait2.USERCONSTANTS',
        'S_discarded.CONSTANTSTDOBJECTS = S_handler.CONSTANTSTDOBJECTS',
        '~((HOBJECT n_candidate) <- S_discarded.ALLOCATIONS)',
        '(HOBJECT n_original) <- S_discarded.ALLOCATIONS',
        '$heap_owners($heap_graph(S_discarded),HOBJECT n_candidate) = 0',
        '$global_std_completed(S_discarded,pconstantstdobject_new[.COMPLETE = true])',
        '$global_std_records_valid(S_discarded,S_discarded.CONSTANTSTDOBJECTS)',
        '~$constant_value_class_valid(S_discarded,POBJECT n_candidate,PVSTDCLASS n_candidate porigin_site)',
        '$constant_value_class_valid(S_discarded,puserconstant.VALUE,puserconstant.CLASS)',
        '$dynamic_global_constant_value(S_discarded,$ptascii("V57_EVAL")) = eps',
    ]
    checks += property_value('S_discarded', 'n_original', 31, 'discarded')
    return checks + final_checks('S_discarded', stdout)


def final_checks(previous, stdout):
    return [f'S_final = $drive_steps({previous},5000)', 'S_final.COMPLETION = NORMAL',
            'S_final.TODO = eps', 'S_final.FRAMES = eps', 'S_final.CURRENT = eps',
            'S_final.CONSTCONTEXT = eps', 'S_final.EVALCONTEXTS = eps',
            '$test_std_outputs(S_final.EVENTS) = ' + term(stdout.encode()), *public('S_final')]


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for item in value.values():
            yield from nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from nodes(item)


def prepare(out, sources):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for stage, (suite, name, result) in CASES.items():
            case = sources / suite / name
            native = json.loads((case.parent / 'report.json').read_text())
            assert native['result'] == result and native['stable_inputs'] and native['target'] == types.PROFILE
            row, = [item for item in native['records'] if item['id'] == name]
            assert row['probe_sanity'] and row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            initial = ['S_run = $php_run(' + main + ',0,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
                       'S_initial = $test_std_running(S_run)', '~S_initial.COMPILESTOP']
            if stage == 'root':
                checks = root_checks(initial, row['stdout'])
            else:
                code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                         if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'const V57_EVAL ')]
                responses = []
                for unit in [1, 2]:
                    parsed_unit = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval',
                        'profile': 'cli-raw-85', 'source': b64(code)})
                    assert parsed_unit['accepted']
                    checked = adapter.request({'op': 'check', 'ast': parsed_unit['ast'], 'fixture': True})['fixture']
                    responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(code) + ' ' + checked)
                initial = ['S_wait1 = $php_run(' + main + ',5000,' + json.dumps(b64(str(case / 'main.php').encode())) + ')',
                           'S_wait1.COMPLETION = SOURCE_PENDING', *public('S_wait1'),
                           'S_wait1.EVALCONTEXTS = pevalcontext_first :: eps', 'pevalcontext_first.UNIT = 1',
                           'pevalcontext_first.BYTES = ' + term(code),
                           '$eval_response_valid(S_wait1,' + responses[0] + ')',
                           'S_initial = $test_std_running($eval_resume(S_wait1,' + responses[0] + '))']
                checks = duplicate_checks(initial, responses[1], code, row['stdout'])
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
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
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for suite, name, _ in CASES.values():
        case = sources / suite / name
        paths += [case.parent / 'run.py', case.parent / 'report.json', case / 'main.php',
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

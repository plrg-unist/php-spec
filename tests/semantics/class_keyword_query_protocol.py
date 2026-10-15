#!/usr/bin/env python3
"""Reached keyword queries in inherited eval and actual API scope Errors."""
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
CASES = {'eval': 'eval-keyword-scopes', 'errors': 'keyword-scope-errors'}
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
dec $test_keyword_front(pstate, nat, preqbytes, nat) : bool
def $test_keyword_front(S,n_kind,preqbytes,n_line) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if (n_kind = 0 /\ pconfigcall.KIND = INTRINSIC_CONSTANT) \/ (n_kind = 1 /\ pconfigcall.KIND = INTRINSIC_DEFINED)
  -- if n_line = 0 \/ pconfigcall.LINE = n_line
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_query)]
  -- if $string_bytes(pvalue_query) = (preqbytes)
def $test_keyword_front(S,n_kind,preqbytes,n_line) = false -- otherwise
dec $test_keyword_seek(pstate, nat, preqbytes, nat, nat) : pstate
def $test_keyword_seek(S,n_kind,preqbytes,n_line,0) = S
def $test_keyword_seek(S,n_kind,preqbytes,n_line,n) = S
  -- if $(n > 0)
  -- if $test_keyword_front(S,n_kind,preqbytes,n_line) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_keyword_seek(S,n_kind,preqbytes,n_line,n) = $test_keyword_seek($drive_steps($test_running(S),1),n_kind,preqbytes,n_line,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_keyword_front(S,n_kind,preqbytes,n_line)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def reach(state, previous, kind, query, line=0):
    args = str(kind) + ',$ptascii(' + json.dumps(query) + '),' + str(line)
    return [state + '_found = $test_keyword_seek(' + previous + ',' + args + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_keyword_front(' + state + ',' + args + ')',
        state + '.TODO = (CONFIG_INVOKE pconfigcall_' + state + ') :: ptask_' + state + '*',
        'pconfigcall_' + state + '.SENT = [NAMED_SENT (KNOWN pvalue_' + state + ')]',
        '$config_invoke_valid(' + state + ',pconfigcall_' + state + ')',
        '$call_current_valid(' + state + ')',
        '$dynamic_keyword_valid(' + state + ',pconfigcall_' + state + ')', *public(state)]


def step(state, previous, value=None):
    checks = [state + '_found = $drive_steps(' + previous + ',1)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]']
    if value is not None:
        checks += [state + '.RESULT = KNOWN (' + value + ')',
            *[state + '.' + field + ' = ' + previous + '.' + field for field in
                ('CURRENT','SOURCES','EVALBINDINGS','ARRAYS','STORE','ALLOCATIONS','EVENTS','SELECTEDCALLS','CLASSCONSTANTCACHE')],
            *public(state)]
    return checks


def final(previous, stdout):
    return ['S_final = $drive_steps(' + previous + ',10000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.EVALCONTEXTS = eps',
        '$test_outputs(S_final.EVENTS) = ' + term(stdout.encode()), *public('S_final')]


def eval_assertions(main, response, code, case, stdout):
    checks = ['S_wait = $php_run(' + main + ',3000,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        'S_wait.COMPLETION = SOURCE_PENDING', 'S_wait.EVALCONTEXTS = [pevalcontext]',
        'pevalcontext.UNIT = 1', 'pevalcontext.BYTES = ' + term(code),
        '$class_named(S_wait.CLASSNAMES,$ptascii("v52grand")) = (porigin_grand)',
        '$class_named(S_wait.CLASSNAMES,$ptascii("v52base")) = (porigin_base)',
        '$class_named(S_wait.CLASSNAMES,$ptascii("v52child")) = (porigin_child)',
        'porigin_base =/= porigin_child', 'porigin_base =/= porigin_grand',
        'S_wait.CURRENT = (pcallcontext)',
        'pcallcontext.LEXICAL_CLASS = (porigin_base)', 'pcallcontext.CALLED_CLASS = (porigin_child)',
        'pevalcontext.LEXICAL_CLASS = (porigin_base)', *public('S_wait'),
        '$eval_response_valid(S_wait,' + response + ')', 'S_body = $eval_resume(S_wait,' + response + ')',
        'S_body.COMPLETION = NORMAL',
        '$eval_binding_at(S_body.EVALBINDINGS,1) = (pevalbinding)',
        'pevalbinding.CLASS = (porigin_base)', 'pevalbinding.SITE = pevalcontext.SITE']
    previous = 'S_body'
    for index, (kind, query, value, target) in enumerate([
            (0,'self::K','PINT 17','porigin_base'),
            (0,'parent::K','PINT 11','porigin_grand'),
            (0,'StAtIc::K','PINT 29','porigin_child'),
            (1,'self::LATE','PBOOL false','porigin_base'),
            (1,'parent::HERE','PBOOL false','porigin_grand'),
            (1,'static::LATE','PBOOL true','porigin_child')]):
        state, after = 'S_' + str(index), 'S_after_' + str(index)
        name, member = query.split('::')
        checks += [*reach(state,previous,kind,query),
            state + '.CURRENT = (pcallcontext)', 'pconfigcall_' + state + '.SITE = PORIGIN 1 pcpath_' + state,
            '$method_current_scope(' + state + ') = (porigin_base)',
            '$method_called_scope(' + state + ') = (porigin_child)',
            '$dynamic_keyword_target(' + state + ',$ptascii(' + json.dumps(name) + ')) = (' + target + ')',
            '$eval_binding_at(' + state + '.EVALBINDINGS,1) = (pevalbinding)']
        if index == 0:
            checks += ['S_budget = $drive_steps(S_0,0)', 'S_budget = S_0[.COMPLETION = BUDGET]',
                'S_resume = S_budget[.COMPLETION = NORMAL]', 'S_resume = S_0']
        if index < 3:
            checks += ['$class_constant_lookup(' + state + ',' + target + ',$ptascii("K"),|' + state + '.CLASSES|) = (pclassconstantdesc_' + state + ')',
                'pclassconstantdesc_' + state + '.FOLDED',
                '$compiled_read(' + state + ',pclassconstantdesc_' + state + '.INITIALIZER) = (' + value + ')']
        elif index < 5:
            checks += ['$class_constant_lookup(' + state + ',' + target + ',$ptascii(' + json.dumps(member) + '),|' + state + '.CLASSES|) = eps']
        else:
            checks += ['$class_constant_lookup(' + state + ',porigin_child,$ptascii("LATE"),|' + state + '.CLASSES|) = (pclassconstantdesc_late)',
                '$compiled_read(' + state + ',pclassconstantdesc_late.INITIALIZER) = (PINT 31)']
        checks += step(after,'S_resume' if index == 0 else state,value)
        previous = after
    checks += ['S_wrong_scope = S_0[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_child)])]',
        '~$call_current_valid(S_wrong_scope)', '~$dynamic_keyword_valid(S_wrong_scope,pconfigcall_S_0)',
        '~$call_descriptors_valid(S_wrong_scope)',
        'S_wrong_called = S_2[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_base)])]',
        '~$call_current_valid(S_wrong_called)', '~$dynamic_keyword_valid(S_wrong_called,pconfigcall_S_2)',
        '~$call_descriptors_valid(S_wrong_called)',
        'S_wrong_binding = S_0[.EVALBINDINGS = [pevalbinding[.CLASS = (porigin_child)]]]',
        '~$call_descriptors_valid(S_wrong_binding)',
        'pconfigcall_nonce = pconfigcall_S_0[.SELECTION = (S_0.SELECTSEQ)]',
        '~$dynamic_keyword_valid(S_0,pconfigcall_nonce)',
        'pconfigcall_dangling = pconfigcall_S_2[.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_2.STRINGDATA|)) $ptascii("StAtIc::K")))]]',
        '~$dynamic_keyword_valid(S_2,pconfigcall_dangling)',
        '$dynamic_define_known(S_2,pconfigcall_S_2.SITE,0) = (pvalue_literal)',
        '$string_bytes(pvalue_literal) = ($ptascii("StAtIc::K"))',
        'pconfigcall_literal = pconfigcall_S_2[.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("self::K")))]]',
        '~$dynamic_keyword_valid(S_2,pconfigcall_literal)',
        '$class_at(S_0.CLASSES,porigin_base) = (pclassdesc_base)',
        'S_nonuser = S_0[.CLASSES = [(pclassdesc_base[.KIND = "enum"])]]',
        '~$dynamic_keyword_scope_valid(S_nonuser,(porigin_base))',
        'S_internal_parent = S_0[.LINKEDPARENTS = [CLASSLINK porigin_base STDCLASS_PARENT]]',
        '$dynamic_keyword_target(S_internal_parent,$ptascii("parent")) = eps',
        '$dynamic_keyword_error(S_internal_parent,$ptascii("parent")) = eps',
        *final(previous,stdout)]
    return checks


def error_step(state, previous, message, api):
    call, query = 'pconfigcall_' + previous, 'pvalue_' + previous
    return [*step(state,previous),
        state + '.TODO = (THROW_SEARCH n_error_' + state + ') :: ptask_throw_' + state + '*',
        state + '.OBJECTS[n_error_' + state + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = "Error"', 'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + state + ',n_error_' + state + ',"message")) = (' + term(message.encode()) + ')',
        '$throwable_field(' + state + ',n_error_' + state + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + state + ',n_error_' + state + ',"file")) = ($call_sourcefile(' + state + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + state + ',n_error_' + state + ',"trace") = PARRAY n_trace_' + state,
        state + '.ARRAYS[n_trace_' + state + '].ITEMS = (ENTRY (KINT 0) (DIRECT (PARRAY n_frame_' + state + '))) :: pentry_trace_' + state + '*',
        '$trace_array_field(' + state + ',n_frame_' + state + ',$ptascii("function")) = PSTRING $ptascii(' + json.dumps(api) + ')',
        '$trace_array_field(' + state + ',n_frame_' + state + ',$ptascii("line")) = PINT ' + call + '.LINE',
        '$trace_array_field(' + state + ',n_frame_' + state + ',$ptascii("args")) = PARRAY n_args_' + state,
        state + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT ' + query + ')]',
        state + '.CURRENT = ' + previous + '.CURRENT', state + '.EVENTS = ' + previous + '.EVENTS',
        state + '.CLASSCONSTANTINIT = eps', state + '.CONSTCONTEXT = eps', *public(state)]


def error_assertions(main, case, stdout):
    global_message = 'Cannot access "self" when no class scope is active'
    parent_message = 'Cannot access "parent" when current class scope has no parent'
    return ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reach('S_global','S_initial',1,'self::K',21), 'S_global.CURRENT = eps', 'S_global.FRAMES = eps',
        '$dynamic_keyword_target(S_global,$ptascii("self")) = eps',
        '$dynamic_keyword_error(S_global,$ptascii("self")) = (' + term(global_message.encode()) + ')',
        *error_step('S_global_throw','S_global',global_message,'defined'),
        *reach('S_root','S_global_throw',0,'parent::K',8),
        'S_root.CURRENT = (pcallcontext_root)',
        '$class_named(S_root.CLASSNAMES,$ptascii("v52root")) = (porigin_root)',
        'pcallcontext_root.LEXICAL_CLASS = (porigin_root)', 'pcallcontext_root.CALLED_CLASS = (porigin_root)',
        '$class_at(S_root.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.PARENT = eps',
        '$dynamic_keyword_target(S_root,$ptascii("parent")) = eps',
        '$dynamic_keyword_error(S_root,$ptascii("parent")) = (' + term(parent_message.encode()) + ')',
        '$string_carrier_valid(S_root,pvalue_S_root)',
        *error_step('S_root_throw','S_root',parent_message,'constant'), *final('S_root_throw',stdout)]


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
        native = json.loads((sources / 'static-native-v52/report.json').read_text())
        assert native['result'] == 'native_observation' and native['stable_inputs'] and native['target'] == types.PROFILE
        for stage, name in CASES.items():
            case = sources / 'static-native-v52' / name
            row, = [item for item in native['records'] if item['id'] == name]
            assert row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            if stage == 'eval':
                expression, = [node for node in nodes(parsed['ast']) if node['node'] == 'Expr_Eval']
                literal, = [node for node in nodes(expression) if node['node'] == 'Scalar_String']
                code = base64.b64decode(literal['fields'][0]['bytes'])
                unit = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                    'profile': 'cli-raw-85', 'source': b64(code)})
                assert unit['accepted']
                checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
                response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked
                checks = eval_assertions(main,response,code,case,row['stdout'])
            else:
                checks = error_assertions(main,case,row['stdout'])
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
    args = parser.parse_args()
    sources, out = args.sources.resolve(), args.output.resolve()
    suite = sources / 'static-native-v52'
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php',
        ROOT / 'adapter/wire.ml', suite / 'run.py', suite / 'report.json']
    for name in CASES.values():
        case = suite / name
        paths += [case / 'main.php', *[case / 'native' / item for item in ['stdout','stderr','process.json','command.json']]]
    if args.phase == 'check':
        for stage in CASES:
            paths += [out / stage / 'protocol.watsup', out / stage / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    assert not (out / (args.phase + '-report.json')).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
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
            for stage in CASES:
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
            report['result'] = 'pass' if len(report['records']) == len(CASES) and all(row['pass'] for row in report['records']) else 'fail'
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

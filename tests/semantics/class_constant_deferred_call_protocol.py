#!/usr/bin/env python3
"""Reached per-value deferred class constants, API Errors, retry and string caches."""
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
STAGES = {'retry': ('static-native-v48', 'requested-only-error-retry', 'V48Lazy::GOOD'),
    'string': ('static-native-v48', 'selected-runtime-string', 'V48String::TEXT')}
b64 = lambda data: base64.b64encode(data).decode()

PREFIX = r"""
dec $test_output_item(pevent) : nat*
def $test_output_item(OUTPUT n*) = n*
def $test_output_item(pevent) = eps -- otherwise
dec $test_outputs(pevent*) : nat*
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output_item(pevent) ++ $test_outputs(pevent_tail*)
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_constant_front(pstate, nat, preqbytes) : bool
def $test_constant_front(S, 0, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
def $test_constant_front(S, 1, preqbytes) = true
  -- if S.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*
  -- if pclassconstantcontext.SELECTION = CLASS_CONST_CALL pconfigcall
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if pconstantcontext.FACTS = [pconstantfact]
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
def $test_constant_front(S, 2, preqbytes) = true
  -- if S.TODO = (DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall) :: ptask_tail*
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
def $test_constant_front(S, 11, preqbytes) = true
  -- if S.TODO = (STMT (NStmtExpression expression metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 11
def $test_constant_front(S, n_stage, preqbytes) = false -- otherwise
dec $test_constant_seek(pstate, nat, preqbytes, nat) : pstate
def $test_constant_seek(S, n_stage, preqbytes, 0) = S
def $test_constant_seek(S, n_stage, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_constant_front(S,n_stage,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_constant_seek(S, n_stage, preqbytes, n) = $test_constant_seek($drive_steps($test_running(S),1),n_stage,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_constant_front(S,n_stage,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""

def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def reach(state, source, stage, query):
    found = state + '_found'
    return [found + ' = $test_constant_seek(' + source + ',' + str(stage) + ',$ptascii(' + json.dumps(query) + '),3000)',
        found + '.COMPLETION = NORMAL \\/ ' + found + '.COMPLETION = BUDGET',
        state + ' = ' + found + '[.COMPLETION = NORMAL]',
        '$test_constant_front(' + state + ',' + str(stage) + ',$ptascii(' + json.dumps(query) + '))']


def step(state, source, result=None):
    found = state + '_found'
    checks = [found + ' = $drive_steps(' + source + ',1)',
        found + '.COMPLETION = NORMAL \\/ ' + found + '.COMPLETION = BUDGET',
        state + ' = ' + found + '[.COMPLETION = NORMAL]']
    if result is not None:
        checks += [state + '.RESULT = KNOWN (' + result + ')',
            state + '.EVENTS = ' + source + '.EVENTS',
            state + '.CLASSCONSTANTCACHE = ' + source + '.CLASSCONSTANTCACHE',
            state + '.CLASSNAMES = ' + source + '.CLASSNAMES', *public(state)]
    return checks


def initialized(state, source, call, desc, context, facts):
    return [*step(state,source),
        state + '.CLASSCONSTANTINIT = ' + context + ' :: ' + source + '.CLASSCONSTANTINIT',
        context + '.DECL = ' + desc + '.ORIGIN', context + '.SELECTION = CLASS_CONST_CALL ' + call,
        context + '.ORIGIN = (' + call + '.SITE)', context + '.LINE = ' + call + '.LINE',
        context + '.PREVIOUS = ' + source + '.CONSTCONTEXT',
        state + '.CONSTCONTEXT = (' + facts + ')', facts + '.ORIGIN = ' + desc + '.ORIGIN',
        facts + '.LINE = ' + call + '.LINE', facts + '.FACTS = eps',
        '$dynamic_class_constant_resume_present(' + state + '.TODO,' + desc + '.ORIGIN,' + call + ')',
        '$class_constant_context_site($class_constant_restore(' + state + ',' + context + ',' + source + '.CLASSCONSTANTINIT),' + context + ')',
        '$dynamic_class_constant_context(' + state + ') = (' + call + ')',
        *[state + '.' + field + ' = ' + source + '.' + field for field in
            ('CLASSCONSTANTCACHE','CLASSCONSTANTHISTORY','ARRAYS','STORE','ALLOCATIONS','EVENTS')], *public(state)]


def assertions(main, case, query, stdout, stage):
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reach('S','S_initial',0,query), 'S.FILEINCLUDEPATH = eps',
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_query)]',
        '$dynamic_class_constant_valid(S,pconfigcall)',
        '$dynamic_class_constant_deferred(S,pconfigcall) = (pclassconstantdesc)',
        '~pclassconstantdesc.FOLDED', 'pclassconstantdesc.TYPE = eps',
        'S.CONSTCONTEXT = eps', 'S.CLASSCONSTANTINIT = eps', 'S.CLASSCONSTANTCACHE = eps',
        '~$class_constant_table_done(S,pclassconstantdesc.OWNER)', *public('S'),
        *initialized('S_init','S','pconfigcall','pclassconstantdesc','pclassconstantcontext_init','pconstantcontext_init'),
        'S_init.TODO = ptask_eval :: (CLASS_CONST_BIND pclassconstantdesc.ORIGIN) :: (DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall) :: ptask_tail*',
        'S_shift = S_init[.TODO = [ptask_eval,CLASS_CONST_BIND pclassconstantdesc.ORIGIN,DISCARD,DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall] ++ ptask_tail*]',
        '~$dynamic_class_constant_resume_present(S_shift.TODO,pclassconstantdesc.ORIGIN,pconfigcall)',
        '~$class_constant_selection_valid($class_constant_restore(S_shift,pclassconstantcontext_init,eps),pclassconstantcontext_init)',
        '~$call_descriptors_valid(S_shift)',
        'pclassconstantcontext_wrong = pclassconstantcontext_init[.LINE = $(pclassconstantcontext_init.LINE + 1)]',
        '~$class_constant_context_site($class_constant_restore(S_init,pclassconstantcontext_wrong,eps),pclassconstantcontext_wrong)',
        'pclassconstantdesc_wrong = pclassconstantdesc[.INITIALIZER = pconfigcall.SITE]',
        '~$dynamic_class_constant_initializer(S,pclassconstantdesc_wrong)']
    if stage == 'retry':
        checks += ['pconfigcall.SELECTION = eps',
            *reach('S_good','S_init',2,query), 'S_good.RESULT = KNOWN (PINT 17)',
            'S_good.CLASSCONSTANTINIT = eps', 'S_good.CONSTCONTEXT = eps',
            'S_good.CLASSCONSTANTCACHE = [pdefaultcache_good]',
            'pdefaultcache_good.ORIGIN = pclassconstantdesc.ORIGIN', 'pdefaultcache_good.VALUE = PINT 17',
            'pdefaultcache_good.CLASS = PVSCALAR',
            'S_good.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [CCCACHE pclassconstantdesc.ORIGIN pconfigcall.SITE (|S.DECLARATIONS|)]',
            '~$class_constant_table_done(S_good,pclassconstantdesc.OWNER)', *public('S_good'),
            *reach('S_bad','S_good',0,'V48Lazy::BAD'),
            'S_bad.TODO = (CONFIG_INVOKE pconfigcall_bad) :: ptask_bad*',
            '$dynamic_class_constant_deferred(S_bad,pconfigcall_bad) = (pclassconstantdesc_bad)',
            '$default_cache_at(S_bad.CLASSCONSTANTCACHE,pclassconstantdesc_bad.ORIGIN) = eps',
            '~$class_constant_cache_trigger(S_bad,pclassconstantdesc.ORIGIN,pconfigcall_bad.SITE,|S_bad.DECLARATIONS|)',
            *initialized('S_bad_init','S_bad','pconfigcall_bad','pclassconstantdesc_bad','pclassconstantcontext_bad','pconstantcontext_bad'),
            *reach('S_catch','S_bad_init',11,'V48Lazy::BAD'),
            'S_catch.CLASSCONSTANTINIT = eps', 'S_catch.CONSTCONTEXT = eps',
            'S_catch.CLASSCONSTANTCACHE = S_good.CLASSCONSTANTCACHE',
            'S_catch.CLASSCONSTANTHISTORY = S_good.CLASSCONSTANTHISTORY',
            '~$class_constant_table_done(S_catch,pclassconstantdesc.OWNER)',
            '$lookup(S_catch.ENV,$ptascii("error")) = (n_error_cell)',
            'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            'S_catch.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
            'pthrowable.ORIGIN = (pconfigcall_bad.SITE)',
            '$string_bytes($throwable_field(S_catch,n_error,"message")) = ($ptascii("Undefined constant \\"V48_LATE\\""))',
            '$throwable_field(S_catch,n_error,"line") = PINT 9',
            '$string_bytes($throwable_field(S_catch,n_error,"file")) = ($call_sourcefile(S_catch.FILES,pconfigcall_bad.SITE))',
            '$throwable_field(S_catch,n_error,"trace") = PARRAY n_trace',
            'S_catch.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$trace_array_field(S_catch,n_frame,$ptascii("function")) = PSTRING $ptascii("constant")',
            '$trace_array_field(S_catch,n_frame,$ptascii("line")) = PINT 9',
            '$trace_array_field(S_catch,n_frame,$ptascii("args")) = PARRAY n_args',
            'pconfigcall_bad.SENT = [NAMED_SENT (KNOWN pvalue_bad_query)]',
            'S_catch.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_bad_query)]', *public('S_catch'),
            *reach('S_retry','S_catch',0,'V48Lazy::BAD'),
            'S_retry.TODO = (CONFIG_INVOKE pconfigcall_retry) :: ptask_retry*',
            '$user_constant_at(S_retry.USERCONSTANTS,$ptascii("V48_LATE")) = (puserconstant_late)',
            'puserconstant_late.VALUE = PINT 31',
            '$default_cache_at(S_retry.CLASSCONSTANTCACHE,pclassconstantdesc_bad.ORIGIN) = eps',
            *step('S_retry_init','S_retry'), *reach('S_retry_done','S_retry_init',2,'V48Lazy::BAD'),
            'S_retry_done.RESULT = KNOWN (PINT 31)',
            'S_retry_done.CLASSCONSTANTCACHE = [pdefaultcache_good,pdefaultcache_bad]',
            'pdefaultcache_bad.ORIGIN = pclassconstantdesc_bad.ORIGIN',
            'pdefaultcache_bad.VALUE = PINT 31', 'pdefaultcache_bad.CLASS = PVSCALAR',
            'S_retry_done.CLASSCONSTANTHISTORY = S_good.CLASSCONSTANTHISTORY ++ [CCCACHE pclassconstantdesc_bad.ORIGIN pconfigcall_retry.SITE (|S_retry.DECLARATIONS|)]',
            'S_retry_done.CLASSCONSTANTINIT = eps', 'S_retry_done.CONSTCONTEXT = eps',
            '~$class_constant_table_done(S_retry_done,pclassconstantdesc.OWNER)', *public('S_retry_done'),
            *reach('S_again','S_retry_done',0,query), *step('S_done','S_again','PINT 17'),
            'S_done.CLASSCONSTANTHISTORY = S_again.CLASSCONSTANTHISTORY']
    else:
        checks += ['pconfigcall.SELECTION = (n_selection)',
            '$user_constant_at(S.USERCONSTANTS,$ptascii("V48_TEXT")) = (puserconstant_text)',
            'puserconstant_text.VALUE = PSTRING_CARRIER (REQUEST_STRING n_string) $ptascii("old")',
            'puserconstant_text.CLASS = PVSTRING false', '$string_carrier_valid(S,puserconstant_text.VALUE)',
            *reach('S_fact','S_init',1,query),
            'S_fact.CONSTCONTEXT = (pconstantcontext_fact)', 'pconstantcontext_fact.FACTS = [pconstantfact]',
            'pconstantfact.ORIGIN = pclassconstantdesc.INITIALIZER',
            'pconstantfact.VALUE = (puserconstant_text.VALUE)', 'pconstantfact.CLASS = PVSTRING false',
            '$class_constant_facts_valid(S_fact,pclassconstantdesc.ORIGIN,[pconstantfact])',
            *public('S_fact'),
            'pconstantfact_wrong = pconstantfact[.CLASS = PVSTRING true]',
            '~$class_constant_facts_valid(S_fact,pclassconstantdesc.ORIGIN,[pconstantfact_wrong])',
            'S_fact_wrong = S_fact[.CONSTCONTEXT = (pconstantcontext_fact[.FACTS = [pconstantfact_wrong]])]',
            '~$call_descriptors_valid(S_fact_wrong)',
            'pconstantfact_dangling = pconstantfact[.VALUE = (PSTRING_CARRIER (REQUEST_STRING (|S_fact.STRINGDATA|)) $ptascii("old"))]',
            '~$class_constant_facts_valid(S_fact,pclassconstantdesc.ORIGIN,[pconstantfact_dangling])',
            'S_fact_dangling = S_fact[.CONSTCONTEXT = (pconstantcontext_fact[.FACTS = [pconstantfact_dangling]])]',
            '~$call_descriptors_valid(S_fact_dangling)',
            *reach('S_cached','S_fact',2,query), 'S_cached.RESULT = KNOWN puserconstant_text.VALUE',
            'S_cached.CLASSCONSTANTCACHE = [pdefaultcache_text]',
            'pdefaultcache_text.ORIGIN = pclassconstantdesc.ORIGIN',
            'pdefaultcache_text.VALUE = puserconstant_text.VALUE', 'pdefaultcache_text.CLASS = PVSTRING false',
            '$class_constant_cache_value_valid(S_cached,pdefaultcache_text)',
            'S_cached.CLASSCONSTANTINIT = eps', 'S_cached.CONSTCONTEXT = eps', *public('S_cached'),
            'pdefaultcache_wrong = pdefaultcache_text[.CLASS = PVSTRING true]',
            '~$class_constant_cache_value_valid(S_cached,pdefaultcache_wrong)',
            '~$call_descriptors_valid(S_cached[.CLASSCONSTANTCACHE = [pdefaultcache_wrong]])',
            'pdefaultcache_dangling = pdefaultcache_text[.VALUE = PSTRING_CARRIER (REQUEST_STRING (|S_cached.STRINGDATA|)) $ptascii("old")]',
            '~$class_constant_cache_value_valid(S_cached,pdefaultcache_dangling)',
            '~$call_descriptors_valid(S_cached[.CLASSCONSTANTCACHE = [pdefaultcache_dangling]])',
            *reach('S_again','S_cached',0,query),
            '$lookup(S_again.ENV,$ptascii("value")) = (n_value_cell)',
            'S_again.STORE[n_value_cell] = DEFINED pvalue_new', '$string_bytes(pvalue_new) = ($ptascii("new"))',
            '$user_constant_at(S_again.USERCONSTANTS,$ptascii("V48_TEXT")) = (puserconstant_text)',
            'S_again.CLASSCONSTANTCACHE = S_cached.CLASSCONSTANTCACHE',
            'S_again.TODO = (CONFIG_INVOKE pconfigcall_again) :: ptask_again*',
            'pconfigcall_again.SELECTION = (n_selection_again)', 'n_selection_again =/= n_selection',
            *step('S_done','S_again'), 'S_done.RESULT = KNOWN puserconstant_text.VALUE',
            '$string_same(puserconstant_text.VALUE,pdefaultcache_text.VALUE) = (true)',
            'S_done.CLASSCONSTANTCACHE = S_cached.CLASSCONSTANTCACHE',
            'S_done.CLASSCONSTANTHISTORY = S_cached.CLASSCONSTANTHISTORY', *public('S_done')]
    checks += ['S_final = $drive_steps(S_done,10000)', 'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CLASSCONSTANTINIT = eps', 'S_final.CONSTCONTEXT = eps',
        '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(stdout) + ')',
        '~$class_constant_table_done(S_final,pclassconstantdesc.OWNER)', *public('S_final')]
    return checks

def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for stage in names:
            suite, case_name, constant = STAGES[stage]
            case = sources / suite / case_name
            native = json.loads((case.parent / 'report.json').read_text())
            row, = [item for item in native['records'] if item['id'] == case_name]
            assert native['result'] == 'native_observation' and native['stable_inputs']
            assert native['target'] == types.PROFILE and row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted'], parsed
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            checks = assertions(main, case, constant, row['stdout'], stage)
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
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
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names, out, sources = args.stage or list(STAGES), args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for name in names:
        suite, case, _ = STAGES[name]
        paths += [sources / suite / 'report.json', sources / suite / 'run.py', sources / suite / case / 'main.php']
        paths += [sources / suite / case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    assert not (out / (label + '-report.json')).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())), 'inputs': before,
        'implementation_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'records': [], 'agreement_credit': 0, 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
        else:
            mods = [str(ROOT / item) for item in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                target = out / name
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *mods,
                    str(target / 'protocol.watsup')], target / label, 90, ROOT)
                passed = runner.returncode == 0 and runner.stdout == b'true\n' and not runner.stderr
                report['records'].append({'id': name, 'pass': passed, 'runner_exit': runner.returncode,
                    'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]), flush=True)
                if not passed:
                    break
        report['result'] = 'pass' if args.phase == 'fixtures' or len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'], record['premises'] = False, 0
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['result'] == 'pass' else 1)


if __name__ == '__main__':
    main()

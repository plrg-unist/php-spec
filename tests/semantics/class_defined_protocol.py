#!/usr/bin/env python3
"""Reached class-qualified defined lookup, lexical visibility and loader authority."""
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
STAGES = {'loaded': ('static-native-v44', 'loaded-inherited-visibility', 'V44Child::OPEN'),
    'autoload': ('static-native-v44', 'selected-named-autoload', 'V44Loaded::READY')}
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
dec $test_defined_front(pstate, nat, preqbytes) : bool
def $test_defined_front(S, 0, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
def $test_defined_front(S, 1, preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))
  -- if pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
  -- if $lookup(S.ENV,$ptascii("name")) = (n_cell)
  -- if $(n_cell < |S.STORE|)
  -- if S.STORE[n_cell] = DEFINED pvalue_argument
  -- if $string_bytes(pvalue_argument) = (pautoloadcall.NAME)
def $test_defined_front(S, 2, preqbytes) = true
  -- if S.TODO = (DYNAMIC_DEFINED_RESUME pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
def $test_defined_front(S, n_stage, preqbytes) = false -- otherwise
dec $test_defined_seek(pstate, nat, preqbytes, nat) : pstate
def $test_defined_seek(S, n_stage, preqbytes, 0) = S
def $test_defined_seek(S, n_stage, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_defined_front(S,n_stage,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_defined_seek(S, n_stage, preqbytes, n) = $test_defined_seek($drive_steps($test_running(S),1),n_stage,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_defined_front(S,n_stage,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def reach(state, source, stage, query):
    found = state + '_found'
    return [found + ' = $test_defined_seek(' + source + ',' + str(stage) + ',$ptascii(' + json.dumps(query) + '),3000)',
        found + '.COMPLETION = NORMAL \\/ ' + found + '.COMPLETION = BUDGET',
        state + ' = ' + found + '[.COMPLETION = NORMAL]',
        '$test_defined_front(' + state + ',' + str(stage) + ',$ptascii(' + json.dumps(query) + '))']


def step(state, source, result=None):
    found = state + '_found'
    checks = [found + ' = $drive_steps(' + source + ',1)',
        found + '.COMPLETION = NORMAL \\/ ' + found + '.COMPLETION = BUDGET',
        state + ' = ' + found + '[.COMPLETION = NORMAL]']
    if result is not None:
        checks += [state + '.RESULT = KNOWN (PBOOL ' + result + ')',
            state + '.EVENTS = ' + source + '.EVENTS',
            state + '.CLASSCONSTANTCACHE = ' + source + '.CLASSCONSTANTCACHE',
            state + '.CLASSNAMES = ' + source + '.CLASSNAMES', *public(state)]
    return checks


def assertions(main, case, query, stdout, stage):
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reach('S','S_initial',0,query), 'S.FILEINCLUDEPATH = eps',
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_query)]',
        '$string_bytes(pvalue_query) = ($ptascii(' + json.dumps(query) + '))',
        '$string_carrier_valid(S,pvalue_query)', '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_defined_valid(S,pconfigcall)', *public('S')]
    if stage == 'loaded':
        checks += ['S.CURRENT = eps', 'pconfigcall.SELECTION = eps',
            '$class_named(S.CLASSNAMES,$ptascii("v44child")) = (porigin_child)',
            '$class_named(S.CLASSNAMES,$ptascii("v44base")) = (porigin_base)',
            'porigin_child =/= porigin_base',
            '$class_constant_lookup(S,porigin_child,$ptascii("OPEN"),|S.CLASSES|) = (pclassconstantdesc_open)',
            'pclassconstantdesc_open.OWNER = porigin_base', 'pclassconstantdesc_open.FOLDED',
            '$class_constant_visible(S,pclassconstantdesc_open)',
            '$class_constant_lookup(S,porigin_base,$ptascii("HIDDEN"),|S.CLASSES|) = (pclassconstantdesc_hidden)',
            '$class_constant_lookup(S,porigin_base,$ptascii("SECRET"),|S.CLASSES|) = (pclassconstantdesc_secret)',
            '~$class_constant_visible(S,pclassconstantdesc_hidden)', '~$class_constant_visible(S,pclassconstantdesc_secret)']
        checks += step('S_yes','S','true')
        for label, value in [('site','pconfigcall[.SITE = PORIGIN 0 eps]'),
                ('line','pconfigcall[.LINE = $(pconfigcall.LINE + 1)]'),
                ('nonce','pconfigcall[.SELECTION = (0)]')]:
            checks += ['~$dynamic_defined_valid(S,' + value + ')',
                'S_' + label + ' = S[.TODO = (CONFIG_INVOKE (' + value + ')) :: ptask_tail*]',
                '~$call_descriptors_valid(S_' + label + ')']
        checks += ['~$dynamic_defined_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("V44Child::open"))))]])',
            *reach('S_global','S_yes',0,'V44Base::HIDDEN'), 'S_global.CURRENT = eps', *public('S_global')]
        checks += step('S_no','S_global','false')
        checks += reach('S_scope','S_no',0,'V44Base::HIDDEN')
        checks += ['S_scope.CURRENT = (pcallcontext)', '$method_current_scope(S_scope) = (porigin_base)',
            '$target_called_class(S_scope,pcallcontext.TARGET) = (porigin_child)',
            '$class_constant_visible(S_scope,pclassconstantdesc_hidden)',
            '$class_constant_visible(S_scope,pclassconstantdesc_secret)', *public('S_scope')]
        checks += step('S_scope_yes','S_scope','true')
        checks += reach('S_private','S_scope_yes',0,'V44Base::SECRET')
        checks += ['$method_current_scope(S_private) = (porigin_base)', *public('S_private')]
        checks += step('S_private_yes','S_private','true')
        finish = 'S_private_yes'
    else:
        checks += ['pconfigcall.SELECTION = (n_selection)',
            '$(n_selection < |S.SELECTEDCALLS|)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINED',
            '$class_named(S.CLASSNAMES,$ptascii("v44loaded")) = eps', '$autoload_pending(S,$ptascii("V44Loaded"))']
        checks += step('S_next','S')
        checks += ['S_next.TODO = (AUTO_NEXT pautoloadcall) :: ptask_after*',
            'pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall', 'pautoloadcall.RESUME = DYNAMIC_DEFINED_RESUME pconfigcall',
            'pautoloadcall.NAME = $ptascii("V44Loaded")', 'pautoloadcall.KEY = $ptascii("v44loaded")',
            '$dynamic_defined_autoload_valid(S_next,pautoloadcall)', '$autoload_lookup_mode(pautoloadcall.MODE)',
            '$autoload_active_tasks(S_next.TODO,pautoloadcall.KEY)',
            '~$autoload_pending(S_next,pautoloadcall.NAME)',
            '$autoload_trace_arguments(pconfigcall,pautoloadcall.NAME) = [pvalue_query]', *public('S_next')]
        for label, value in [('name','pautoloadcall[.NAME = $ptascii("V44Unknown")]'),
                ('key','pautoloadcall[.KEY = $ptascii("v44unknown")]'),
                ('line','pautoloadcall[.LINE = $(pautoloadcall.LINE + 1)]'),
                ('resume','pautoloadcall[.RESUME = AUTO_EXPLICIT_DONE pconfigcall]')]:
            checks += ['~$dynamic_defined_autoload_valid(S_next,' + value + ')',
                'S_bad_' + label + ' = S_next[.TODO = (AUTO_NEXT (' + value + ')) :: ptask_after*]',
                '~$call_descriptors_valid(S_bad_' + label + ')']
        for label, value in [('query','pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("V44Loaded"))))]]'),
                ('nonce','pconfigcall[.SELECTION = (|S_next.SELECTEDCALLS|)]'),
                ('site','pconfigcall[.SITE = PORIGIN 0 eps]'),
                ('carrier','pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_next.STRINGDATA|)) ($ptascii("V44Loaded::READY"))))]]')]:
            bad_config = 'pconfigcall_' + label
            bad_call = 'pautoloadcall_' + label
            checks += [bad_config + ' = ' + value,
                bad_call + ' = pautoloadcall[.MODE = AUTO_EXPLICIT ' + bad_config + '][.RESUME = DYNAMIC_DEFINED_RESUME ' + bad_config + ']',
                'S_bad_' + label + ' = S_next[.TODO = (AUTO_NEXT ' + bad_call + ') :: ptask_after*]',
                '~$call_descriptors_valid(S_bad_' + label + ')']
            checks += ['~$dynamic_defined_autoload_valid(S_next,' + bad_call + ')']
            if label == 'carrier':
                checks += ['~$dynamic_defined_valid(S_next,' + bad_config + ')']
        checks += reach('S_loader','S_next',1,query)
        checks += ['S_loader.CURRENT = (pcallcontext_loader)',
            '$autoload_context_call(pcallcontext_loader,S_loader.CURRENT,S_loader.FRAMES) = ((pautoloadcall_loader,pautoloadentry,poperand))',
            'pautoloadcall_loader.MODE = AUTO_EXPLICIT pconfigcall',
            '$autoload_context_valid(S_loader,pcallcontext_loader)',
            '$autoload_lookup_mode(pautoloadcall_loader.MODE)',
            '~$autoload_pending(S_loader,$ptascii("V44Loaded"))',
            '$class_named(S_loader.CLASSNAMES,$ptascii("v44loaded")) = eps',
            '$trace_context(S_loader,S_loader.ENV,S_loader.CURRENT) = [ptraceframe_loader,ptraceframe_api]',
            'ptraceframe_loader.FILE = eps', 'ptraceframe_loader.LINE = $(-1)',
            'ptraceframe_api.FUNCTION = $ptascii("defined")',
            'ptraceframe_api.ARGS = $trace_indexed_args([pvalue_query],0)',
            'ptraceframe_api.LINE = pconfigcall.LINE',
            'ptraceframe_api.FILE = $call_sourcefile(S_loader.FILES,pconfigcall.SITE)', *public('S_loader')]
        checks += reach('S_resume','S_loader',2,query)
        checks += ['S_resume.TODO = (DYNAMIC_DEFINED_RESUME pconfigcall) :: ptask_resume*',
            '$class_named(S_resume.CLASSNAMES,$ptascii("v44loaded")) = (porigin_loaded)',
            '$dynamic_defined_valid(S_resume,pconfigcall)', *public('S_resume')]
        checks += step('S_loaded','S_resume','true')
        checks += reach('S_missing','S_loaded',0,'V44Loaded::MISSING')
        checks += ['$class_named(S_missing.CLASSNAMES,$ptascii("v44loaded")) = (porigin_loaded)',
            '~$autoload_pending(S_missing,$ptascii("V44Loaded"))', *public('S_missing')]
        checks += step('S_missing_no','S_missing','false')
        checks += reach('S_unknown','S_missing_no',0,'V44Unknown::READY')
        checks += ['$autoload_pending(S_unknown,$ptascii("V44Unknown"))', *public('S_unknown')]
        checks += step('S_unknown_next','S_unknown')
        checks += ['S_unknown_next.TODO = (AUTO_NEXT pautoloadcall_unknown) :: ptask_unknown*',
            'pautoloadcall_unknown.NAME = $ptascii("V44Unknown")',
            '$dynamic_defined_autoload_valid(S_unknown_next,pautoloadcall_unknown)', *public('S_unknown_next')]
        checks += reach('S_unknown_resume','S_unknown_next',2,'V44Unknown::READY')
        checks += ['$class_named(S_unknown_resume.CLASSNAMES,$ptascii("v44unknown")) = eps', *public('S_unknown_resume')]
        checks += step('S_unknown_no','S_unknown_resume','false')
        finish = 'S_unknown_no'
    checks += ['S_final = $drive_steps(' + finish + ',3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FILEINCLUDEPATH = eps', 'S_final.USERCONSTANTS = eps',
        '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(stdout) + ')', *public('S_final')]
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

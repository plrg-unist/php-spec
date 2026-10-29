#!/usr/bin/env python3
"""Anonymous constructor named reference tails retain cells and ordered aliases."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_variadic_cases.json'
SOURCE_SHA = '6b0836c51a8acd2a923d5dca572f49fb54dbb910f9a7b6496f157489aaf92939'

PREFIX = r'''
dec $ctor_tail_output_item(pevent) : ptbytes
def $ctor_tail_output_item(OUTPUT ptbytes) = ptbytes
def $ctor_tail_output_item(pevent) = eps -- otherwise
dec $ctor_tail_output(pevent*) : ptbytes
def $ctor_tail_output(eps) = eps
def $ctor_tail_output(pevent :: pevent_tail*) = $ctor_tail_output_item(pevent) ++ $ctor_tail_output(pevent_tail*)
dec $ctor_tail_site(pstate,porigin) : bool
def $ctor_tail_site(S,porigin) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata) = 5
def $ctor_tail_site(S,porigin) = false -- otherwise
dec $ctor_tail_stage(pstate,nat) : bool
def $ctor_tail_stage(S,0) = true
  -- if S.TODO = (NAMED_ARGS (METHOD_TARGET n porigin) eps 3 pnamedargs (porigin_site) z) :: ptask_tail*
  -- if $ctor_tail_site(S,porigin_site)
def $ctor_tail_stage(S,1) = true
  -- if S.TODO = [VARIADIC_BEGIN porigin]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $ctor_tail_site(S,porigin_site)
def $ctor_tail_stage(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 14
def $ctor_tail_stage(S,n) = false -- otherwise
dec $ctor_tail_seek(pstate,nat,nat) : pstate
def $ctor_tail_seek(S,n_mode,n) = S -- if $ctor_tail_stage(S,n_mode)
def $ctor_tail_seek(S,n_mode,0) = S -- if ~$ctor_tail_stage(S,n_mode)
def $ctor_tail_seek(S,n_mode,n) = $ctor_tail_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ctor_tail_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ctor_tail_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_sent_raw = $ctor_tail_seek(S_initial[.COMPLETION = NORMAL],0,4096)',
        r'S_sent_raw.COMPLETION = NORMAL \/ S_sent_raw.COMPLETION = BUDGET',
        'S_sent = S_sent_raw[.COMPLETION = NORMAL]',
        '$ctor_tail_stage(S_sent,0)', 'S_sent.CURRENT = eps',
        'S_sent.TODO = (NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 3 pnamedargs (porigin_site) z) :: ptask_tail*',
        '$target_function(S_sent,METHOD_TARGET n_object porigin_ctor) = (pfunction)',
        'pfunction.SIGNATURE.PARAMETERS = [psparam_fixed,psparam_tail]',
        'psparam_fixed.NAME = $ptascii("ignored")',
        '~psparam_fixed.BYREF', '~psparam_fixed.VARIADIC', 'psparam_fixed.TYPE = eps',
        'psparam_tail.NAME = $ptascii("values")',
        'psparam_tail.BYREF', 'psparam_tail.VARIADIC',
        'psparam_tail.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = [psparam_fixed]',
        '~$call_parameter_reference(S_sent,METHOD_TARGET n_object porigin_ctor,0)',
        '$call_parameter_reference(S_sent,METHOD_TARGET n_object porigin_ctor,1)',
        '$call_parameter_reference(S_sent,METHOD_TARGET n_object porigin_ctor,6)',
        '$lookup(S_sent.ENV,$ptascii("old_alias")) = (n_old)',
        'S_sent.STORE[n_old] = DEFINED pvalue_old_raw',
        '$string_bytes(pvalue_old_raw) = ($ptascii("5"))',
        '$lookup(S_sent.ENV,$ptascii("slot")) = (n_live)',
        '$lookup(S_sent.ENV,$ptascii("other")) = (n_live)',
        'n_old =/= n_live', 'S_sent.STORE[n_live] = DEFINED (PINT 20)',
        'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 20))]',
        'pnamedargs.NAMED = [($ptascii("first"),REFERENCE n_old),($ptascii("second"),REFERENCE n_live)]',
        '$call_reference_operand_valid(S_sent,REFERENCE n_old)',
        '$call_reference_operand_valid(S_sent,REFERENCE n_live)',
        '$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 3 pnamedargs (porigin_site) z)',
        '$call_descriptors_valid(S_sent)', '$ctor_tail_output(S_sent.EVENTS) = eps',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 2 pnamedargs (porigin_site) z)',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 3 pnamedargs[.NAMED = [($ptascii("first"),KNOWN pvalue_old_raw),($ptascii("second"),REFERENCE n_live)]] (porigin_site) z)',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 3 pnamedargs[.NAMED = [($ptascii("second"),REFERENCE n_live),($ptascii("first"),REFERENCE n_old)]] (porigin_site) z)',
        'S_enter_raw = $drive_steps(S_sent,1)',
        r'S_enter_raw.COMPLETION = NORMAL \/ S_enter_raw.COMPLETION = BUDGET',
        'S_enter = S_enter_raw[.COMPLETION = NORMAL]',
        'S_enter.TODO = [NAMED_PREFLIGHT porigin_ctor 0]',
        'S_enter.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
        'pcallcontext.ARGC = 1', 'pcallcontext.EXTRA = eps', 'pcallcontext.HOLES = eps',
        'pcallcontext.NAMED = pnamedargs.NAMED',
        '$lookup(S_enter.ENV,$ptascii("ignored")) = (n_fixed)',
        'S_enter.STORE[n_fixed] = DEFINED (PINT 20)',
        'n_fixed =/= n_old', 'n_fixed =/= n_live',
        'S_enter.STORE[n_old] = DEFINED pvalue_old_raw',
        '$call_task_valid(S_enter,NAMED_PREFLIGHT porigin_ctor 0)',
        'S_begin_raw = $ctor_tail_seek(S_enter,1,4096)',
        r'S_begin_raw.COMPLETION = NORMAL \/ S_begin_raw.COMPLETION = BUDGET',
        'S_begin = S_begin_raw[.COMPLETION = NORMAL]',
        '$ctor_tail_stage(S_begin,1)',
        'S_begin.TODO = [VARIADIC_BEGIN porigin_ctor]',
        'S_begin.STORE[n_old] = DEFINED pvalue_old_raw',
        'S_begin.STORE[n_live] = DEFINED (PINT 20)',
        'S_begin.STORE[n_fixed] = DEFINED (PINT 20)',
        '$variadic_unreceived(S_begin,psparam_tail.NAME)',
        '$call_task_valid(S_begin,VARIADIC_BEGIN porigin_ctor)',
        'S_empty_raw = $drive_steps(S_begin,1)',
        r'S_empty_raw.COMPLETION = NORMAL \/ S_empty_raw.COMPLETION = BUDGET',
        'S_empty = S_empty_raw[.COMPLETION = NORMAL]',
        'S_empty.TODO = [VARIADIC_RECEIVE porigin_ctor 1]',
        '$lookup(S_empty.ENV,$ptascii("values")) = (n_values)',
        'S_empty.STORE[n_values] = DEFINED (PARRAY n_array)',
        'S_empty.ARRAYS[n_array].ITEMS = eps',
        '$variadic_next(S_empty.ARRAYS[n_array],0)',
        '$call_task_valid(S_empty,VARIADIC_RECEIVE porigin_ctor 1)',
        'S_first_raw = $drive_steps(S_empty,1)',
        r'S_first_raw.COMPLETION = NORMAL \/ S_first_raw.COMPLETION = BUDGET',
        'S_first = S_first_raw[.COMPLETION = NORMAL]',
        'S_first.TODO = [NAMED_VARIADIC_RECEIVE porigin_ctor 0]',
        'S_first.STORE[n_old] = DEFINED pvalue_old_raw',
        'S_first.STORE[n_live] = DEFINED (PINT 20)',
        'S_first.ARRAYS[n_array].ITEMS = eps',
        '~$typed_caller_strict(S_first)',
        '~$typed_parameter_source(S_first,psparam_tail)',
        '$call_task_valid(S_first,NAMED_VARIADIC_RECEIVE porigin_ctor 0)',
        'S_second_raw = $drive_steps(S_first,1)',
        r'S_second_raw.COMPLETION = NORMAL \/ S_second_raw.COMPLETION = BUDGET',
        'S_second = S_second_raw[.COMPLETION = NORMAL]',
        'S_second.TODO = [NAMED_VARIADIC_RECEIVE porigin_ctor 1]',
        'S_second.STORE[n_old] = DEFINED (PINT 5)',
        'S_second.STORE[n_live] = DEFINED (PINT 20)',
        'S_second.STORE[n_fixed] = DEFINED (PINT 20)',
        'S_second.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING $ptascii("first")) (ALIAS n_old)]',
        '$variadic_next(S_second.ARRAYS[n_array],0)',
        'S_second.CURRENT = (pcallcontext_second)',
        'pcallcontext_second.NAMED = pnamedargs.NAMED',
        '$call_task_valid(S_second,NAMED_VARIADIC_RECEIVE porigin_ctor 1)',
        '~$call_task_valid(S_second[.TODO = [NAMED_VARIADIC_RECEIVE porigin_ctor 0]],NAMED_VARIADIC_RECEIVE porigin_ctor 0)',
        'S_collected_raw = $drive_steps(S_second,1)',
        r'S_collected_raw.COMPLETION = NORMAL \/ S_collected_raw.COMPLETION = BUDGET',
        'S_collected = S_collected_raw[.COMPLETION = NORMAL]',
        'S_collected.TODO = [NAMED_VARIADIC_RECEIVE porigin_ctor 2]',
        'S_collected.STORE[n_old] = DEFINED (PINT 5)',
        'S_collected.STORE[n_live] = DEFINED (PINT 20)',
        'S_collected.STORE[n_fixed] = DEFINED (PINT 20)',
        'S_collected.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING $ptascii("first")) (ALIAS n_old),ENTRY (KSTRING $ptascii("second")) (ALIAS n_live)]',
        '$variadic_next(S_collected.ARRAYS[n_array],0)',
        '$call_task_valid(S_collected,NAMED_VARIADIC_RECEIVE porigin_ctor 2)',
        '$call_descriptors_valid(S_collected)',
        '$heap_valid($heap_graph(S_collected))',
        '$ctor_tail_output(S_collected.EVENTS) = eps',
        'S_late_raw = $ctor_tail_seek(S_collected,2,4096)',
        r'S_late_raw.COMPLETION = NORMAL \/ S_late_raw.COMPLETION = BUDGET',
        'S_late = S_late_raw[.COMPLETION = NORMAL]',
        '$ctor_tail_stage(S_late,2)',
        '$ctor_tail_output(S_late.EVENTS) = $ptascii("first:5|second:20|fixed|20|")',
        '$lookup(S_late.ENV,$ptascii("old_alias")) = (n_old)',
        '$lookup(S_late.ENV,$ptascii("slot")) = (n_live)',
        '$lookup(S_late.ENV,$ptascii("other")) = (n_live)',
        'S_late.STORE[n_old] = DEFINED (PINT 6)',
        'S_late.STORE[n_live] = DEFINED (PINT 21)',
        '$call_descriptors_valid(S_late)', '$heap_valid($heap_graph(S_late))',
        'S_done = $drive_steps(S_late,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$ctor_tail_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-constructor-variadic-binding-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row.get('stdout_template_base64', row['stdout_base64'])).replace(b'{FILE}', os.fsencode(source))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, source, Path(__file__),
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'source_sha256': SOURCE_SHA, 'inputs_before': before, 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        checks = assertions(checked['fixture'], os.fsencode(source), stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), derived_guards=4, fixture_sha256=sha(fixture))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

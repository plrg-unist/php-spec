#!/usr/bin/env python3
"""Eval method calls bind fresh local defaults for by-reference formals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_method_parameter_cases.json'
SOURCE_SHA = '9636141591d7961bb922cf95437a823a26534dcd7198e85021ab4e2bc1d1f396'

PREFIX = r'''
dec $am158_output_item(pevent) : ptbytes
def $am158_output_item(OUTPUT ptbytes) = ptbytes
def $am158_output_item(pevent) = eps -- otherwise
dec $am158_output(pevent*) : ptbytes
def $am158_output(eps) = eps
def $am158_output(pevent :: pevent_tail*) = $am158_output_item(pevent) ++ $am158_output(pevent_tail*)
dec $am158_method(pstate,porigin) : bool
def $am158_method(S,PORIGIN 1 pcpath) = true
  -- if $class_method_origin(S.CLASSES,PORIGIN 1 pcpath) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("calculate")
  -- if |pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS| = 2
def $am158_method(S,porigin) = false -- otherwise
dec $am158_site(pstate,int) : bool
def $am158_site(S,z) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $origin_node(S.SOURCES,porigin_site) = (NExprMethodCall expression (NIdentifier (BYTES text) metadata_name) (SEQUENCE phpType7*) metadata)
  -- if $base64(text) = $ptascii("calculate")
  -- if $source_line(metadata) = z
def $am158_site(S,z) = false -- otherwise
dec $am158_stage(pstate,nat) : bool
def $am158_stage(S,0) = true
  -- if S.TODO = [NAMED_PREFLIGHT porigin 0]
  -- if $am158_method(S,porigin) /\ $am158_site(S,16)
def $am158_stage(S,1) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if $am158_method(S,porigin) /\ $am158_site(S,16)
def $am158_stage(S,2) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if $am158_method(S,porigin) /\ $am158_site(S,17)
def $am158_stage(S,3) = true
  -- if S.TODO = [DEFAULT_RECEIVE porigin 0]
  -- if $am158_method(S,porigin) /\ $am158_site(S,17)
def $am158_stage(S,4) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 1]
  -- if $am158_method(S,porigin) /\ $am158_site(S,17)
def $am158_stage(S,5) = true
  -- if S.TODO = [DEFAULT_RECEIVE porigin 1]
  -- if $am158_method(S,porigin) /\ $am158_site(S,17)
def $am158_stage(S,6) = true
  -- if S.TODO = [NAMED_PREFLIGHT porigin 0]
  -- if $am158_method(S,porigin) /\ $am158_site(S,18)
def $am158_stage(S,7) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if $am158_method(S,porigin) /\ $am158_site(S,18)
def $am158_stage(S,n) = false -- otherwise
dec $am158_seek(pstate,nat,nat) : pstate
def $am158_seek(S,n_mode,n) = S -- if $am158_stage(S,n_mode)
def $am158_seek(S,n_mode,0) = S -- if ~$am158_stage(S,n_mode)
def $am158_seek(S,n_mode,n) = $am158_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$am158_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $am158_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $am158_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$am158_stage({state},{stage})',
    ]


def assertions(fixture, filename, code, response, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait.EVALCONTEXTS,1) = (pevalcontext)',
        'pevalcontext.BYTES = ' + term(code),
        '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')',
        'S_entered.COMPLETION = NORMAL',
        'S_entered.CLASSES = [pclassdesc]',
        'pclassdesc.ORIGIN = PORIGIN 1 pcpath_class',
        'pclassdesc.EARLY', 'pclassdesc.PARENT = eps',
        '$class_named(S_entered.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        'pclassdesc.METHODS = [pmethoddesc]',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
        'porigin_method = PORIGIN 1 pcpath_method',
        '$class_method_origin(S_entered.CLASSES,porigin_method) = (pmethoddesc)',
        'pmethoddesc.NAME = $ptascii("calculate")',
        'pmethoddesc.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam_value,psparam_last]',
        'psparam_value.NAME = $ptascii("value")', 'psparam_value.BYREF',
        'psparam_value.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '~psparam_value.REQUIRED', '~psparam_value.VARIADIC',
        'psparam_last.NAME = $ptascii("last")', '~psparam_last.BYREF',
        'psparam_last.TYPE = psparam_value.TYPE', '~psparam_last.REQUIRED',
        '$default_at(pmethoddesc.FUNCTION.DEFAULTS,0) = (pdefault_value)',
        'pdefault_value.KIND = PDSTORED',
        '$compiled_read(S_entered,pdefault_value.ORIGIN) = (PINT 7)',
        '$default_at(pmethoddesc.FUNCTION.DEFAULTS,1) = (pdefault_last)',
        'pdefault_last.KIND = PDSTORED',
        '$compiled_read(S_entered,pdefault_last.ORIGIN) = (PINT 2)',
        '$class_state_valid(S_entered)', '$call_descriptors_valid(S_entered)',
        *seek('S_entered', 'S_first_preflight', 0),
        'S_first_preflight.CURRENT = (pcallcontext_first)',
        'pcallcontext_first.TARGET = METHOD_TARGET n_first porigin_method',
        'pcallcontext_first.RECEIVER = (n_first)',
        'pcallcontext_first.CALLSITE = (porigin_first)',
        'pcallcontext_first.ARGC = 2', 'pcallcontext_first.HOLES = [0]',
        '$lookup(S_first_preflight.ENV,$ptascii("value")) = eps',
        '$call_task_valid(S_first_preflight,S_first_preflight.TODO[0])',
        *seek('S_first_preflight', 'S_first_type', 1),
        '$lookup(S_first_type.ENV,$ptascii("value")) = (n_value_first)',
        'S_first_type.STORE[n_value_first] = DEFINED (PINT 7)',
        '$call_task_valid(S_first_type,S_first_type.TODO[0])',
        *seek('S_first_type', 'S_second_type', 2),
        'S_second_type.CURRENT = (pcallcontext_second)',
        'pcallcontext_second.TARGET = METHOD_TARGET n_second porigin_method',
        'pcallcontext_second.RECEIVER = (n_second)',
        'pcallcontext_second.ARGC = 0', 'pcallcontext_second.HOLES = eps',
        'n_first =/= n_second',
        '$am158_output(S_second_type.EVENTS) = $ptascii("14|")',
        '$lookup(S_second_type.ENV,$ptascii("value")) = eps',
        *seek('S_second_type', 'S_second_default', 3),
        'S_second_default.TODO = [DEFAULT_RECEIVE porigin_method 0]',
        '$call_task_valid(S_second_default,S_second_default.TODO[0])',
        'S_second_bound_raw = $drive_steps(S_second_default,1)',
        'S_second_bound_raw.COMPLETION = BUDGET',
        'S_second_bound = S_second_bound_raw[.COMPLETION = NORMAL]',
        '$am158_stage(S_second_bound,4)',
        '$lookup(S_second_bound.ENV,$ptascii("value")) = (n_value_second)',
        'n_value_first =/= n_value_second',
        'S_second_bound.STORE[n_value_second] = DEFINED (PINT 7)',
        '$lookup(S_second_bound.ENV,$ptascii("last")) = eps',
        *seek('S_second_bound', 'S_second_last', 5),
        'S_second_last.TODO = [DEFAULT_RECEIVE porigin_method 1]',
        '$call_task_valid(S_second_last,S_second_last.TODO[0])',
        *seek('S_second_last', 'S_third_preflight', 6),
        'S_third_preflight.CURRENT = (pcallcontext_third)',
        'pcallcontext_third.TARGET = METHOD_TARGET n_first porigin_method',
        'pcallcontext_third.ARGC = 2', 'pcallcontext_third.HOLES = [0]',
        '$am158_output(S_third_preflight.EVENTS) = $ptascii("14|12|")',
        '$lookup(S_third_preflight.ENV,$ptascii("value")) = eps',
        *seek('S_third_preflight', 'S_third_bound', 7),
        '$lookup(S_third_bound.ENV,$ptascii("value")) = (n_value_third)',
        'n_value_third =/= n_value_first', 'n_value_third =/= n_value_second',
        'S_third_bound.STORE[n_value_third] = DEFINED (PINT 7)',
        '$call_task_valid(S_third_bound,S_third_bound.TODO[0])',
        'S_done = $drive_steps(S_third_bound,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.CURRENT = eps', 'S_done.EVALCONTEXTS = eps',
        '$am158_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-method-eval-default-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', os.fsencode(source))
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
        code, = [base64.b64decode(n['fields'][0]['bytes']) for n in nodes(parsed['ast'])
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace Method158Author;')]
        parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                        'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
        assert parsed_eval['accepted'] is True
        checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
        assert checked_eval['ok'] is True
        response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked_eval['fixture']
        checks = assertions(checked['fixture'], os.fsencode(source), code, response, stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + c + '\n' for c in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 900, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), reached_conditions=len(checks),
                      derived_conditions=0, derived_guards=0, fixture_sha256=sha(fixture))
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

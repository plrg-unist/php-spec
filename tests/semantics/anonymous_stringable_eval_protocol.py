#!/usr/bin/env python3
"""Real eval anonymous Stringable linking, callbacks and diagnostic name views."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_stringable_cases.json'
SOURCE_SHA = '50676330675a5426880316ac5e9f392b5fffc825397d0aad12f7f1dffe09bdeb'
PREFIX = r'''
dec $string157_eval_output_item(pevent) : ptbytes
def $string157_eval_output_item(OUTPUT ptbytes) = ptbytes
def $string157_eval_output_item(pevent) = eps -- otherwise
dec $string157_eval_output(pevent*) : ptbytes
def $string157_eval_output(eps) = eps
def $string157_eval_output(pevent :: pevent_tail*) = $string157_eval_output_item(pevent) ++ $string157_eval_output(pevent_tail*)
dec $string157_eval_site(pstate,porigin,ptbytes) : bool
def $string157_eval_site(S,porigin,ptbytes) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprVariable (BYTES text) metadata)
  -- if $base64(text) = ptbytes
  -- if $source_line(metadata) = 18
def $string157_eval_site(S,porigin,ptbytes) = false -- otherwise
dec $string157_eval_stage(pstate,nat) : bool
def $string157_eval_stage(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = PORIGIN 1 pcpath
  -- if S.TODO = (STMT (NStmtReturn (NExprNew statement (SEQUENCE eps) metadata_new) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 3
def $string157_eval_stage(S,1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n (PORIGIN 1 pcpath)) eps 0 eps (porigin_site) 18) :: ptask_tail*
  -- if $string157_eval_site(S,porigin_site,$ptascii("first157"))
def $string157_eval_stage(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = PORIGIN 1 pcpath
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 6
def $string157_eval_stage(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin_site 18) :: (EMIT 18) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("unit4"))
def $string157_eval_stage(S,4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n (PORIGIN 1 pcpath)) eps 0 eps (porigin_site) 18) :: ptask_tail*
  -- if $string157_eval_site(S,porigin_site,$ptascii("second157"))
def $string157_eval_stage(S,5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin_site 18) :: (EMIT 18) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("unit5"))
def $string157_eval_stage(S,n) = false -- otherwise
dec $string157_eval_seek(pstate,nat,nat) : pstate
def $string157_eval_seek(S,n_mode,n) = S -- if $string157_eval_stage(S,n_mode)
def $string157_eval_seek(S,n_mode,0) = S -- if ~$string157_eval_stage(S,n_mode)
def $string157_eval_seek(S,n_mode,n) = $string157_eval_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$string157_eval_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $string157_eval_seek(S,n_mode,n) = S -- otherwise
'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $string157_eval_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$string157_eval_stage({state},{stage})',
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
        *seek('S_entered', 'S_factory', 0),
        'S_factory.ORIGIN = (PORIGIN 1 pcpath_return)',
        '$origin_node(S_factory.SOURCES,PORIGIN 1 pcpath_return) = (NStmtReturn (NExprNew statement_new (SEQUENCE eps) metadata_new) metadata_return)',
        '$origin_child(S_factory.ORIGIN,[PCFIELD 0]) = (porigin_new)',
        '$anonymous_new_pending(S_factory,porigin_new) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN 1 pcpath_class',
        'pclassdesc.LINE = 3', 'pclassdesc.PARENT = eps',
        'pclassdesc.INTERFACES = [$ptascii("Stringable")]', '~pclassdesc.EARLY',
        '$anonymous_class_name(pevalcontext.FILE,3,0) = (pclassdesc.NAME)',
        '$class_named(S_factory.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$source_unit(S_factory.SOURCES,1) = (pcunit)',
        '$anonymous_rtd_count(S_factory,pcunit) = (1)',
        'S_factory.CURRENT = (pcallcontext_make)',
        'porigin_make = pcallcontext_make.FUNCTION',
        '$function_at($all_functions(S_factory),porigin_make) = (pfunction_make)',
        'pfunction_make.NAME = ' + term(b'String157Author\\make157'),
        '$class_state_valid(S_factory)', '$call_descriptors_valid(S_factory)',
        *seek('S_factory', 'S_pending', 1),
        '$lookup(S_pending.ENV,$ptascii("first157")) = (n_first_cell)',
        '$lookup(S_pending.ENV,$ptascii("second157")) = (n_second_cell)',
        'S_pending.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
        'S_pending.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'n_first =/= n_second',
        'S_pending.OBJECTS[n_first] = INSTANCE pclassdesc.ORIGIN',
        'S_pending.OBJECTS[n_second] = INSTANCE pclassdesc.ORIGIN',
        '$effective_method(S_pending,pclassdesc.ORIGIN,$ptascii("__toString"),|S_pending.CLASSES|) = (pmethoddesc)',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
        'porigin_method = PORIGIN 1 pcpath_method',
        'pmethoddesc.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', '~pmethoddesc.STATIC',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = eps',
        'pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]',
        '~pmethoddesc.FUNCTION.SIGNATURE.BYREF',
        '$class_named(S_pending.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$anonymous_new_available(S_pending,pclassdesc)',
        '$anonymous_runtime_declaration(S_pending.DECLARATIONS,pclassdesc.ORIGIN)',
        'S_pending.TODO = (CALL_ARGS (METHOD_TARGET n_first porigin_method) eps 0 eps (porigin_site) 18) :: (STRINGIFY_RESULT n_first porigin_site 18) :: (EMIT 18) :: ptask_tail*',
        'porigin_site = PORIGIN 0 pcpath_first',
        '$stringify_pending(S_pending,METHOD_TARGET n_first porigin_method,porigin_site)',
        '$stringify_method_selected(S_pending,n_first,porigin_method,porigin_site)',
        '$task_nodes(STRINGIFY_RESULT n_first porigin_site 18) = [HOBJECT n_first]',
        '$call_task_valid(S_pending,S_pending.TODO[0])',
        '~$call_task_valid(S_pending,CALL_ARGS (METHOD_TARGET n_first porigin_method) eps 0 eps (porigin_site) 19)',
        '$string157_eval_output(S_pending.EVENTS) = $ptascii("stringable|")',
        '$class_state_valid(S_pending)', '$call_descriptors_valid(S_pending)',
        '$heap_valid($heap_graph(S_pending))',
        *seek('S_pending', 'S_body', 2),
        'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_first porigin_method',
        'pcallcontext.FUNCTION = porigin_method', 'pcallcontext.RECEIVER = (n_first)',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext.CALLSITE = (porigin_site)',
        'pcallcontext.LINE = 18', 'pcallcontext.ARGC = 0',
        'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
        'pcallcontext.WRAPPER = eps',
        '$stringify_context(S_body,pcallcontext)',
        '$call_function_name(S_body,pmethoddesc.FUNCTION) = pclassdesc.NAME ++ $ptascii("::__toString")',
        '$return_function_name(S_body,pmethoddesc.FUNCTION) = $ptascii("class@anonymous::__toString")',
        '$call_function_kind(S_body) = $ptascii("method")',
        '$call_function_kind(S_body[.CURRENT = (pcallcontext[.TARGET = porigin_make])]) = $ptascii("function")',
        '$c_string($call_function_name(S_body,pmethoddesc.FUNCTION)) = $ptascii("class@anonymous")',
        '$return_function_name(S_body,pmethoddesc.FUNCTION[.NAME = $ptascii("fixture-clone")]) = $ptascii("fixture-clone")',
        '$return_function_name(S_body[.CURRENT = (pcallcontext[.TARGET = porigin_make])],pmethoddesc.FUNCTION) = pmethoddesc.FUNCTION.NAME',
        '$string157_eval_output(S_body.EVENTS) = $ptascii("stringable|")',
        '$call_descriptors_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        *seek('S_body', 'S_returned', 3),
        'S_returned.TODO = (STRINGIFY_RESULT n_first porigin_site 18) :: (EMIT 18) :: ptask_tail*',
        'S_returned.RESULT = KNOWN pvalue_first', '$string_bytes(pvalue_first) = ($ptascii("unit4"))',
        '$stringify_result_valid(S_returned,n_first,porigin_site,18)',
        '$string157_eval_output(S_returned.EVENTS) = $ptascii("stringable|body|")',
        'S_returned.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
        'S_returned.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '(HOBJECT n_first) <- S_returned.ALLOCATIONS',
        '(HOBJECT n_second) <- S_returned.ALLOCATIONS',
        '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
        *seek('S_returned', 'S_second', 4),
        'S_second.TODO = (CALL_ARGS (METHOD_TARGET n_second porigin_method) eps 0 eps (porigin_second_site) 18) :: (STRINGIFY_RESULT n_second porigin_second_site 18) :: (EMIT 18) :: ptask_second_tail*',
        'porigin_site =/= porigin_second_site',
        '$stringify_pending(S_second,METHOD_TARGET n_second porigin_method,porigin_second_site)',
        '$string157_eval_output(S_second.EVENTS) = $ptascii("stringable|body|unit4|")',
        *seek('S_second', 'S_second_return', 5),
        'S_second_return.RESULT = KNOWN pvalue_second', '$string_bytes(pvalue_second) = ($ptascii("unit5"))',
        '$stringify_result_valid(S_second_return,n_second,porigin_second_site,18)',
        '$string157_eval_output(S_second_return.EVENTS) = $ptascii("stringable|body|unit4|body|")',
        'S_second_return.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
        'S_second_return.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$class_state_valid(S_second_return)', '$call_descriptors_valid(S_second_return)',
        '$heap_valid($heap_graph(S_second_return))',
        'S_done = $drive_steps(S_second_return,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$string157_eval_output(S_done.EVENTS) = ' + term(stdout),
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-stringable-eval-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', os.fsencode(source))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__), source,
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(p): sha(p) for p in watched}
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
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace String157Author;')]
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
        report.update(passed=True, conditions=len(checks), derived_guards=4, derived_conditions=4, reached_conditions=len(checks)-4, fixture_sha256=sha(fixture))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(p): sha(p) for p in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

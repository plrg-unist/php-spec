#!/usr/bin/env python3
"""Private anonymous method references share a real caller cell."""
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
SOURCE_SHA = 'd12505661821a6794ef10557f333cf70faebb12cf1249d5b15664e2c74dd6f52'

PREFIX = r'''
dec $anon_method_output_item(pevent) : ptbytes
def $anon_method_output_item(OUTPUT ptbytes) = ptbytes
def $anon_method_output_item(pevent) = eps -- otherwise
dec $anon_method_output(pevent*) : ptbytes
def $anon_method_output(eps) = eps
def $anon_method_output(pevent :: pevent_tail*) = $anon_method_output_item(pevent) ++ $anon_method_output(pevent_tail*)
dec $anon_method_site(pstate,porigin,int) : bool
def $anon_method_site(S,porigin,z) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprMethodCall expression (NIdentifier (BYTES text) metadata_name) (SEQUENCE phpType7*) metadata)
  -- if $base64(text) = $ptascii("accept158Review")
  -- if $source_line(metadata) = z
def $anon_method_site(S,porigin,z) = false -- otherwise
dec $anon_method_stage(pstate,nat) : bool
def $anon_method_stage(S,0) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin) eps 2 poperand* (porigin_site) z) :: ptask_tail*
  -- if $anon_method_site(S,porigin_site,13)
def $anon_method_stage(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 14
def $anon_method_stage(S,2) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin) phpType7* 0 eps (porigin_site) z) :: ptask_tail*
  -- if $anon_method_site(S,porigin_site,16)
def $anon_method_stage(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 20
def $anon_method_stage(S,n) = false -- otherwise
dec $anon_method_seek(pstate,nat,nat) : pstate
def $anon_method_seek(S,n_mode,n) = S -- if $anon_method_stage(S,n_mode)
def $anon_method_seek(S,n_mode,0) = S -- if ~$anon_method_stage(S,n_mode)
def $anon_method_seek(S,n_mode,n) = $anon_method_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_method_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $anon_method_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $anon_method_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$anon_method_stage({state},{stage})',
    ]


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_initial.CLASSES = [pclassdesc]', 'pclassdesc.EARLY',
        'pclassdesc.PARENT = eps', 'pclassdesc.INTERFACES = eps',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_sent', 0),
        'S_sent.CURRENT = (pcallcontext_run)',
        'pcallcontext_run.RECEIVER = (n_object)',
        'S_sent.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
        'pcallcontext_run.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext_run.CALLED_CLASS = (pclassdesc.ORIGIN)',
        'S_sent.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_accept) eps 2 poperand* (porigin_site) z_call) :: ptask_tail*',
        '$class_method_origin(S_sent.CLASSES,porigin_accept) = (pmethoddesc)',
        'pmethoddesc.NAME = $ptascii("accept158Review")',
        'pmethoddesc.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE', '~pmethoddesc.STATIC', '~pmethoddesc.ABSTRACT',
        '$target_function(S_sent,METHOD_TARGET n_object porigin_accept) = (pfunction)',
        'pfunction = pmethoddesc.FUNCTION',
        'pfunction.SIGNATURE.PARAMETERS = [psparam_head,psparam_same]',
        'psparam_head.BYREF', 'psparam_same.BYREF',
        'psparam_head.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]', 'psparam_same.TYPE = eps',
        'pfunction.SIGNATURE.RETURNS = eps', '~pfunction.SIGNATURE.BYREF',
        '$call_parameter_reference(S_sent,METHOD_TARGET n_object porigin_accept,0)',
        '$call_parameter_reference(S_sent,METHOD_TARGET n_object porigin_accept,1)',
        '$lookup(S_sent.ENV,$ptascii("local158Review")) = (n_shared)',
        '$lookup(S_sent.ENV,$ptascii("alias158Review")) = (n_shared)',
        'S_sent.STORE[n_shared] = DEFINED pvalue_raw', '$string_bytes(pvalue_raw) = ($ptascii("7"))',
        'poperand* = [REFERENCE n_shared,REFERENCE n_shared]',
        '$call_reference_operand_valid(S_sent,REFERENCE n_shared)',
        '$method_call_selected(S_sent,METHOD_TARGET n_object porigin_accept,porigin_site)',
        '$method_site_scope(S_sent,porigin_accept,porigin_site) = (pclassdesc.ORIGIN)',
        '$anon_method_output(S_sent.EVENTS) = eps',
        '$class_state_valid(S_sent)', '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
        '~$call_task_valid(S_sent,CALL_ARGS (METHOD_TARGET n_object porigin_accept) eps 1 poperand* (porigin_site) z_call)',
        '~$call_task_valid(S_sent,CALL_ARGS (METHOD_TARGET n_object porigin_accept) eps 2 ([KNOWN pvalue_raw,REFERENCE n_shared]) (porigin_site) z_call)',
        '~$call_task_valid(S_sent,CALL_ARGS (METHOD_TARGET n_object porigin_accept) eps 2 poperand* (porigin_site) $(z_call + 1))',
        'S_entered_raw = $drive_steps(S_sent,1)',
        r'S_entered_raw.COMPLETION = NORMAL \/ S_entered_raw.COMPLETION = BUDGET',
        'S_entered = S_entered_raw[.COMPLETION = NORMAL]',
        'S_entered.TODO = [TYPE_RECEIVE porigin_accept 0]',
        'S_entered.CURRENT = (pcallcontext_accept)',
        'pcallcontext_accept.TARGET = METHOD_TARGET n_object porigin_accept',
        'pcallcontext_accept.FUNCTION = porigin_accept',
        'pcallcontext_accept.RECEIVER = (n_object)',
        'pcallcontext_accept.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext_accept.CALLED_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext_accept.CALLSITE = (porigin_site)',
        'pcallcontext_accept.ARGC = 2', 'pcallcontext_accept.HOLES = eps',
        'pcallcontext_accept.EXTRA = eps', 'pcallcontext_accept.NAMED = eps',
        '$missing_argument_function_name(S_entered,pfunction) = $ptascii("class@anonymous::accept158Review")',
        '$missing_argument_function_name(S_entered,pfunction[.NAME = $ptascii("fixture-clone")]) = $ptascii("fixture-clone")',
        '$lookup(S_entered.ENV,$ptascii("head")) = (n_shared)',
        '$lookup(S_entered.ENV,$ptascii("same")) = (n_shared)',
        'S_entered.STORE[n_shared] = DEFINED pvalue_raw',
        '~$typed_caller_strict(S_entered)', '~$typed_parameter_source(S_entered,psparam_head)',
        '$call_task_valid(S_entered,TYPE_RECEIVE porigin_accept 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_coerced_raw = $drive_steps(S_entered,1)',
        r'S_coerced_raw.COMPLETION = NORMAL \/ S_coerced_raw.COMPLETION = BUDGET',
        'S_coerced = S_coerced_raw[.COMPLETION = NORMAL]',
        'S_coerced.TODO = [TYPE_RECEIVE porigin_accept 1]',
        'S_coerced.STORE[n_shared] = DEFINED (PINT 7)',
        '$lookup(S_coerced.ENV,$ptascii("head")) = (n_shared)',
        '$lookup(S_coerced.ENV,$ptascii("same")) = (n_shared)',
        '$call_reference_operand_valid(S_coerced,REFERENCE n_shared)',
        *seek('S_coerced', 'S_back', 1),
        'S_back.CURRENT = (pcallcontext_run)',
        '$lookup(S_back.ENV,$ptascii("local158Review")) = (n_shared)',
        '$lookup(S_back.ENV,$ptascii("alias158Review")) = (n_shared)',
        'S_back.STORE[n_shared] = DEFINED pvalue_written',
        '$string_bytes(pvalue_written) = ($ptascii("written"))',
        '$anon_method_output(S_back.EVENTS) = $ptascii("private|head-int|same-cell|")',
        '$call_descriptors_valid(S_back)', '$heap_valid($heap_graph(S_back))',
        *seek('S_back', 'S_bad', 2),
        'S_bad.CURRENT = (pcallcontext_run)',
        'S_bad.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_accept) phpType7_bad* 0 eps (porigin_bad_site) z_bad) :: ptask_bad_tail*',
        'porigin_site =/= porigin_bad_site',
        '$method_call_selected(S_bad,METHOD_TARGET n_object porigin_accept,porigin_bad_site)',
        '$call_task_valid(S_bad,S_bad.TODO[0])',
        'S_bad.STORE[n_shared] = DEFINED pvalue_written',
        '$anon_method_output(S_bad.EVENTS) = $ptascii("private|head-int|same-cell|written|")',
        *seek('S_bad', 'S_caught', 3),
        'S_caught.CURRENT = (pcallcontext_run)',
        '$lookup(S_caught.ENV,$ptascii("local158Review")) = (n_shared)',
        '$lookup(S_caught.ENV,$ptascii("alias158Review")) = (n_shared)',
        'S_caught.STORE[n_shared] = DEFINED pvalue_written',
        '$lookup(S_caught.ENV,$ptascii("error158Review")) = (n_error_cell)',
        'S_caught.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        '$throwable_live(S_caught,n_error)',
        '$string_bytes($throwable_field(S_caught,n_error,"message")) = ($ptascii("class@anonymous(): Argument #1 ($head) could not be passed by reference"))',
        '$throwable_field(S_caught,n_error,"line") = PINT 16',
        '$call_descriptors_valid(S_caught)', '$heap_valid($heap_graph(S_caught))',
        'S_done = $drive_steps(S_caught,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$anon_method_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-method-parameter-binding-', dir=ROOT / '.tools'))
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
        checks = assertions(checked['fixture'], os.fsencode(source), stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), reached_conditions=len(checks)-4,
                      derived_conditions=4, derived_guards=4, fixture_sha256=sha(fixture))
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

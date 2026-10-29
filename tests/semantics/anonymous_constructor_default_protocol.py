#!/usr/bin/env python3
"""Real anonymous constructor named holes, ordered reception and publication retry."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_arity_cases.json'
SOURCE_SHA = 'c60ee6b229f8394a89ab2dcd365bacc987ed3aa29f4c97a58741b32177b0ffa4'

PREFIX = r'''
dec $ctor_default_output_item(pevent) : ptbytes
def $ctor_default_output_item(OUTPUT ptbytes) = ptbytes
def $ctor_default_output_item(pevent) = eps -- otherwise
dec $ctor_default_is_output(pevent) : bool
def $ctor_default_is_output(OUTPUT ptbytes) = true
def $ctor_default_is_output(pevent) = false -- otherwise
dec $ctor_default_output(pevent*) : ptbytes
def $ctor_default_output(eps) = eps
def $ctor_default_output(pevent :: pevent_tail*) = $ctor_default_output_item(pevent) ++ $ctor_default_output(pevent_tail*)
dec $ctor_default_last(pevent*,ptbytes) : ptbytes
def $ctor_default_last(eps,ptbytes) = ptbytes
def $ctor_default_last((OUTPUT ptbytes) :: pevent_tail*,ptbytes_old) = $ctor_default_last(pevent_tail*,ptbytes)
def $ctor_default_last(pevent :: pevent_tail*,ptbytes) = $ctor_default_last(pevent_tail*,ptbytes)
  -- if ~$ctor_default_is_output(pevent)
dec $ctor_default_method(pstate,porigin) : bool
def $ctor_default_method(S,porigin) = true
  -- if $class_method_origin(S.CLASSES,porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
  -- if |pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS| = 4
def $ctor_default_method(S,porigin) = false -- otherwise
dec $ctor_default_stage(pstate,nat) : bool
def $ctor_default_stage(S,0) = true
  -- if S.ORIGIN = (PORIGIN 1 pcpath)
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if |phpType7*| = 3
def $ctor_default_stage(S,1) = true
  -- if S.TODO = (NAMED_ARGS (METHOD_TARGET n porigin) eps 3 pnamedargs (porigin_site) z) :: ptask_tail*
  -- if $ctor_default_method(S,porigin)
def $ctor_default_stage(S,2) = true
  -- if S.TODO = [NAMED_PREFLIGHT porigin 1]
  -- if $ctor_default_method(S,porigin)
def $ctor_default_stage(S,3) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if $ctor_default_method(S,porigin)
def $ctor_default_stage(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ctor_default_method(S,pcallcontext.FUNCTION)
  -- if $ctor_default_last(S.EVENTS,eps) = $ptascii("ctor|")
def $ctor_default_stage(S,n) = false -- otherwise
dec $ctor_default_seek(pstate,nat,nat) : pstate
def $ctor_default_seek(S,n_mode,n) = S -- if $ctor_default_stage(S,n_mode)
def $ctor_default_seek(S,n_mode,0) = S -- if ~$ctor_default_stage(S,n_mode)
def $ctor_default_seek(S,n_mode,n) = $ctor_default_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ctor_default_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ctor_default_seek(S,n_mode,n) = S -- otherwise
dec $ctor_default_publications(pdeclaration*,porigin) : nat
dec $ctor_default_publication(pdeclaration,porigin) : bool
def $ctor_default_publications(eps,porigin) = 0
def $ctor_default_publications((PDRCLASS porigin pdeclcause) :: pdeclaration_tail*,porigin) = $(1 + $ctor_default_publications(pdeclaration_tail*,porigin))
def $ctor_default_publications(pdeclaration :: pdeclaration_tail*,porigin) = $ctor_default_publications(pdeclaration_tail*,porigin)
  -- if ~$ctor_default_publication(pdeclaration,porigin)
def $ctor_default_publication(PDRCLASS porigin pdeclcause,porigin) = true
def $ctor_default_publication(pdeclaration,porigin) = false -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, code, response, stdout):
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait.EVALCONTEXTS,1) = (pevalcontext)',
        'pevalcontext.BYTES = ' + term(code),
        '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')',
        'S_entered.COMPLETION = NORMAL',
        'S_front_raw = $ctor_default_seek(S_entered,0,4096)',
        r'S_front_raw.COMPLETION = NORMAL \/ S_front_raw.COMPLETION = BUDGET',
        'S_front = S_front_raw[.COMPLETION = NORMAL]',
        '$ctor_default_stage(S_front,0)',
        'S_front.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_front,porigin_new) = (pclassdesc)',
        '~pclassdesc.EARLY',
        '$anonymous_parent_class_name($ptascii("Base152Review"),pevalcontext.FILE,12,0) = (pclassdesc.NAME)',
        '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$class_named(S_front.CLASSNAMES,$ptascii("base152review")) = (porigin_base)',
        '$effective_method(S_front,pclassdesc.ORIGIN,$ptascii("__construct"),|S_front.CLASSES|) = (pmethoddesc)',
        'pmethoddesc.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam_first,psparam_second,psparam_third,psparam_fourth]',
        'psparam_first.NAME = $ptascii("first")', 'psparam_second.NAME = $ptascii("second")',
        'psparam_third.NAME = $ptascii("third")', 'psparam_fourth.NAME = $ptascii("fourth")',
        'psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'psparam_second.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
        'psparam_third.TYPE = psparam_first.TYPE', 'psparam_fourth.TYPE = psparam_first.TYPE',
        'psparam_first.REQUIRED', '~psparam_second.REQUIRED', '~psparam_third.REQUIRED', '~psparam_fourth.REQUIRED',
        'psparam_first.DEFAULT = PSNONE',
        'psparam_second.DEFAULT = PSDEFAULT expression_second "string"',
        '$parser_literal(expression_second) = (PSTRING $ptascii("default"))',
        '$default_at(pmethoddesc.FUNCTION.DEFAULTS,1) = (pdefault_second)',
        'pdefault_second.KIND = PDSTORED',
        '$compiled_read(S_front,pdefault_second.ORIGIN) = (PSTRING $ptascii("default"))',
        '$default_at(pmethoddesc.FUNCTION.DEFAULTS,2) = (pdefault_third)',
        '$compiled_read(S_front,pdefault_third.ORIGIN) = (PINT 30)',
        '$default_at(pmethoddesc.FUNCTION.DEFAULTS,3) = (pdefault_fourth)',
        '$compiled_read(S_front,pdefault_fourth.ORIGIN) = (PINT 40)',
        '$class_state_valid(S_front)', '$call_descriptors_valid(S_front)',
        'S_link_raw = $drive_steps(S_front,1)',
        r'S_link_raw.COMPLETION = NORMAL \/ S_link_raw.COMPLETION = BUDGET',
        'S_link = S_link_raw[.COMPLETION = NORMAL]',
        'S_link.TODO = S_front.TODO', 'S_link.ORIGIN = S_front.ORIGIN',
        'S_link.EVENTS = S_front.EVENTS', 'S_link.ALLOCATIONS = S_front.ALLOCATIONS',
        '$class_named(S_link.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$ctor_default_publications(S_link.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        'S_sent_raw = $ctor_default_seek(S_link,1,4096)',
        r'S_sent_raw.COMPLETION = NORMAL \/ S_sent_raw.COMPLETION = BUDGET',
        'S_sent = S_sent_raw[.COMPLETION = NORMAL]',
        'S_sent.TODO = (NAMED_ARGS (METHOD_TARGET n_failed porigin_ctor) eps 3 pnamedargs (porigin_new) z_new) :: ptask_tail*',
        'porigin_ctor = pmethoddesc.FUNCTION.ORIGIN',
        'S_sent.OBJECTS[n_failed] = INSTANCE pclassdesc.ORIGIN',
        '(HOBJECT n_failed) <- S_sent.ALLOCATIONS',
        'pnamedargs.SLOTS = [NAMED_SENT (KNOWN pvalue_bad),NAMED_HOLE,NAMED_SENT (KNOWN (PINT 3)),NAMED_SENT (KNOWN (PINT 4))]',
        'pvalue_bad = $string_literal_value(PSTRING $ptascii("bad"))',
        'pnamedargs.NAMED = eps',
        '$ctor_default_output(S_sent.EVENTS) = $ptascii("fourth|first|third|")',
        'S_sent.DECLARATIONS = S_link.DECLARATIONS',
        '$call_descriptors_valid(S_sent)',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_failed porigin_ctor) eps 2 pnamedargs (porigin_new) z_new)',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_failed porigin_ctor) eps 3 pnamedargs[.SLOTS = [NAMED_SENT (KNOWN pvalue_bad),NAMED_SENT (KNOWN (PINT 3)),NAMED_HOLE,NAMED_SENT (KNOWN (PINT 4))]] (porigin_new) z_new)',
        'S_hole_raw = $ctor_default_seek(S_sent,2,4096)',
        r'S_hole_raw.COMPLETION = NORMAL \/ S_hole_raw.COMPLETION = BUDGET',
        'S_hole = S_hole_raw[.COMPLETION = NORMAL]',
        'S_hole.TODO = [NAMED_PREFLIGHT porigin_ctor 1]',
        'S_hole.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_failed porigin_ctor',
        'pcallcontext.FUNCTION = porigin_ctor', 'pcallcontext.CALLSITE = (porigin_new)',
        'pcallcontext.ARGC = 4', 'pcallcontext.HOLES = [1]',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc.ORIGIN)',
        '~$named_defined(S_hole,$ptascii("second"))',
        '$lookup(S_hole.ENV,$ptascii("first")) = (n_first)',
        'S_hole.STORE[n_first] = DEFINED pvalue_bad',
        '$call_descriptors_valid(S_hole)',
        '~$call_task_valid(S_hole,TYPE_RECEIVE porigin_ctor 0)',
        '~$call_task_valid(S_hole,NAMED_PREFLIGHT porigin_ctor 2)',
        'S_type_raw = $ctor_default_seek(S_hole,3,4096)',
        r'S_type_raw.COMPLETION = NORMAL \/ S_type_raw.COMPLETION = BUDGET',
        'S_type = S_type_raw[.COMPLETION = NORMAL]',
        'S_type.TODO = [TYPE_RECEIVE porigin_ctor 0]',
        '$lookup(S_type.ENV,$ptascii("second")) = (n_second)',
        'S_type.STORE[n_second] = DEFINED (PSTRING $ptascii("default"))',
        'S_type.STORE[n_first] = DEFINED pvalue_bad',
        'S_type.CURRENT = (pcallcontext)',
        'S_type.EVENTS = S_sent.EVENTS', 'S_type.DECLARATIONS = S_link.DECLARATIONS',
        '~$typed_caller_strict(S_type)',
        '$call_task_valid(S_type,TYPE_RECEIVE porigin_ctor 0)',
        '$call_function_name(S_type,pmethoddesc.FUNCTION) = pclassdesc.NAME ++ $ptascii("::") ++ pmethoddesc.NAME',
        '$c_string($call_function_name(S_type,pmethoddesc.FUNCTION)) = $ptascii("Base152Review@anonymous")',
        '$missing_argument_function_name(S_type,pmethoddesc.FUNCTION) = $ptascii("Base152Review@anonymous::__construct")',
        '$missing_argument_function_name(S_type[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_base)])],pmethoddesc.FUNCTION) = $ptascii("Base152Review@anonymous::__construct")',
        '$missing_argument_function_name(S_type[.CURRENT = (pcallcontext[.TARGET = METHOD_TARGET n_failed porigin_base])],pmethoddesc.FUNCTION) = pmethoddesc.FUNCTION.NAME',
        '$missing_argument_function_name(S_type,pmethoddesc.FUNCTION[.NAME = $ptascii("altered")]) = $ptascii("altered")',
        'S_fail_raw = $drive_steps(S_type,1)',
        'S_fail_raw.COMPLETION = BUDGET',
        'S_fail = S_fail_raw[.COMPLETION = NORMAL]',
        'S_fail.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_fail.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "TypeError"',
        '$throwable_field(S_fail,n_error,"line") = PINT 13',
        'S_fail.EVENTS = S_type.EVENTS', 'S_fail.DECLARATIONS = S_link.DECLARATIONS',
        'S_retry_raw = $ctor_default_seek(S_fail,0,4096)',
        r'S_retry_raw.COMPLETION = NORMAL \/ S_retry_raw.COMPLETION = BUDGET',
        'S_retry = S_retry_raw[.COMPLETION = NORMAL]',
        'S_retry.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_retry,porigin_new) = eps',
        '$anonymous_new_name(S_retry,porigin_new) = (pclassdesc.NAME)',
        'S_retry.DECLARATIONS = S_link.DECLARATIONS',
        'S_body_raw = $ctor_default_seek(S_retry,4,4096)',
        r'S_body_raw.COMPLETION = NORMAL \/ S_body_raw.COMPLETION = BUDGET',
        'S_body = S_body_raw[.COMPLETION = NORMAL]',
        '$ctor_default_stage(S_body,4)',
        'S_body.CURRENT = (pcallcontext_body)',
        'pcallcontext_body.TARGET = METHOD_TARGET n_success porigin_ctor',
        'n_success =/= n_failed', 'pcallcontext_body.HOLES = [1]',
        '$lookup(S_body.ENV,$ptascii("first")) = (n_success_first)',
        'S_body.STORE[n_success_first] = DEFINED (PINT 1)',
        '$lookup(S_body.ENV,$ptascii("second")) = (n_success_second)',
        'S_body.STORE[n_success_second] = DEFINED (PSTRING $ptascii("default"))',
        '$lookup(S_body.ENV,$ptascii("third")) = (n_success_third)',
        'S_body.STORE[n_success_third] = DEFINED (PINT 3)',
        '$lookup(S_body.ENV,$ptascii("fourth")) = (n_success_fourth)',
        'S_body.STORE[n_success_fourth] = DEFINED (PINT 4)',
        'S_body.DECLARATIONS = S_link.DECLARATIONS',
        'S_done = $drive_steps(S_body,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$ctor_default_output(S_done.EVENTS) = ' + term(stdout),
        '$ctor_default_publications(S_done.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
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


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-constructor-default-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', os.fsencode(source))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__), source,
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
        code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                 if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'namespace Later152Review;')]
        parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                        'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
        assert parsed_eval['accepted'] is True
        checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
        assert checked_eval['ok'] is True
        response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked_eval['fixture']
        checks = assertions(checked['fixture'], os.fsencode(source), code, response, stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1500, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), derived_guards=7, fixture_sha256=sha(fixture))
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

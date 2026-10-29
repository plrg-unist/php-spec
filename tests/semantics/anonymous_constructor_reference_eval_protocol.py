#!/usr/bin/env python3
"""Real eval constructor reference sends, reception writes and caller aliases."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_reference_cases.json'
SOURCE_SHA = '0d9d7e78c012372fae1b49b1e4c0bd7f73b57f39c89631f5ee12df6b45c3c542'
PREFIX = r'''
dec $ref153_eval_output_item(pevent) : ptbytes
def $ref153_eval_output_item(OUTPUT ptbytes) = ptbytes
def $ref153_eval_output_item(pevent) = eps -- otherwise
dec $ref153_eval_output(pevent*) : ptbytes
def $ref153_eval_output(eps) = eps
def $ref153_eval_output(pevent :: pevent_tail*) = $ref153_eval_output_item(pevent) ++ $ref153_eval_output(pevent_tail*)
dec $ref153_eval_is_output(pevent) : bool
def $ref153_eval_is_output(OUTPUT ptbytes) = true
def $ref153_eval_is_output(pevent) = false -- otherwise
dec $ref153_eval_last(pevent*,ptbytes) : ptbytes
def $ref153_eval_last(eps,ptbytes) = ptbytes
def $ref153_eval_last((OUTPUT ptbytes) :: pevent_tail*,ptbytes_old) = $ref153_eval_last(pevent_tail*,ptbytes)
def $ref153_eval_last(pevent :: pevent_tail*,ptbytes) = $ref153_eval_last(pevent_tail*,ptbytes)
  -- if ~$ref153_eval_is_output(pevent)
dec $ref153_eval_ctor(pstate,porigin) : bool
def $ref153_eval_ctor(S,PORIGIN 1 pcpath) = true
  -- if $class_method_origin(S.CLASSES,PORIGIN 1 pcpath) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
  -- if |pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS| = 4
  -- if pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS[3].NAME = $ptascii("last")
def $ref153_eval_ctor(S,porigin) = false -- otherwise
dec $ref153_eval_stage(pstate,nat) : bool
def $ref153_eval_stage(S,0) = true
  -- if S.TODO = (NAMED_ARGS (METHOD_TARGET n porigin) eps 4 pnamedargs (porigin_site) z) :: ptask_tail*
  -- if $ref153_eval_ctor(S,porigin)
def $ref153_eval_stage(S,1) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 3]
  -- if $ref153_eval_ctor(S,porigin)
def $ref153_eval_stage(S,2) = true
  -- if S.CURRENT = eps /\ S.EVALCONTEXTS = eps
  -- if $ref153_eval_last(S.EVENTS,eps) = $ptascii("|after")
def $ref153_eval_stage(S,n) = false -- otherwise
dec $ref153_eval_seek(pstate,nat,nat) : pstate
def $ref153_eval_seek(S,n_mode,n) = S -- if $ref153_eval_stage(S,n_mode)
def $ref153_eval_seek(S,n_mode,0) = S -- if ~$ref153_eval_stage(S,n_mode)
def $ref153_eval_seek(S,n_mode,n) = $ref153_eval_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ref153_eval_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ref153_eval_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, code, response, stdout):
    return [
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
        'S_sent_raw = $ref153_eval_seek(S_entered,0,4096)',
        r'S_sent_raw.COMPLETION = NORMAL \/ S_sent_raw.COMPLETION = BUDGET',
        'S_sent = S_sent_raw[.COMPLETION = NORMAL]',
        '$ref153_eval_stage(S_sent,0)',
        'S_sent.TODO = (NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 4 pnamedargs (porigin_site) z_call) :: ptask_tail*',
        'porigin_site = PORIGIN 1 pcpath_new',
        '$class_method_origin(S_sent.CLASSES,porigin_ctor) = (pmethoddesc)',
        '$class_at(S_sent.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
        'S_sent.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
        '(HOBJECT n_object) <- S_sent.ALLOCATIONS',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam_a,psparam_b,psparam_c,psparam_last]',
        r'~psparam_a.BYREF /\ ~psparam_b.BYREF /\ ~psparam_c.BYREF',
        'psparam_last.BYREF', 'psparam_last.NAME = $ptascii("last")',
        'psparam_last.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'psparam_last.REQUIRED', 'psparam_last.DEFAULT = PSNONE',
        'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 1)),NAMED_SENT (KNOWN (PINT 2)),NAMED_SENT (KNOWN (PINT 3)),NAMED_SENT (REFERENCE n_ref)]',
        'pnamedargs.NAMED = eps',
        'S_sent.STORE[n_ref] = DEFINED pvalue_raw',
        '$string_bytes(pvalue_raw) = ($ptascii("4"))',
        '$call_reference_operand_valid(S_sent,REFERENCE n_ref)',
        '$call_parameter_reference(S_sent,METHOD_TARGET n_object porigin_ctor,3)',
        'S_global_sent = $global_table_view(S_sent)',
        '$lookup(S_global_sent.ENV,$ptascii("x153")) = (n_ref)',
        '$lookup(S_global_sent.ENV,$ptascii("outside153")) = (n_ref)',
        '$lookup(S_sent.ENV,$ptascii("x153")) = (n_ref)',
        '$call_task_valid(S_sent,S_sent.TODO[0])',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 4 pnamedargs (PORIGIN 0 pcpath_new) z_call)',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 4 pnamedargs[.SLOTS = [NAMED_SENT (KNOWN (PINT 1)),NAMED_SENT (KNOWN (PINT 2)),NAMED_SENT (KNOWN (PINT 3)),NAMED_SENT (KNOWN pvalue_raw)]] (porigin_site) z_call)',
        '$class_state_valid(S_sent)', '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
        'S_type_raw = $ref153_eval_seek(S_sent,1,4096)',
        r'S_type_raw.COMPLETION = NORMAL \/ S_type_raw.COMPLETION = BUDGET',
        'S_type = S_type_raw[.COMPLETION = NORMAL]',
        'S_type.TODO = [TYPE_RECEIVE porigin_ctor 3]',
        'S_type.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
        'pcallcontext.CALLSITE = (porigin_site)', 'pcallcontext.ARGC = 4', 'pcallcontext.HOLES = eps',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN)', 'pcallcontext.CALLED_CLASS = (pclassdesc.ORIGIN)',
        '$lookup(S_type.ENV,$ptascii("last")) = (n_ref)',
        'S_type.STORE[n_ref] = DEFINED pvalue_raw',
        '~$typed_caller_strict(S_type)', '~$typed_parameter_source(S_type,psparam_last)',
        '~$typed_reference_cell_source(S_type,n_ref)',
        '$call_task_valid(S_type,TYPE_RECEIVE porigin_ctor 3)',
        'S_coerced_raw = $drive_steps(S_type,1)',
        'S_coerced_raw.COMPLETION = BUDGET',
        'S_coerced = S_coerced_raw[.COMPLETION = NORMAL]',
        'S_coerced.STORE[n_ref] = DEFINED (PINT 4)',
        '$lookup(S_coerced.ENV,$ptascii("last")) = (n_ref)',
        'S_global_coerced = $global_table_view(S_coerced)',
        '$lookup(S_global_coerced.ENV,$ptascii("x153")) = (n_ref)',
        '$lookup(S_global_coerced.ENV,$ptascii("outside153")) = (n_ref)',
        'S_coerced.DECLARATIONS = S_type.DECLARATIONS', 'S_coerced.EVENTS = S_type.EVENTS',
        'S_end_raw = $ref153_eval_seek(S_coerced,2,8192)',
        r'S_end_raw.COMPLETION = NORMAL \/ S_end_raw.COMPLETION = BUDGET',
        'S_end = S_end_raw[.COMPLETION = NORMAL]',
        '$ref153_eval_stage(S_end,2)',
        '$lookup(S_end.ENV,$ptascii("x153")) = (n_ref)',
        '$lookup(S_end.ENV,$ptascii("outside153")) = (n_ref)',
        'S_end.STORE[n_ref] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '$ref153_eval_output(S_end.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_end)', '$call_descriptors_valid(S_end)', '$heap_valid($heap_graph(S_end))',
        'S_done = $drive_steps(S_end,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$ref153_eval_output(S_done.EVENTS) = ' + term(stdout),
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-constructor-reference-eval-', dir=ROOT / '.tools'))
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
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace Ref153Author;')]
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
        report.update(passed=True, conditions=len(checks), fixture_sha256=sha(fixture))
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

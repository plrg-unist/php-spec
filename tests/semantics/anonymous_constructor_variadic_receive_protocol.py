#!/usr/bin/env python3
"""Real eval variadic defaults, named tail collection and empty-array reception."""
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
SOURCE_SHA = 'bbbbaa1e6fb8b56ad6fe3bb5107045239ec2c49151ab84e1fd9c01486c763da6'
PREFIX = r'''
dec $var154_output_item(pevent) : ptbytes
def $var154_output_item(OUTPUT ptbytes) = ptbytes
def $var154_output_item(pevent) = eps -- otherwise
dec $var154_output(pevent*) : ptbytes
def $var154_output(eps) = eps
def $var154_output(pevent :: pevent_tail*) = $var154_output_item(pevent) ++ $var154_output(pevent_tail*)
dec $var154_is_output(pevent) : bool
def $var154_is_output(OUTPUT ptbytes) = true
def $var154_is_output(pevent) = false -- otherwise
dec $var154_last(pevent*,ptbytes) : ptbytes
def $var154_last(eps,ptbytes) = ptbytes
def $var154_last((OUTPUT ptbytes) :: pevent_tail*,ptbytes_old) = $var154_last(pevent_tail*,ptbytes)
def $var154_last(pevent :: pevent_tail*,ptbytes) = $var154_last(pevent_tail*,ptbytes)
  -- if ~$var154_is_output(pevent)
dec $var154_ctor(pstate,porigin,nat) : bool
def $var154_ctor(S,PORIGIN 1 pcpath,0) = true
  -- if $class_method_origin(S.CLASSES,PORIGIN 1 pcpath) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
  -- if |pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS| = 2
  -- if pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS[1].VARIADIC
def $var154_ctor(S,PORIGIN 0 pcpath,1) = true
  -- if $class_method_origin(S.CLASSES,PORIGIN 0 pcpath) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
  -- if |pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS| = 1
  -- if pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS[0].VARIADIC
def $var154_ctor(S,porigin,n) = false -- otherwise
dec $var154_stage(pstate,nat) : bool
def $var154_stage(S,0) = true
  -- if S.TODO = (NAMED_ARGS (METHOD_TARGET n porigin) eps 1 pnamedargs (porigin_site) z) :: ptask_tail*
  -- if $var154_ctor(S,porigin,0)
def $var154_stage(S,1) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if $var154_ctor(S,porigin,0)
def $var154_stage(S,2) = true
  -- if S.TODO = [VARIADIC_BEGIN porigin]
  -- if $var154_ctor(S,porigin,0)
def $var154_stage(S,3) = true
  -- if S.TODO = [NAMED_VARIADIC_RECEIVE porigin 0]
  -- if $var154_ctor(S,porigin,0)
def $var154_stage(S,4) = true
  -- if S.TODO = [VARIADIC_BEGIN porigin]
  -- if $var154_ctor(S,porigin,1)
def $var154_stage(S,5) = true
  -- if S.CURRENT = eps /\ S.EVALCONTEXTS = eps
  -- if $var154_last(S.EVENTS,eps) = $ptascii("|after")
def $var154_stage(S,n) = false -- otherwise
dec $var154_seek(pstate,nat,nat) : pstate
def $var154_seek(S,n_mode,n) = S -- if $var154_stage(S,n_mode)
def $var154_seek(S,n_mode,0) = S -- if ~$var154_stage(S,n_mode)
def $var154_seek(S,n_mode,n) = $var154_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$var154_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $var154_seek(S,n_mode,n) = S -- otherwise
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
        'S_sent_raw = $var154_seek(S_entered,0,4096)',
        r'S_sent_raw.COMPLETION = NORMAL \/ S_sent_raw.COMPLETION = BUDGET',
        'S_sent = S_sent_raw[.COMPLETION = NORMAL]',
        '$var154_stage(S_sent,0)',
        'S_sent.TODO = (NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 1 pnamedargs (porigin_site) z_call) :: ptask_tail*',
        'porigin_site = PORIGIN 1 pcpath_new',
        '$class_method_origin(S_sent.CLASSES,porigin_ctor) = (pmethoddesc)',
        '$class_at(S_sent.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
        'S_sent.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam_head,psparam_rest]',
        'psparam_head.NAME = $ptascii("head")', '~psparam_head.BYREF', '~psparam_head.VARIADIC',
        'psparam_head.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]', '~psparam_head.REQUIRED',
        'psparam_rest.NAME = $ptascii("rest")', '~psparam_rest.BYREF', 'psparam_rest.VARIADIC',
        'psparam_rest.TYPE = psparam_head.TYPE', '~psparam_rest.REQUIRED', 'psparam_rest.DEFAULT = PSNONE',
        '$default_at(pmethoddesc.FUNCTION.DEFAULTS,0) = (pdefault_head)',
        'pdefault_head.KIND = PDSTORED', '$compiled_read(S_sent,pdefault_head.ORIGIN) = (PINT 7)',
        'pnamedargs.SLOTS = eps', 'pnamedargs.NAMED = [($ptascii("last"),KNOWN (PINT 5))]',
        '$named_index(pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS,NAMED_EXTRA $ptascii("last")) = 1',
        '~$named_reference(pmethoddesc.FUNCTION,NAMED_EXTRA $ptascii("last"))',
        '$call_task_valid(S_sent,S_sent.TODO[0])',
        '~$call_task_valid(S_sent,NAMED_ARGS (METHOD_TARGET n_object porigin_ctor) eps 1 pnamedargs (PORIGIN 0 pcpath_new) z_call)',
        '$class_state_valid(S_sent)', '$call_descriptors_valid(S_sent)',
        'S_type_raw = $var154_seek(S_sent,1,4096)',
        r'S_type_raw.COMPLETION = NORMAL \/ S_type_raw.COMPLETION = BUDGET',
        'S_type = S_type_raw[.COMPLETION = NORMAL]',
        'S_type.TODO = [TYPE_RECEIVE porigin_ctor 0]',
        'S_type.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
        'pcallcontext.CALLSITE = (porigin_site)', 'pcallcontext.ARGC = 0', 'pcallcontext.HOLES = eps',
        'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = pnamedargs.NAMED',
        '$lookup(S_type.ENV,$ptascii("head")) = eps',
        '$call_task_valid(S_type,S_type.TODO[0])',
        'S_missing_raw = $drive_steps(S_type,1)', 'S_missing_raw.COMPLETION = BUDGET',
        'S_missing = S_missing_raw[.COMPLETION = NORMAL]',
        'S_missing.TODO = [DEFAULT_RECEIVE porigin_ctor 0]',
        '$lookup(S_missing.ENV,$ptascii("head")) = eps',
        '$call_task_valid(S_missing,S_missing.TODO[0])',
        'S_begin_raw = $var154_seek(S_missing,2,4096)',
        r'S_begin_raw.COMPLETION = NORMAL \/ S_begin_raw.COMPLETION = BUDGET',
        'S_begin = S_begin_raw[.COMPLETION = NORMAL]',
        'S_begin.TODO = [VARIADIC_BEGIN porigin_ctor]',
        '$lookup(S_begin.ENV,$ptascii("head")) = (n_head)',
        'S_begin.STORE[n_head] = DEFINED (PINT 7)',
        '$variadic_unreceived(S_begin,$ptascii("rest"))',
        '$call_task_valid(S_begin,S_begin.TODO[0])',
        '~$call_task_valid(S_begin,VARIADIC_RECEIVE porigin_ctor 1)',
        'S_alloc_raw = $drive_steps(S_begin,1)', 'S_alloc_raw.COMPLETION = BUDGET',
        'S_alloc = S_alloc_raw[.COMPLETION = NORMAL]',
        'S_alloc.TODO = [VARIADIC_RECEIVE porigin_ctor 1]',
        '$lookup(S_alloc.ENV,$ptascii("rest")) = (n_rest)',
        'S_alloc.STORE[n_rest] = DEFINED (PARRAY n_array)',
        'S_alloc.ARRAYS[n_array].ITEMS = eps',
        '$call_task_valid(S_alloc,S_alloc.TODO[0])',
        '~$call_task_valid(S_alloc,VARIADIC_RECEIVE porigin_ctor 0)',
        'S_alloc.EVENTS = S_begin.EVENTS', 'S_alloc.DECLARATIONS = S_begin.DECLARATIONS',
        'S_named_raw = $var154_seek(S_alloc,3,4096)',
        r'S_named_raw.COMPLETION = NORMAL \/ S_named_raw.COMPLETION = BUDGET',
        'S_named = S_named_raw[.COMPLETION = NORMAL]',
        'S_named.TODO = [NAMED_VARIADIC_RECEIVE porigin_ctor 0]',
        '$call_task_valid(S_named,S_named.TODO[0])',
        'S_collected_raw = $drive_steps(S_named,1)', 'S_collected_raw.COMPLETION = BUDGET',
        'S_collected = S_collected_raw[.COMPLETION = NORMAL]',
        'S_collected.TODO = [NAMED_VARIADIC_RECEIVE porigin_ctor 1]',
        'S_collected.STORE[n_rest] = DEFINED (PARRAY n_array)',
        'S_collected.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING $ptascii("last")) (DIRECT (PINT 5))]',
        '$call_task_valid(S_collected,S_collected.TODO[0])',
        'S_collected.EVENTS = S_named.EVENTS', 'S_collected.DECLARATIONS = S_named.DECLARATIONS',
        '$class_state_valid(S_collected)', '$call_descriptors_valid(S_collected)', '$heap_valid($heap_graph(S_collected))',
        'S_empty_raw = $var154_seek(S_collected,4,8192)',
        r'S_empty_raw.COMPLETION = NORMAL \/ S_empty_raw.COMPLETION = BUDGET',
        'S_empty = S_empty_raw[.COMPLETION = NORMAL]',
        'S_empty.TODO = [VARIADIC_BEGIN porigin_empty]',
        '$class_method_origin(S_empty.CLASSES,porigin_empty) = (pmethoddesc_empty)',
        'pmethoddesc_empty.FUNCTION.SIGNATURE.PARAMETERS = [psparam_empty]',
        'psparam_empty.VARIADIC', '~psparam_empty.BYREF', 'psparam_empty.TYPE = eps',
        'S_empty.CURRENT = (pcallcontext_empty)',
        'pcallcontext_empty.ARGC = 0', 'pcallcontext_empty.HOLES = eps',
        'pcallcontext_empty.EXTRA = eps', 'pcallcontext_empty.NAMED = eps',
        '$variadic_unreceived(S_empty,$ptascii("rest"))',
        '$call_task_valid(S_empty,S_empty.TODO[0])',
        'S_empty_alloc_raw = $drive_steps(S_empty,1)', 'S_empty_alloc_raw.COMPLETION = BUDGET',
        'S_empty_alloc = S_empty_alloc_raw[.COMPLETION = NORMAL]',
        'S_empty_alloc.TODO = [VARIADIC_RECEIVE porigin_empty 0]',
        '$lookup(S_empty_alloc.ENV,$ptascii("rest")) = (n_empty_rest)',
        'S_empty_alloc.STORE[n_empty_rest] = DEFINED (PARRAY n_empty_array)',
        'S_empty_alloc.ARRAYS[n_empty_array].ITEMS = eps',
        '$call_task_valid(S_empty_alloc,S_empty_alloc.TODO[0])',
        'S_end_raw = $var154_seek(S_empty_alloc,5,8192)',
        r'S_end_raw.COMPLETION = NORMAL \/ S_end_raw.COMPLETION = BUDGET',
        'S_end = S_end_raw[.COMPLETION = NORMAL]',
        '$var154_stage(S_end,5)', '$var154_output(S_end.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_end)', '$call_descriptors_valid(S_end)', '$heap_valid($heap_graph(S_end))',
        'S_done = $drive_steps(S_end,8192)', 'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$var154_output(S_done.EVENTS) = ' + term(stdout),
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-constructor-variadic-receive-', dir=ROOT / '.tools'))
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
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace Ref154Author;')]
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
        report.update(passed=True, conditions=len(checks), derived_guards=3, reached_conditions=len(checks)-3, fixture_sha256=sha(fixture))
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

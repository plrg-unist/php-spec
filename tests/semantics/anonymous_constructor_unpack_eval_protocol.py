#!/usr/bin/env python3
"""Real eval array-unpack source authority and named-hole default reception."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_unpack_cases.json'
SOURCE_SHA = '69777db9fc8ebea21b3a0a2f881bacd57c791760aa9b46deeb98848f693a4389'
PREFIX = r'''
dec $unpack155_output_item(pevent) : ptbytes
def $unpack155_output_item(OUTPUT ptbytes) = ptbytes
def $unpack155_output_item(pevent) = eps -- otherwise
dec $unpack155_output(pevent*) : ptbytes
def $unpack155_output(eps) = eps
def $unpack155_output(pevent :: pevent_tail*) = $unpack155_output_item(pevent) ++ $unpack155_output(pevent_tail*)
dec $unpack155_is_output(pevent) : bool
def $unpack155_is_output(OUTPUT ptbytes) = true
def $unpack155_is_output(pevent) = false -- otherwise
dec $unpack155_last(pevent*,ptbytes) : ptbytes
def $unpack155_last(eps,ptbytes) = ptbytes
def $unpack155_last((OUTPUT ptbytes) :: pevent_tail*,ptbytes_old) = $unpack155_last(pevent_tail*,ptbytes)
def $unpack155_last(pevent :: pevent_tail*,ptbytes) = $unpack155_last(pevent_tail*,ptbytes)
  -- if ~$unpack155_is_output(pevent)
dec $unpack155_ctor(pstate,porigin) : bool
def $unpack155_ctor(S,PORIGIN 1 pcpath) = true
  -- if $class_method_origin(S.CLASSES,PORIGIN 1 pcpath) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
  -- if |pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS| = 4
def $unpack155_ctor(S,porigin) = false -- otherwise
dec $unpack155_stage(pstate,nat) : bool
def $unpack155_stage(S,0) = true
  -- if S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*
  -- if punpackcall.FUNCTION = METHOD_TARGET n porigin
  -- if $unpack155_ctor(S,porigin)
def $unpack155_stage(S,1) = true
  -- if S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail*
  -- if punpackcall.ARGUMENTS = eps
  -- if punpackcall.FUNCTION = METHOD_TARGET n porigin
  -- if $unpack155_ctor(S,porigin)
def $unpack155_stage(S,2) = true
  -- if S.TODO = [NAMED_PREFLIGHT porigin 1]
  -- if $unpack155_ctor(S,porigin)
def $unpack155_stage(S,3) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if $unpack155_ctor(S,porigin)
def $unpack155_stage(S,4) = true
  -- if S.CURRENT = eps /\ S.EVALCONTEXTS = eps
  -- if $unpack155_last(S.EVENTS,eps) = $ptascii("|after")
def $unpack155_stage(S,n) = false -- otherwise
dec $unpack155_seek(pstate,nat,nat) : pstate
def $unpack155_seek(S,n_mode,n) = S -- if $unpack155_stage(S,n_mode)
def $unpack155_seek(S,n_mode,0) = S -- if ~$unpack155_stage(S,n_mode)
def $unpack155_seek(S,n_mode,n) = $unpack155_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$unpack155_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $unpack155_seek(S,n_mode,n) = S -- otherwise
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
        'S_prep_raw = $unpack155_seek(S_entered,0,4096)',
        r'S_prep_raw.COMPLETION = NORMAL \/ S_prep_raw.COMPLETION = BUDGET',
        'S_prep = S_prep_raw[.COMPLETION = NORMAL]',
        '$unpack155_stage(S_prep,0)',
        'S_prep.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
        'punpackcall.FUNCTION = METHOD_TARGET n_object porigin_ctor',
        'punpackcall.CALLSITE = (porigin_site)', 'porigin_site = PORIGIN 1 pcpath_new',
        'punpackcall.INDEX = 0', 'punpackcall.SENT.SLOTS = eps', 'punpackcall.SENT.NAMED = eps',
        '$unpack_class(S_prep,punpackcall) = (UNPACK_CV)',
        '$class_method_origin(S_prep.CLASSES,porigin_ctor) = (pmethoddesc)',
        '$class_at(S_prep.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
        'S_prep.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam_first,psparam_second,psparam_third,psparam_last]',
        r'~psparam_first.BYREF /\ ~psparam_second.BYREF /\ ~psparam_third.BYREF /\ ~psparam_last.BYREF',
        r'~psparam_first.VARIADIC /\ ~psparam_second.VARIADIC /\ ~psparam_third.VARIADIC /\ ~psparam_last.VARIADIC',
        'psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'psparam_second.TYPE = psparam_first.TYPE', 'psparam_third.TYPE = psparam_first.TYPE', 'psparam_last.TYPE = psparam_first.TYPE',
        '$default_at(pmethoddesc.FUNCTION.DEFAULTS,1) = (pdefault_second)',
        'pdefault_second.KIND = PDSTORED', '$compiled_read(S_prep,pdefault_second.ORIGIN) = (PINT 20)',
        '$lookup(S_prep.ENV,$ptascii("parts")) = (n_parts)',
        'S_prep.STORE[n_parts] = DEFINED (PARRAY n_array)',
        'S_prep.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING $ptascii("third")) (DIRECT (PINT 3)),ENTRY (KSTRING $ptascii("first")) (DIRECT (PINT 1))]',
        '$call_task_valid(S_prep,S_prep.TODO[0])',
        '~$call_task_valid(S_prep,UNPACK_PREP punpackcall[.CALLSITE = (PORIGIN 0 pcpath_new)])',
        '$class_state_valid(S_prep)', '$call_descriptors_valid(S_prep)',
        'S_ready_raw = $drive_steps(S_prep,1)', 'S_ready_raw.COMPLETION = BUDGET',
        'S_ready = S_ready_raw[.COMPLETION = NORMAL]',
        'S_ready.TODO = (UNPACK_NEXT punpackcall (KNOWN (PARRAY n_array)) 0 false) :: ptask_tail*',
        '$call_task_valid(S_ready,S_ready.TODO[0])',
        'S_ready.STORE[n_parts] = DEFINED (PARRAY n_array)',
        'S_ready.EVENTS = S_prep.EVENTS', 'S_ready.DECLARATIONS = S_prep.DECLARATIONS',
        'S_sent_raw = $unpack155_seek(S_ready,1,4096)',
        r'S_sent_raw.COMPLETION = NORMAL \/ S_sent_raw.COMPLETION = BUDGET',
        'S_sent = S_sent_raw[.COMPLETION = NORMAL]',
        '$unpack155_stage(S_sent,1)',
        'S_sent.TODO = (UNPACK_ARGS punpackcall_sent) :: ptask_tail*',
        'punpackcall_sent.FUNCTION = punpackcall.FUNCTION',
        'punpackcall_sent.CALLSITE = (porigin_site)',
        'punpackcall_sent.INDEX = 2', 'punpackcall_sent.ARGUMENTS = eps',
        'punpackcall_sent.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 1)),NAMED_HOLE,NAMED_SENT (KNOWN (PINT 3)),NAMED_SENT (KNOWN (PINT 4))]',
        'punpackcall_sent.SENT.NAMED = eps',
        '$call_task_valid(S_sent,S_sent.TODO[0])',
        '~$call_task_valid(S_sent,UNPACK_ARGS punpackcall_sent[.INDEX = 3])',
        'S_hole_raw = $unpack155_seek(S_sent,2,4096)',
        r'S_hole_raw.COMPLETION = NORMAL \/ S_hole_raw.COMPLETION = BUDGET',
        'S_hole = S_hole_raw[.COMPLETION = NORMAL]',
        'S_hole.TODO = [NAMED_PREFLIGHT porigin_ctor 1]',
        'S_hole.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_object porigin_ctor',
        'pcallcontext.CALLSITE = (porigin_site)', 'pcallcontext.ARGC = 4',
        'pcallcontext.HOLES = [1]', 'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
        '~$named_defined(S_hole,$ptascii("second"))',
        '$call_task_valid(S_hole,S_hole.TODO[0])',
        '~$call_task_valid(S_hole[.TODO = [TYPE_RECEIVE porigin_ctor 0]],TYPE_RECEIVE porigin_ctor 0)',
        'S_type_raw = $unpack155_seek(S_hole,3,4096)',
        r'S_type_raw.COMPLETION = NORMAL \/ S_type_raw.COMPLETION = BUDGET',
        'S_type = S_type_raw[.COMPLETION = NORMAL]',
        'S_type.TODO = [TYPE_RECEIVE porigin_ctor 0]',
        'S_type.CURRENT = (pcallcontext_type)',
        'pcallcontext_type.HOLES = [1]', 'pcallcontext_type.ARGC = 4',
        '$lookup(S_type.ENV,$ptascii("first")) = (n_first)', 'S_type.STORE[n_first] = DEFINED (PINT 1)',
        '$lookup(S_type.ENV,$ptascii("second")) = (n_second)', 'S_type.STORE[n_second] = DEFINED (PINT 20)',
        '$lookup(S_type.ENV,$ptascii("third")) = (n_third)', 'S_type.STORE[n_third] = DEFINED (PINT 3)',
        '$lookup(S_type.ENV,$ptascii("last")) = (n_last)', 'S_type.STORE[n_last] = DEFINED (PINT 4)',
        '$call_task_valid(S_type,S_type.TODO[0])',
        '$class_state_valid(S_type)', '$call_descriptors_valid(S_type)', '$heap_valid($heap_graph(S_type))',
        'S_end_raw = $unpack155_seek(S_type,4,8192)',
        r'S_end_raw.COMPLETION = NORMAL \/ S_end_raw.COMPLETION = BUDGET',
        'S_end = S_end_raw[.COMPLETION = NORMAL]',
        '$unpack155_stage(S_end,4)', '$unpack155_output(S_end.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_end)', '$call_descriptors_valid(S_end)', '$heap_valid($heap_graph(S_end))',
        'S_done = $drive_steps(S_end,8192)', 'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$unpack155_output(S_done.EVENTS) = ' + term(stdout),
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-constructor-unpack-eval-', dir=ROOT / '.tools'))
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
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace Ref155Author;')]
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

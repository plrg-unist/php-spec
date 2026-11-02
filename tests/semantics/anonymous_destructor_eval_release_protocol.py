#!/usr/bin/env python3
"""Real eval anonymous destructor selection, call entry and last-owner release."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_destructor_cases.json'
SOURCE_SHA = '38042dbf7ed505730a325d8a5b8ca5c67f858d853b9b790cc16207afd7c07500'
PREFIX = r'''
dec $anon_eval_output_item(pevent) : ptbytes
def $anon_eval_output_item(OUTPUT ptbytes) = ptbytes
def $anon_eval_output_item(pevent) = eps -- otherwise
dec $anon_eval_output(pevent*) : ptbytes
def $anon_eval_output(eps) = eps
def $anon_eval_output(pevent :: pevent_tail*) = $anon_eval_output_item(pevent) ++ $anon_eval_output(pevent_tail*)
dec $anon_eval_stage(pstate,nat) : bool
def $anon_eval_stage(S,0) = true
  -- if S.CURRENT = eps /\ S.EVALCONTEXTS = eps
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 14
def $anon_eval_stage(S,1) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.TARGET = METHOD_TARGET n (PORIGIN 1 pcpath)
def $anon_eval_stage(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = PORIGIN 1 pcpath
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 5
def $anon_eval_stage(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 15
def $anon_eval_stage(S,4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 17
def $anon_eval_stage(S,n) = false -- otherwise
dec $anon_eval_seek(pstate,nat,nat) : pstate
def $anon_eval_seek(S,n_mode,n) = S -- if $anon_eval_stage(S,n_mode)
def $anon_eval_seek(S,n_mode,0) = S -- if ~$anon_eval_stage(S,n_mode)
def $anon_eval_seek(S,n_mode,n) = $anon_eval_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_eval_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $anon_eval_seek(S,n_mode,n) = S -- otherwise
'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, code, response, stdout):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait.EVALCONTEXTS,1) = (pevalcontext)',
        'pevalcontext.BYTES = ' + term(code),
        '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')',
        'S_entered.COMPLETION = NORMAL',
        'S_live_raw = $anon_eval_seek(S_entered,0,4096)',
        r'S_live_raw.COMPLETION = NORMAL \/ S_live_raw.COMPLETION = BUDGET',
        'S_live = S_live_raw[.COMPLETION = NORMAL]',
        '$anon_eval_stage(S_live,0)', '$anon_eval_output(S_live.EVENTS) = eps',
        '$lookup(S_live.ENV,$ptascii("first156")) = (n_first_cell)',
        '$lookup(S_live.ENV,$ptascii("second156")) = (n_second_cell)',
        'S_live.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
        'S_live.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'n_first =/= n_second',
        'S_live.OBJECTS[n_first] = INSTANCE porigin_class',
        'S_live.OBJECTS[n_second] = INSTANCE porigin_class',
        'porigin_class = PORIGIN 1 pcpath_class',
        '$class_at(S_live.CLASSES,porigin_class) = (pclassdesc)',
        '$destructor_method(S_live,n_first) = (pmethoddesc)',
        '$destructor_method(S_live,n_second) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_class',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', '~pmethoddesc.STATIC',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = eps',
        'pmethoddesc.FUNCTION.SIGNATURE.RETURNS = eps',
        '~pmethoddesc.FUNCTION.SIGNATURE.BYREF',
        'porigin_destructor = pmethoddesc.FUNCTION.ORIGIN',
        '$destructor_uncalled_node(S_live,HOBJECT n_first)',
        '$destructor_uncalled_node(S_live,HOBJECT n_second)',
        'S_live.DESTRUCTION.CALLS = eps',
        '$objectprops_at(S_live.OBJECTPROPS,n_first) = (ppropertyslot_first*)',
        '$property_slot_at(ppropertyslot_first*,$ptascii("tag")) = (ppropertyslot_tag)',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 4))',
        '$class_state_valid(S_live)', '$call_descriptors_valid(S_live)',
        '$heap_valid($heap_graph(S_live))',
        'S_enter_raw = $anon_eval_seek(S_live,1,4096)',
        r'S_enter_raw.COMPLETION = NORMAL \/ S_enter_raw.COMPLETION = BUDGET',
        'S_enter = S_enter_raw[.COMPLETION = NORMAL]',
        'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*',
        'pdestructorcall.OBJECT = n_first',
        'pdestructorcall.TARGET = METHOD_TARGET n_first porigin_destructor',
        '~pdestructorcall.STORE', 'pdestructorcall.USER',
        'pdestructorcall.CALLER = eps', 'pdestructorcall.CONSTCONTEXT = eps',
        'pdestructorcall.PENDING = eps',
        'pdestructorcall.SITE = (PORIGIN 0 pcpath_site)',
        'pdestructorcall.LINE = 14',
        'pdestructorcall.RELEASE = (pdestructionrelease)',
        'pdestructionrelease.JOBS = pdestructionjob :: pdestructionjob_tail*',
        '$destruction_job_node(pdestructionjob) = (HOBJECT n_first)',
        'S_enter.DESTRUCTION.CALLS = [pdestructorcall]',
        'n_first <- S_enter.DESTRUCTION.CALLED',
        '~(n_second <- S_enter.DESTRUCTION.CALLED)',
        '(HOBJECT n_first) <- S_enter.ALLOCATIONS',
        '(HOBJECT n_second) <- S_enter.ALLOCATIONS',
        '~$named_defined(S_enter,$ptascii("first156"))',
        'S_enter.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$destructor_enter_valid(S_enter,pdestructorcall)',
        '$call_task_valid(S_enter,S_enter.TODO[0])',
        'pdestructorcall_bad_target = pdestructorcall[.TARGET = METHOD_TARGET n_second porigin_destructor]',
        'S_bad_target = S_enter[.DESTRUCTION.CALLS = [pdestructorcall_bad_target]][.TODO = (DESTRUCTOR_ENTER pdestructorcall_bad_target) :: ptask_tail*]',
        '~$destructor_enter_valid(S_bad_target,pdestructorcall_bad_target)',
        'pdestructorcall_bad_site = pdestructorcall[.SITE = (PORIGIN 1 pcpath_site)]',
        'S_bad_site = S_enter[.DESTRUCTION.CALLS = [pdestructorcall_bad_site]][.TODO = (DESTRUCTOR_ENTER pdestructorcall_bad_site) :: ptask_tail*]',
        '~$destructor_enter_valid(S_bad_site,pdestructorcall_bad_site)',
        'pdestructorcall_bad_line = pdestructorcall[.LINE = 15]',
        'S_bad_line = S_enter[.DESTRUCTION.CALLS = [pdestructorcall_bad_line]][.TODO = (DESTRUCTOR_ENTER pdestructorcall_bad_line) :: ptask_tail*]',
        '~$destructor_enter_valid(S_bad_line,pdestructorcall_bad_line)',
        '$class_state_valid(S_enter)', '$call_descriptors_valid(S_enter)',
        '$heap_valid($heap_graph(S_enter))',
        'S_body_raw = $anon_eval_seek(S_enter,2,4096)',
        r'S_body_raw.COMPLETION = NORMAL \/ S_body_raw.COMPLETION = BUDGET',
        'S_body = S_body_raw[.COMPLETION = NORMAL]',
        '$anon_eval_stage(S_body,2)', 'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_first porigin_destructor',
        'pcallcontext.FUNCTION = porigin_destructor',
        'pcallcontext.RECEIVER = (n_first)',
        'pcallcontext.LEXICAL_CLASS = (porigin_class)',
        'pcallcontext.CALLED_CLASS = (porigin_class)',
        'pcallcontext.CALLSITE = pdestructorcall.SITE',
        'pcallcontext.LINE = 14', 'pcallcontext.ARGC = 0',
        'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
        'pcallcontext.WRAPPER = eps',
        'S_body.DESTRUCTION.CALLS = [pdestructorcall]',
        '$anon_eval_output(S_body.EVENTS) = eps',
        '$call_descriptors_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        'S_after_raw = $anon_eval_seek(S_body,3,4096)',
        r'S_after_raw.COMPLETION = NORMAL \/ S_after_raw.COMPLETION = BUDGET',
        'S_after = S_after_raw[.COMPLETION = NORMAL]',
        '$anon_eval_stage(S_after,3)',
        '$anon_eval_output(S_after.EVENTS) = $ptascii("eval|4|")',
        '~((HOBJECT n_first) <- S_after.ALLOCATIONS)',
        '(HOBJECT n_second) <- S_after.ALLOCATIONS',
        'S_after.DESTRUCTION.CALLS = eps',
        'S_after.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_second_raw = $anon_eval_seek(S_after,1,4096)',
        r'S_second_raw.COMPLETION = NORMAL \/ S_second_raw.COMPLETION = BUDGET',
        'S_second = S_second_raw[.COMPLETION = NORMAL]',
        'S_second.TODO = (DESTRUCTOR_ENTER pdestructorcall_second) :: ptask_tail_second*',
        'pdestructorcall_second.OBJECT = n_second',
        'pdestructorcall_second.TARGET = METHOD_TARGET n_second porigin_destructor',
        'pdestructorcall_second.LINE = 16',
        '$destructor_enter_valid(S_second,pdestructorcall_second)',
        '$anon_eval_output(S_second.EVENTS) = $ptascii("eval|4|between|")',
        'S_end_raw = $anon_eval_seek(S_second,4,8192)',
        r'S_end_raw.COMPLETION = NORMAL \/ S_end_raw.COMPLETION = BUDGET',
        'S_end = S_end_raw[.COMPLETION = NORMAL]',
        '$anon_eval_stage(S_end,4)',
        '$anon_eval_output(S_end.EVENTS) = $ptascii("eval|4|between|eval|5|")',
        '~((HOBJECT n_first) <- S_end.ALLOCATIONS)',
        '~((HOBJECT n_second) <- S_end.ALLOCATIONS)',
        'S_end.DESTRUCTION.CALLS = eps',
        'S_end.DECLARATIONS = S_live.DECLARATIONS',
        '$class_state_valid(S_end)', '$call_descriptors_valid(S_end)',
        '$heap_valid($heap_graph(S_end))',
        'S_done = $drive_steps(S_end,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$anon_eval_output(S_done.EVENTS) = ' + term(stdout),
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
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-destructor-eval-release-', dir=ROOT / '.tools'))
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
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace Destruct156Author;')]
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
        report.update(passed=True, conditions=len(checks), derived_guards=3, derived_conditions=9, reached_conditions=len(checks)-9, fixture_sha256=sha(fixture))
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

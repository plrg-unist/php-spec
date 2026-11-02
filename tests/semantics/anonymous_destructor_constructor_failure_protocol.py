#!/usr/bin/env python3
"""Failed anonymous construction suppresses automatic, not explicit, destruction."""
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
SOURCE_SHA = '13ba454200e57a78285507eb62b29c9551dd9621d69988c88253eb84d52b417a'

PREFIX = r'''
dec $anon_failed_output_item(pevent) : ptbytes
def $anon_failed_output_item(OUTPUT ptbytes) = ptbytes
def $anon_failed_output_item(pevent) = eps -- otherwise
dec $anon_failed_output(pevent*) : ptbytes
def $anon_failed_output(eps) = eps
def $anon_failed_output(pevent :: pevent_tail*) = $anon_failed_output_item(pevent) ++ $anon_failed_output(pevent_tail*)
dec $anon_failed_manual_site(pstate,porigin) : bool
def $anon_failed_manual_site(S,porigin) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprMethodCall expression (NIdentifier (BYTES text) metadata_name) (SEQUENCE eps) metadata)
  -- if $base64(text) = $ptascii("__destruct")
  -- if $source_line(metadata) = 20
def $anon_failed_manual_site(S,porigin) = false -- otherwise
dec $anon_failed_stage(pstate,nat) : bool
def $anon_failed_stage(S,0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 19
def $anon_failed_stage(S,1) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin) eps 0 eps (porigin_site) z) :: ptask_tail*
  -- if $anon_failed_manual_site(S,porigin_site)
def $anon_failed_stage(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if $anon_failed_manual_site(S,porigin_site)
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 14
def $anon_failed_stage(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 22
def $anon_failed_stage(S,4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 23
def $anon_failed_stage(S,n) = false -- otherwise
dec $anon_failed_seek(pstate,nat,nat) : pstate
def $anon_failed_seek(S,n_mode,n) = S -- if $anon_failed_stage(S,n_mode)
def $anon_failed_seek(S,n_mode,0) = S -- if ~$anon_failed_stage(S,n_mode)
def $anon_failed_seek(S,n_mode,n) = $anon_failed_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_failed_stage(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $anon_failed_seek(S,n_mode,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_alive_raw = $anon_failed_seek(S_initial[.COMPLETION = NORMAL],0,4096)',
        r'S_alive_raw.COMPLETION = NORMAL \/ S_alive_raw.COMPLETION = BUDGET',
        'S_alive = S_alive_raw[.COMPLETION = NORMAL]',
        '$anon_failed_stage(S_alive,0)',
        '$anon_failed_output(S_alive.EVENTS) = $ptascii("ctor|caught|")',
        '$lookup(S_alive.ENV,$ptascii("destination156Review")) = (n_destination)',
        'S_alive.STORE[n_destination] = DEFINED (PINT 99)',
        '$lookup(S_alive.ENV,$ptascii("escaped156Review")) = (n_escaped)',
        'S_alive.STORE[n_escaped] = DEFINED (POBJECT n_object)',
        '(HOBJECT n_object) <- S_alive.ALLOCATIONS',
        'n_object <- S_alive.DESTRUCTION.CALLED',
        'S_alive.OBJECTS[n_object] = INSTANCE porigin_class',
        '$class_at(S_alive.CLASSES,porigin_class) = (pclassdesc)',
        '$destructor_method(S_alive,n_object) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_class',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '~pmethoddesc.STATIC', '~pmethoddesc.ABSTRACT',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = eps',
        'pmethoddesc.FUNCTION.SIGNATURE.RETURNS = eps',
        '~pmethoddesc.FUNCTION.SIGNATURE.BYREF',
        'porigin_destructor = pmethoddesc.FUNCTION.ORIGIN',
        '$effective_method(S_alive,porigin_class,$ptascii("__construct"),|S_alive.CLASSES|) = (pmethoddesc_ctor)',
        'porigin_ctor = pmethoddesc_ctor.FUNCTION.ORIGIN',
        'S_alive.DESTRUCTION.CALLS = eps',
        '~$destructor_uncalled_node(S_alive,HOBJECT n_object)',
        '$lookup(S_alive.ENV,$ptascii("given156Review")) = (n_given)',
        '$lookup(S_alive.ENV,$ptascii("error")) = (n_error)',
        'S_alive.STORE[n_given] = DEFINED (POBJECT n_exception)',
        'S_alive.STORE[n_error] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_alive,n_exception)',
        '$class_state_valid(S_alive)', '$call_descriptors_valid(S_alive)',
        '$heap_valid($heap_graph(S_alive))',
        'S_manual_raw = $anon_failed_seek(S_alive,1,4096)',
        r'S_manual_raw.COMPLETION = NORMAL \/ S_manual_raw.COMPLETION = BUDGET',
        'S_manual = S_manual_raw[.COMPLETION = NORMAL]',
        '$anon_failed_stage(S_manual,1)',
        'S_manual.CURRENT = eps',
        'S_manual.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_destructor) eps 0 eps (porigin_site) z_call) :: ptask_tail*',
        '$anon_failed_output(S_manual.EVENTS) = $ptascii("ctor|caught|99|7|manual-before|")',
        'n_object <- S_manual.DESTRUCTION.CALLED',
        '(HOBJECT n_object) <- S_manual.ALLOCATIONS',
        'S_manual.DESTRUCTION.CALLS = eps',
        '$target_function(S_manual,METHOD_TARGET n_object porigin_destructor) = (pmethoddesc.FUNCTION)',
        '$call_task_valid(S_manual,S_manual.TODO[0])',
        '~$call_task_valid(S_manual,CALL_ARGS (METHOD_TARGET n_object porigin_ctor) eps 0 eps (porigin_site) z_call)',
        '~$call_task_valid(S_manual,CALL_ARGS (METHOD_TARGET n_object porigin_destructor) eps 1 eps (porigin_site) z_call)',
        '~$call_task_valid(S_manual,CALL_ARGS (METHOD_TARGET n_object porigin_destructor) eps 0 eps (porigin_site) $(z_call + 1))',
        'S_body_raw = $anon_failed_seek(S_manual,2,4096)',
        r'S_body_raw.COMPLETION = NORMAL \/ S_body_raw.COMPLETION = BUDGET',
        'S_body = S_body_raw[.COMPLETION = NORMAL]',
        '$anon_failed_stage(S_body,2)',
        'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_object porigin_destructor',
        'pcallcontext.FUNCTION = porigin_destructor',
        'pcallcontext.RECEIVER = (n_object)',
        'pcallcontext.LEXICAL_CLASS = (porigin_class)',
        'pcallcontext.CALLED_CLASS = (porigin_class)',
        'pcallcontext.CALLSITE = (porigin_site)',
        'pcallcontext.ARGC = 0', 'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
        'pcallcontext.WRAPPER = eps',
        'n_object <- S_body.DESTRUCTION.CALLED',
        'S_body.DESTRUCTION.CALLS = eps',
        '(HOBJECT n_object) <- S_body.ALLOCATIONS',
        '$anon_failed_output(S_body.EVENTS) = $anon_failed_output(S_manual.EVENTS)',
        '$call_descriptors_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        'S_unset_raw = $anon_failed_seek(S_body,3,4096)',
        r'S_unset_raw.COMPLETION = NORMAL \/ S_unset_raw.COMPLETION = BUDGET',
        'S_unset = S_unset_raw[.COMPLETION = NORMAL]',
        '$anon_failed_stage(S_unset,3)',
        '$anon_failed_output(S_unset.EVENTS) = $ptascii("ctor|caught|99|7|manual-before|destruct|manual-after|")',
        'S_unset.STORE[n_escaped] = DEFINED (POBJECT n_object)',
        'n_object <- S_unset.DESTRUCTION.CALLED',
        '(HOBJECT n_object) <- S_unset.ALLOCATIONS',
        'S_unset.DESTRUCTION.CALLS = eps',
        '~$destructor_uncalled_node(S_unset,HOBJECT n_object)',
        'S_gone_raw = $anon_failed_seek(S_unset,4,4096)',
        r'S_gone_raw.COMPLETION = NORMAL \/ S_gone_raw.COMPLETION = BUDGET',
        'S_gone = S_gone_raw[.COMPLETION = NORMAL]',
        '$anon_failed_stage(S_gone,4)',
        '$anon_failed_output(S_gone.EVENTS) = $anon_failed_output(S_unset.EVENTS)',
        '~((HOBJECT n_object) <- S_gone.ALLOCATIONS)',
        'n_object <- S_gone.DESTRUCTION.CALLED',
        '~$named_defined(S_gone,$ptascii("escaped156Review"))',
        'S_gone.DESTRUCTION.CALLS = eps',
        '$class_state_valid(S_gone)', '$call_descriptors_valid(S_gone)',
        '$heap_valid($heap_graph(S_gone))',
        'S_done = $drive_steps(S_gone,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$anon_failed_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-destructor-constructor-failure-', dir=ROOT / '.tools'))
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
        report.update(passed=True, conditions=len(checks), reached_conditions=len(checks)-3,
                      derived_conditions=3, derived_guards=3, fixture_sha256=sha(fixture))
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

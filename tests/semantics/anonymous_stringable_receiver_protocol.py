#!/usr/bin/env python3
"""Anonymous Stringable naming and a saved receiver through rebinding."""
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
SOURCE_SHA = 'f4238f71d1c170323a5b37fc57a126749cc1d3da3700d0a72f7c19ef6a794945'

PREFIX = r'''
dec $anon_string_output_item(pevent) : ptbytes
def $anon_string_output_item(OUTPUT ptbytes) = ptbytes
def $anon_string_output_item(pevent) = eps -- otherwise
dec $anon_string_output(pevent*) : ptbytes
def $anon_string_output(eps) = eps
def $anon_string_output(pevent :: pevent_tail*) = $anon_string_output_item(pevent) ++ $anon_string_output(pevent_tail*)
dec $anon_string_site(pstate,porigin) : bool
def $anon_string_site(S,porigin) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprVariable (BYTES text) metadata)
  -- if $base64(text) = $ptascii("receiver157Review")
  -- if $source_line(metadata) = 21
def $anon_string_site(S,porigin) = false -- otherwise
dec $anon_string_stage(pstate,nat,nat) : bool
def $anon_string_stage(S,0,n) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_site) 21) :: (STRINGIFY_RESULT n_object porigin_site 21) :: ptask_tail*
  -- if $anon_string_site(S,porigin_site)
def $anon_string_stage(S,1,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if S.TODO = (STMT (NStmtReturn phpType5 metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 14
def $anon_string_stage(S,2,n) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin_site 21) :: (EMIT 21) :: ptask_tail*
def $anon_string_stage(S,3,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
  -- if pdestructorcall.OPERATION =/= eps
def $anon_string_stage(S,4,n) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (EMIT 21) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("old"))
  -- if S.DESTRUCTION.OPERATIONS = eps
def $anon_string_stage(S,n_stage,n) = false -- otherwise
dec $anon_string_seek(pstate,nat,nat,nat) : pstate
def $anon_string_seek(S,n_stage,n_object,n) = S -- if $anon_string_stage(S,n_stage,n_object)
def $anon_string_seek(S,n_stage,n_object,0) = S -- if ~$anon_string_stage(S,n_stage,n_object)
def $anon_string_seek(S,n_stage,n_object,n) = $anon_string_seek(S_next,n_stage,n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_string_stage(S,n_stage,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
def $anon_string_seek(S,n_stage,n_object,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage, receiver='0'):
    return [
        f'{state}_raw = $anon_string_seek({parent},{stage},{receiver},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$anon_string_stage({state},{stage},{receiver})',
    ]


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_initial.CLASSES = [pclassdesc_base,pclassdesc_named,pclassdesc_new,pclassdesc_old,pclassdesc_plain]',
        'pclassdesc_base.NAME = $ptascii("Base157Review")', 'pclassdesc_base.EARLY',
        'pclassdesc_named.NAME = $ptascii("Named157Review")',
        'pclassdesc_named.INTERFACES = [$ptascii("Stringable")]', '~pclassdesc_named.EARLY',
        'pclassdesc_new.PARENT = eps', 'pclassdesc_new.INTERFACES = [$ptascii("Stringable")]',
        '~pclassdesc_new.EARLY',
        'pclassdesc_new.NAME = $ptascii("class@anonymous") ++ [0] ++ ' + term(filename) + ' ++ $ptascii(":6$1")',
        'pclassdesc_old.PARENT = ($ptascii("Base157Review"))',
        'pclassdesc_old.INTERFACES = [$ptascii("Stringable")]', '~pclassdesc_old.EARLY',
        'pclassdesc_old.NAME = $ptascii("Base157Review@anonymous") ++ [0] ++ ' + term(filename) + ' ++ $ptascii(":9$2")',
        'pclassdesc_plain.PARENT = eps', 'pclassdesc_plain.INTERFACES = eps', 'pclassdesc_plain.EARLY',
        'pclassdesc_plain.NAME = $ptascii("class@anonymous") ++ [0] ++ ' + term(filename) + ' ++ $ptascii(":18$3")',
        '$source_unit(S_initial.SOURCES,0) = (pcunit)',
        '$anonymous_class_count(pcunit,' + term(filename) + ',S_initial.CLASSES,eps,0) = (4)',
        '$anonymous_rtd_count(S_initial,pcunit) = (4)',
        '$class_named(S_initial.CLASSNAMES,$ptlc(pclassdesc_named.NAME)) = eps',
        '$class_named(S_initial.CLASSNAMES,$ptlc(pclassdesc_new.NAME)) = eps',
        '$class_named(S_initial.CLASSNAMES,$ptlc(pclassdesc_old.NAME)) = eps',
        '$class_named(S_initial.CLASSNAMES,$ptlc(pclassdesc_plain.NAME)) = (pclassdesc_plain.ORIGIN)',
        '$reference_origin_parent(pclassdesc_new.ORIGIN,1) = ((porigin_new_site,[PCFIELD 0]))',
        '$reference_origin_parent(pclassdesc_old.ORIGIN,1) = ((porigin_old_site,[PCFIELD 0]))',
        '$anonymous_new_pending(S_initial,porigin_new_site) = (pclassdesc_new)',
        '$anonymous_new_pending(S_initial,porigin_old_site) = (pclassdesc_old)',
        '$class_state_valid(S_initial)',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_pending', 0),
        '$lookup(S_pending.ENV,$ptascii("receiver157Review")) = (n_receiver_cell)',
        'S_pending.STORE[n_receiver_cell] = DEFINED (POBJECT n_old)',
        '$lookup(S_pending.ENV,$ptascii("replacement157Review")) = (n_new_cell)',
        'S_pending.STORE[n_new_cell] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        'S_pending.OBJECTS[n_old] = INSTANCE pclassdesc_old.ORIGIN',
        'S_pending.OBJECTS[n_new] = INSTANCE pclassdesc_new.ORIGIN',
        '$effective_method(S_pending,pclassdesc_old.ORIGIN,$ptascii("__toString"),|S_pending.CLASSES|) = (pmethoddesc_old)',
        '$effective_method(S_pending,pclassdesc_new.ORIGIN,$ptascii("__toString"),|S_pending.CLASSES|) = (pmethoddesc_new)',
        'porigin_old_method = pmethoddesc_old.FUNCTION.ORIGIN',
        'porigin_new_method = pmethoddesc_new.FUNCTION.ORIGIN',
        'S_pending.TODO = (CALL_ARGS (METHOD_TARGET n_old porigin_old_method) eps 0 eps (porigin_site) 21) :: (STRINGIFY_RESULT n_old porigin_site 21) :: (EMIT 21) :: ptask_tail*',
        '$stringify_pending(S_pending,METHOD_TARGET n_old porigin_old_method,porigin_site)',
        '$stringify_method_selected(S_pending,n_old,porigin_old_method,porigin_site)',
        '$task_nodes(STRINGIFY_RESULT n_old porigin_site 21) = [HOBJECT n_old]',
        '$class_named(S_pending.CLASSNAMES,$ptlc(pclassdesc_named.NAME)) = (pclassdesc_named.ORIGIN)',
        '$class_named(S_pending.CLASSNAMES,$ptlc(pclassdesc_new.NAME)) = (pclassdesc_new.ORIGIN)',
        '$class_named(S_pending.CLASSNAMES,$ptlc(pclassdesc_old.NAME)) = (pclassdesc_old.ORIGIN)',
        '$anonymous_new_available(S_pending,pclassdesc_new)',
        '$anonymous_new_available(S_pending,pclassdesc_old)',
        'ptbytes_before = pclassdesc_old.NAME ++ $ptascii("|") ++ pclassdesc_plain.NAME ++ $ptascii("|stringable|(")',
        '$anon_string_output(S_pending.EVENTS) = ptbytes_before',
        '$class_state_valid(S_pending)', '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        '~$call_task_valid(S_pending,CALL_ARGS (METHOD_TARGET n_old porigin_old_method) eps 0 eps (porigin_site) 22)',
        '~$call_task_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n_new porigin_new_method) eps 0 eps (porigin_site) 21) :: (STRINGIFY_RESULT n_old porigin_site 21) :: (EMIT 21) :: ptask_tail*],CALL_ARGS (METHOD_TARGET n_new porigin_new_method) eps 0 eps (porigin_site) 21)',
        '$anonymous_class_count(pcunit,' + term(filename) + ',[pclassdesc_base,pclassdesc_named,pclassdesc_new,pclassdesc_old[.INTERFACES = eps],pclassdesc_plain],eps,0) = eps',
        *seek('S_pending', 'S_body', 1, 'n_old'),
        'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_old porigin_old_method',
        'pcallcontext.RECEIVER = (n_old)',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_old.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_old.ORIGIN)',
        'pcallcontext.CALLSITE = (porigin_site)',
        '$stringify_context(S_body,pcallcontext)',
        'S_body.STORE[n_receiver_cell] = DEFINED (POBJECT n_new)',
        '(HOBJECT n_old) <- S_body.ALLOCATIONS',
        '$anon_string_output(S_body.EVENTS) = ptbytes_before ++ $ptascii("old-call|")',
        '$call_descriptors_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        *seek('S_body', 'S_returned', 2, 'n_old'),
        'S_returned.TODO = (STRINGIFY_RESULT n_old porigin_site 21) :: (EMIT 21) :: ptask_tail*',
        'S_returned.RESULT = KNOWN pvalue_old', '$string_bytes(pvalue_old) = ($ptascii("old"))',
        '$stringify_result_valid(S_returned,n_old,porigin_site,21)',
        'S_returned.STORE[n_receiver_cell] = DEFINED (POBJECT n_new)',
        '$heap_owners($heap_graph(S_returned),HOBJECT n_old) = 1',
        '(HOBJECT n_old) <- S_returned.ALLOCATIONS',
        '~(n_old <- S_returned.DESTRUCTION.CALLED)',
        *seek('S_returned', 'S_destructor', 3, 'n_old'),
        'S_destructor.CURRENT = (pcallcontext_destructor)',
        '$destructor_context_call(pcallcontext_destructor,S_destructor.CURRENT,S_destructor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_old', 'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = STRINGIFY_RESULT n_old porigin_site 21',
        'pdestructionoperation.PENDING = eps',
        '$destructor_operation_live(S_destructor,pdestructionoperation)',
        'S_destructor.STORE[n_receiver_cell] = DEFINED (POBJECT n_new)',
        '$anon_string_output(S_destructor.EVENTS) = ptbytes_before ++ $ptascii("old-call|")',
        '$call_descriptors_valid(S_destructor)', '$heap_valid($heap_graph(S_destructor))',
        *seek('S_destructor', 'S_emit', 4, 'n_old'),
        'S_emit.TODO = (EMIT 21) :: ptask_tail*',
        'S_emit.RESULT = KNOWN pvalue_old',
        '~((HOBJECT n_old) <- S_emit.ALLOCATIONS)', 'n_old <- S_emit.DESTRUCTION.CALLED',
        '$anon_string_output(S_emit.EVENTS) = ptbytes_before ++ $ptascii("old-call|old-dtor|")',
        '$call_descriptors_valid(S_emit)', '$heap_valid($heap_graph(S_emit))',
        *seek('S_emit', 'S_second', 0),
        'S_second.TODO = (CALL_ARGS (METHOD_TARGET n_new porigin_new_method) eps 0 eps (porigin_second_site) 21) :: (STRINGIFY_RESULT n_new porigin_second_site 21) :: (EMIT 21) :: ptask_second_tail*',
        'porigin_site =/= porigin_second_site',
        '$stringify_pending(S_second,METHOD_TARGET n_new porigin_new_method,porigin_second_site)',
        '$anon_string_output(S_second.EVENTS) = ptbytes_before ++ $ptascii("old-call|old-dtor|old)|")',
        'S_second.STORE[n_receiver_cell] = DEFINED (POBJECT n_new)',
        '~((HOBJECT n_old) <- S_second.ALLOCATIONS)',
        *seek('S_second', 'S_second_return', 2, 'n_new'),
        '$stringify_result_valid(S_second_return,n_new,porigin_second_site,21)',
        'S_second_return.RESULT = KNOWN pvalue_new', '$string_bytes(pvalue_new) = ($ptascii("new"))',
        '(HOBJECT n_new) <- S_second_return.ALLOCATIONS',
        '$call_descriptors_valid(S_second_return)', '$heap_valid($heap_graph(S_second_return))',
        'S_done = $drive_steps(S_second_return,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$anon_string_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-stringable-receiver-', dir=ROOT / '.tools'))
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

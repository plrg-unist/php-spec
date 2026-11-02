#!/usr/bin/env python3
"""An escaped failed clone retains normal automatic-destructor eligibility."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_clone_cases.json'
SOURCE_SHA = '599a01117f0fbbd25e4481264bdd988970127113c2f5367c0cd7856f71910b6a'
PREFIX = r'''
dec $acf_output_item(pevent) : ptbytes
def $acf_output_item(OUTPUT ptbytes) = ptbytes
def $acf_output_item(pevent) = eps -- otherwise
dec $acf_output(pevent*) : ptbytes
def $acf_output(eps) = eps
def $acf_output(pevent :: pevent_tail*) = $acf_output_item(pevent) ++ $acf_output(pevent_tail*)
dec $acf_site(pstate,porigin,int) : bool
def $acf_site(S,porigin,z) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprClone expression metadata)
  -- if $source_line(metadata) = z
def $acf_site(S,porigin,z) = false -- otherwise
dec $acf_stage(pstate,nat) : bool
def $acf_stage(S,0) = true
  -- if S.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
  -- if $acf_site(S,pcloneoperation.SITE,16)
def $acf_stage(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (STMT (NStmtExpression expression metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 11
def $acf_stage(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 20
def $acf_stage(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin) eps 0 eps (porigin_site) z) :: ptask_tail*
  -- if $origin_node(S.SOURCES,porigin_site) = (NExprMethodCall expression (NIdentifier (BYTES text) metadata_name) (SEQUENCE eps) metadata)
  -- if $source_line(metadata) = 23
  -- if $base64(text) = $ptascii("__destruct")
def $acf_stage(S,4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 24
def $acf_stage(S,5) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 26
def $acf_stage(S,6) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = 28
def $acf_stage(S,n) = false -- otherwise
dec $acf_seek(pstate,nat,nat) : pstate
def $acf_seek(S,n_stage,n) = S -- if $acf_stage(S,n_stage)
def $acf_seek(S,n_stage,0) = S -- if ~$acf_stage(S,n_stage)
def $acf_seek(S,n_stage,n) = $acf_seek(S_next,n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$acf_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $acf_seek(S,n_stage,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $acf_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$acf_stage({state},{stage})',
    ]


def assertions(fixture, filename, stdout):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        *seek('S_initial[.COMPLETION = NORMAL]', 'S_enter', 0),
        'S_enter.CURRENT = eps',
        'S_enter.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*',
        'n_source = pcloneoperation.SOURCE', 'n_clone = pcloneoperation.TARGET',
        'n_source =/= n_clone', 'pcloneoperation.CALL = eps',
        '(HOBJECT n_source) <- S_enter.ALLOCATIONS', '(HOBJECT n_clone) <- S_enter.ALLOCATIONS',
        '$lookup(S_enter.ENV,$ptascii("source160Review")) = (n_source_cell)',
        'S_enter.STORE[n_source_cell] = DEFINED (POBJECT n_source)',
        'S_enter.OBJECTS[n_source] = INSTANCE porigin_class',
        'S_enter.OBJECTS[n_clone] = INSTANCE porigin_class',
        '$clone_method(S_enter,n_clone) = (pmethoddesc_clone)',
        'porigin_clone = pmethoddesc_clone.FUNCTION.ORIGIN',
        'pmethoddesc_clone.OWNER = porigin_class',
        'pmethoddesc_clone.VISIBILITY = PROPERTY_PUBLIC', '~pmethoddesc_clone.STATIC',
        'pmethoddesc_clone.FUNCTION.SIGNATURE.PARAMETERS = eps',
        '~pmethoddesc_clone.FUNCTION.SIGNATURE.BYREF',
        '$destructor_method(S_enter,n_clone) = (pmethoddesc_destructor)',
        'porigin_destructor = pmethoddesc_destructor.FUNCTION.ORIGIN',
        '$lookup(S_enter.ENV,$ptascii("escaped160Review")) = (n_escaped)',
        '$lookup(S_enter.ENV,$ptascii("given160Review")) = (n_given)',
        'S_enter.STORE[n_given] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_enter,n_exception)',
        '$clone_callback_live(S_enter,pcloneoperation)',
        '$call_task_valid(S_enter,S_enter.TODO[0])',
        '~$clone_operation_body_valid(S_enter,pcloneoperation[.TARGET = n_source])',
        '~$clone_operation_source_valid(S_enter,pcloneoperation[.LINE = $(pcloneoperation.LINE + 1)])',
        '$class_state_valid(S_enter)', '$call_descriptors_valid(S_enter)', '$heap_valid($heap_graph(S_enter))',
        *seek('S_enter', 'S_throw', 1),
        'S_throw.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_clone porigin_clone',
        'pcallcontext.FUNCTION = porigin_clone', 'pcallcontext.RECEIVER = (n_clone)',
        'pcallcontext.LEXICAL_CLASS = (porigin_class)', 'pcallcontext.CALLED_CLASS = (porigin_class)',
        'pcallcontext.CALLSITE = (pcloneoperation.SITE)',
        'S_throw.STORE[n_escaped] = DEFINED (POBJECT n_clone)',
        'S_throw.STORE[n_given] = DEFINED (POBJECT n_exception)',
        '~(n_clone <- S_throw.DESTRUCTION.CALLED)',
        '$acf_output(S_throw.EVENTS) = $ptascii("clone|")',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        *seek('S_throw', 'S_caught', 2),
        '$lookup(S_caught.ENV,$ptascii("caught160Review")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_exception)',
        '$lookup(S_caught.ENV,$ptascii("destination160Review")) = (n_destination)',
        'S_caught.STORE[n_destination] = DEFINED (PINT 99)',
        'S_caught.STORE[n_escaped] = DEFINED (POBJECT n_clone)',
        'S_caught.STORE[n_source_cell] = DEFINED (POBJECT n_source)',
        '(HOBJECT n_clone) <- S_caught.ALLOCATIONS', '(HOBJECT n_source) <- S_caught.ALLOCATIONS',
        '~(n_clone <- S_caught.DESTRUCTION.CALLED)', '~(n_source <- S_caught.DESTRUCTION.CALLED)',
        'S_caught.CLONES = eps',
        '$acf_output(S_caught.EVENTS) = $ptascii("clone|same|")',
        '$call_descriptors_valid(S_caught)', '$heap_valid($heap_graph(S_caught))',
        *seek('S_caught', 'S_manual', 3),
        'S_manual.TODO = (CALL_ARGS (METHOD_TARGET n_clone porigin_destructor) eps 0 eps (porigin_manual) z_manual) :: ptask_manual*',
        '~(n_clone <- S_manual.DESTRUCTION.CALLED)', 'S_manual.DESTRUCTION.CALLS = eps',
        '$call_task_valid(S_manual,S_manual.TODO[0])',
        '~$call_task_valid(S_manual,CALL_ARGS (METHOD_TARGET n_clone porigin_clone) eps 0 eps (porigin_manual) z_manual)',
        '$acf_output(S_manual.EVENTS) = $ptascii("clone|same|99|fresh|7|manual-before|")',
        *seek('S_manual', 'S_explicit', 4),
        '(HOBJECT n_clone) <- S_explicit.ALLOCATIONS',
        '~(n_clone <- S_explicit.DESTRUCTION.CALLED)',
        'S_explicit.DESTRUCTION.CALLS = eps',
        '$acf_output(S_explicit.EVENTS) = $ptascii("clone|same|99|fresh|7|manual-before|drop7|")',
        '$call_descriptors_valid(S_explicit)', '$heap_valid($heap_graph(S_explicit))',
        *seek('S_explicit', 'S_copy_gone', 5),
        '~((HOBJECT n_clone) <- S_copy_gone.ALLOCATIONS)', 'n_clone <- S_copy_gone.DESTRUCTION.CALLED',
        '(HOBJECT n_source) <- S_copy_gone.ALLOCATIONS',
        '~(n_source <- S_copy_gone.DESTRUCTION.CALLED)',
        '~$named_defined(S_copy_gone,$ptascii("escaped160Review"))',
        '$acf_output(S_copy_gone.EVENTS) = $ptascii("clone|same|99|fresh|7|manual-before|drop7|manual-after|drop7|")',
        '$call_descriptors_valid(S_copy_gone)', '$heap_valid($heap_graph(S_copy_gone))',
        *seek('S_copy_gone', 'S_source_gone', 6),
        '~((HOBJECT n_source) <- S_source_gone.ALLOCATIONS)', 'n_source <- S_source_gone.DESTRUCTION.CALLED',
        '$acf_output(S_source_gone.EVENTS) = $ptascii("clone|same|99|fresh|7|manual-before|drop7|manual-after|drop7|source-before|drop7|")',
        'S_done = $drive_steps(S_source_gone,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$acf_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-clone-failure-', dir=ROOT / '.tools'))
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

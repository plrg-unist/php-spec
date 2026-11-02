#!/usr/bin/env python3
"""Eval-published anonymous static captures retain their selected diagnostic views."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_captured_method_cases.json'
SOURCE_SHA = 'eb62c89012fc22a12be1d4c9b7b182ddd065a1864f6880e55406543bd348b077'

PREFIX = r'''
dec $ac162_eval_output_item(pevent) : ptbytes
def $ac162_eval_output_item(OUTPUT ptbytes) = ptbytes
def $ac162_eval_output_item(pevent) = eps -- otherwise
dec $ac162_eval_output(pevent*) : ptbytes
def $ac162_eval_output(eps) = eps
def $ac162_eval_output(pevent :: pevent_tail*) = $ac162_eval_output_item(pevent) ++ $ac162_eval_output(pevent_tail*)
dec $ac162_eval_body(pstate,ptbytes,int) : bool
def $ac162_eval_body(S,ptbytes_name,z) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if pmethoddesc.NAME = ptbytes_name
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if $source_line(metadata) = z
def $ac162_eval_body(S,ptbytes_name,z) = false -- otherwise
dec $ac162_eval_stage(pstate,nat) : bool
def $ac162_eval_stage(S,0) = $ac162_eval_body(S,$ptascii("WrongReturn162Author"),5)
def $ac162_eval_stage(S,1) = $ac162_eval_body(S,$ptascii("MissingReturn162Author"),9)
def $ac162_eval_stage(S,2) = $ac162_eval_body(S,$ptascii("NeverReturn162Author"),12)
def $ac162_eval_stage(S,n) = false -- otherwise
dec $ac162_eval_seek(pstate,nat,nat) : pstate
def $ac162_eval_seek(S,n_stage,n) = S -- if $ac162_eval_stage(S,n_stage)
def $ac162_eval_seek(S,n_stage,0) = S -- if ~$ac162_eval_stage(S,n_stage)
def $ac162_eval_seek(S,n_stage,n) = $ac162_eval_seek(S_next,n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ac162_eval_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $ac162_eval_seek(S,n_stage,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def seek(parent, state, stage):
    return [
        f'{state}_raw = $ac162_eval_seek({parent},{stage},8192)',
        fr'{state}_raw.COMPLETION = NORMAL \/ {state}_raw.COMPLETION = BUDGET',
        f'{state} = {state}_raw[.COMPLETION = NORMAL]',
        f'$ac162_eval_stage({state},{stage})',
    ]


def assertions(fixture, filename, code, response, stdout):
    wrong_prefix = stdout.split(b'missing-body|', 1)[0]
    never_prefix = stdout.split(b'never-body|', 1)[0]
    assert wrong_prefix.startswith(b'wrong-body|') and never_prefix.startswith(wrong_prefix)
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
        'S_entered.CLASSES = [pclassdesc]',
        'pclassdesc.ORIGIN = PORIGIN 1 pcpath_class',
        'pclassdesc.EARLY', 'pclassdesc.PARENT = eps',
        '$class_named(S_entered.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        'S_entered.FUNCTIONS = [pfunction_make]',
        'pfunction_make.ORIGIN = PORIGIN 1 pcpath_make',
        'pfunction_make.NAME = ' + term(b'Captured162Author\\make162Author'),
        'pclassdesc.METHODS = [pmethoddesc_wrong,pmethoddesc_missing,pmethoddesc_never]',
        '$class_method_origin(S_entered.CLASSES,pmethoddesc_wrong.FUNCTION.ORIGIN) = (pmethoddesc_wrong)',
        '$class_method_origin(S_entered.CLASSES,pmethoddesc_missing.FUNCTION.ORIGIN) = (pmethoddesc_missing)',
        '$class_method_origin(S_entered.CLASSES,pmethoddesc_never.FUNCTION.ORIGIN) = (pmethoddesc_never)',
        'pmethoddesc_wrong.FUNCTION.ORIGIN = PORIGIN 1 pcpath_wrong',
        'pmethoddesc_missing.FUNCTION.ORIGIN = PORIGIN 1 pcpath_missing',
        'pmethoddesc_never.FUNCTION.ORIGIN = PORIGIN 1 pcpath_never',
        'pmethoddesc_wrong.NAME = $ptascii("WrongReturn162Author")',
        'pmethoddesc_missing.NAME = $ptascii("MissingReturn162Author")',
        'pmethoddesc_never.NAME = $ptascii("NeverReturn162Author")',
        'pmethoddesc_wrong.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc_missing.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc_never.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc_wrong.STATIC', 'pmethoddesc_missing.STATIC', 'pmethoddesc_never.STATIC',
        'pmethoddesc_wrong.VISIBILITY = PROPERTY_PUBLIC',
        'pmethoddesc_missing.VISIBILITY = PROPERTY_PUBLIC',
        'pmethoddesc_never.VISIBILITY = PROPERTY_PUBLIC',
        'pmethoddesc_wrong.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'pmethoddesc_missing.FUNCTION.SIGNATURE.RETURNS = pmethoddesc_wrong.FUNCTION.SIGNATURE.RETURNS',
        'pmethoddesc_never.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "never"]))]',
        '$class_state_valid(S_entered)', '$call_descriptors_valid(S_entered)',
    ]
    for state, stage, label, desc, prefix in [
        ('S_wrong', 0, 'wrong', 'pmethoddesc_wrong', b''),
        ('S_missing', 1, 'missing', 'pmethoddesc_missing', wrong_prefix),
        ('S_never', 2, 'never', 'pmethoddesc_never', never_prefix),
    ]:
        parent = 'S_entered' if stage == 0 else ('S_wrong' if stage == 1 else 'S_missing')
        checks += [
            *seek(parent, state, stage),
            f'{state}.CURRENT = (pcallcontext_{label})',
            f'pcallcontext_{label}.TARGET = CLOSURE_TARGET n_{label}',
            f'pcallcontext_{label}.INSTANCE = (n_{label})',
            f'pcallcontext_{label}.FUNCTION = {desc}.FUNCTION.ORIGIN',
            f'pcallcontext_{label}.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
            f'pcallcontext_{label}.CALLED_CLASS = (pclassdesc.ORIGIN)',
            f'pcallcontext_{label}.RECEIVER = eps',
            f'$object_body({state}.OBJECTS[n_{label}]) = METHODCLOSURE {desc}.FUNCTION.ORIGIN porigin_site_{label} pclassdesc.ORIGIN eps',
            f'(HOBJECT n_{label}) <- {state}.ALLOCATIONS',
            f'$closure_scope_at({state}.CLOSURESCOPES,n_{label}) = (pclosurescope_{label})',
            f'pclosurescope_{label}.LEXICAL = pclassdesc.ORIGIN',
            f'pclosurescope_{label}.CALLED = pclassdesc.ORIGIN',
            f'pclosurescope_{label}.RECEIVER = eps',
            f'$target_function({state},CLOSURE_TARGET n_{label}) = ({desc}.FUNCTION)',
            f'$method_closure_functions({state},n_{label},{desc}) = ({desc}.FUNCTION,{desc}.FUNCTION)',
            f'$captured_method_diagnostic({state}) = ({desc})',
            f'{desc}.FUNCTION.NAME = pclassdesc.NAME ++ $ptascii("::") ++ {desc}.NAME',
            f'$return_function_name({state},{desc}.FUNCTION) = $c_string(pclassdesc.NAME) ++ $ptascii("::") ++ {desc}.NAME',
            f'$call_function_name({state},{desc}.FUNCTION) = {desc}.FUNCTION.NAME',
            f'$c_string($call_function_name({state},{desc}.FUNCTION)) = $ptascii("class@anonymous")',
            f'$call_function_kind({state}) = $ptascii("method")',
            f'$ac162_eval_output({state}.EVENTS) = ' + term(prefix),
            f'$call_current_valid({state})', f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
        ]
    checks += [
        '$return_function_name(S_wrong,pmethoddesc_wrong.FUNCTION[.NAME = $ptascii("forged")]) = $call_function_name(S_wrong,pmethoddesc_wrong.FUNCTION[.NAME = $ptascii("forged")])',
        'S_done = $drive_steps(S_never,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.CURRENT = eps', 'S_done.EVALCONTEXTS = eps',
        '$ac162_eval_output(S_done.EVENTS) = ' + term(stdout),
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-captured-method-eval-', dir=ROOT / '.tools'))
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
        code, = [base64.b64decode(n['fields'][0]['bytes']) for n in nodes(parsed['ast'])
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace Captured162Author;')]
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
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), reached_conditions=len(checks)-1,
                      derived_conditions=1, derived_guards=1, fixture_sha256=sha(fixture))
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

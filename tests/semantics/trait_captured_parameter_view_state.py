#!/usr/bin/env python3
"""A captured trait method receives its saved self type before a direct call."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/trait_captured_method_kind_cases.json'
SOURCE_SHA = '218a6733dd64eef881f2f54ba79336f8a4196d92fb0050ca0df8d51f236746b3'
PREFIX = r'''
dec $tc163a_output_item(pevent) : ptbytes
def $tc163a_output_item(OUTPUT ptbytes) = ptbytes
def $tc163a_output_item(pevent) = eps -- otherwise
dec $tc163a_output(pevent*) : ptbytes
def $tc163a_output(eps) = eps
def $tc163a_output(pevent :: pevent_tail*) = $tc163a_output_item(pevent) ++ $tc163a_output(pevent_tail*)
dec $tc163a_stage(pstate) : bool
def $tc163a_stage(S) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if pcallcontext.ARGC = 1
  -- if $receiving_function(S,porigin) = (pfunction_view)
  -- if $closure_scope_at(S.CLOSURESCOPES,n) = (pclosurescope)
  -- if $class_at(S.CLASSES,pclosurescope.LEXICAL) = (pclassdesc)
  -- if pclassdesc.NAME = $ptascii("Trait163AuthorA")
def $tc163a_stage(S) = false -- otherwise
dec $tc163a_seek(pstate,nat) : pstate
def $tc163a_seek(S,n) = S -- if $tc163a_stage(S)
def $tc163a_seek(S,0) = S -- if ~$tc163a_stage(S)
def $tc163a_seek(S,n) = $tc163a_seek(S_next,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$tc163a_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $tc163a_seek(S,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def checks(fixture, filename, stdout):
    prefix = stdout.split(b'captured-type:', 1)[0]
    assert prefix.startswith(b'missing:') and prefix.endswith(b'captured:')
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        'S_raw = $tc163a_seek(S_initial[.COMPLETION = NORMAL],8192)',
        r'S_raw.COMPLETION = NORMAL \/ S_raw.COMPLETION = BUDGET',
        'S = S_raw[.COMPLETION = NORMAL]', '$tc163a_stage(S)',
        'S.CURRENT = (pcallcontext)',
        'S.TODO = [TYPE_RECEIVE porigin 0]',
        '$typed_receive_valid(S,porigin,0)',
        'pcallcontext.FUNCTION = porigin',
        'pcallcontext.TARGET = CLOSURE_TARGET n',
        'pcallcontext.INSTANCE = (n)', 'pcallcontext.ARGC = 1',
        '$object_body(S.OBJECTS[n]) = METHODCLOSURE porigin_method porigin_site porigin_owner eps',
        '$closure_method_origin(S,porigin_method) = (pmethoddesc)',
        'pmethoddesc.NAME = $ptascii("take")',
        'pmethoddesc.OWNER = porigin_owner',
        '$class_at(S.CLASSES,porigin_owner) = (pclassdesc_owner)',
        'pclassdesc_owner.NAME = $ptascii("Owner163AuthorA")',
        '$closure_scope_at(S.CLOSURESCOPES,n) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_trait',
        'pclosurescope.CALLED = porigin_owner',
        'pclosurescope.RECEIVER = eps',
        '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
        'pclassdesc_trait.NAME = $ptascii("Trait163AuthorA")',
        'pclassdesc_trait.KIND = "trait"',
        'pcallcontext.LEXICAL_CLASS = (porigin_trait)',
        'pcallcontext.CALLED_CLASS = (porigin_owner)',
        'pcallcontext.RECEIVER = eps',
        '$trait_fcc_scope_owner(S,pmethoddesc,porigin_site,porigin_owner,pclosurescope) = (porigin_owner)',
        '$trait_fcc_target_name(S,CLOSURE_TARGET n) = ($ptascii("Trait163AuthorA::take"))',
        '$method_closure_functions(S,n,pmethoddesc) = (pfunction_base,pfunction_view)',
        'pfunction_base = pmethoddesc.FUNCTION',
        'pfunction_view =/= pfunction_base',
        '$trait_fcc_parameter_function(S,n,pmethoddesc) = (pfunction_view)',
        '$target_function(S,CLOSURE_TARGET n) = (pfunction_view)',
        '$receiving_function(S,porigin) = (pfunction_view)',
        'pfunction_base.SIGNATURE.PARAMETERS = [psparam_base]',
        'pfunction_view.SIGNATURE.PARAMETERS = [psparam_view]',
        'psparam_base.NAME = $ptascii("value")',
        'psparam_view.NAME = psparam_base.NAME',
        'psparam_base.TYPE = [(PTBRANCH ([PTCLASS pclassdesc_owner.NAME]))]',
        'psparam_view.TYPE = [(PTBRANCH ([PTCLASS pclassdesc_trait.NAME]))]',
        '$lookup(S.ENV,psparam_view.NAME) = (n_value)',
        'S.STORE[n_value] = DEFINED (POBJECT n_argument)',
        'S.OBJECTS[n_argument] = INSTANCE porigin_owner',
        '$call_function_name(S,pfunction_base) = $ptascii("Trait163AuthorA::take")',
        '$missing_argument_function_name(S,pfunction_view) = $ptascii("Trait163AuthorA::take")',
        '$call_function_kind(S) = $ptascii("method")',
        '$tc163a_output(S.EVENTS) = ' + term(prefix),
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$call_function_kind(S[.CURRENT = (pcallcontext[.INSTANCE = eps])]) = $ptascii("function")',
        '$call_function_kind(S[.CURRENT = (pcallcontext[.CALLED_CLASS = eps])]) = $ptascii("function")',
        'S_done = $drive_steps(S,8192)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps', 'S_done.CURRENT = eps',
        '$tc163a_output(S_done.EVENTS) = ' + term(stdout),
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='trait-captured-parameter-view-', dir=ROOT / '.tools'))
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
        conditions = checks(checked['fixture'], os.fsencode(source), stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + condition + '\n' for condition in conditions))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(conditions), reached_conditions=len(conditions)-2,
                      derived_conditions=2, derived_guards=2, fixture_sha256=sha(fixture))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and before == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Genuine old-clone and later trait FCC never-call states for CLASS163."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

CATALOGUE = ROOT / 'tests/semantics/trait_captured_method_kind_cases.json'
SOURCE_SHA = 'd58cd8d7dad9a86819240bd219c68b9a2638feed352ae16d9e12095980d1ba54'
PREFIX = r'''
dec $tc163_stage(pstate,ptbytes) : bool
def $tc163_stage(S,ptbytes_called) = true
  -- if S.TODO = (TYPE_FALLTHROUGH porigin) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $closure_scope_at(S.CLOSURESCOPES,n) = (pclosurescope)
  -- if $class_at(S.CLASSES,pclosurescope.CALLED) = (pclassdesc)
  -- if pclassdesc.NAME = ptbytes_called
def $tc163_stage(S,ptbytes_called) = false -- otherwise
dec $tc163_seek(pstate,ptbytes,nat) : pstate
def $tc163_seek(S,ptbytes_called,n) = S -- if $tc163_stage(S,ptbytes_called)
def $tc163_seek(S,ptbytes_called,0) = S -- if ~$tc163_stage(S,ptbytes_called)
def $tc163_seek(S,ptbytes_called,n) = $tc163_seek(S_next,ptbytes_called,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$tc163_stage(S,ptbytes_called)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $tc163_seek(S,ptbytes_called,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seek(parent, name, label):
    called = '$ptascii("' + name + '")'
    return [
        f'S_{label}_raw = $tc163_seek({parent},{called},16384)',
        fr'S_{label}_raw.COMPLETION = NORMAL \/ S_{label}_raw.COMPLETION = BUDGET',
        f'S_{label} = S_{label}_raw[.COMPLETION = NORMAL]',
        f'$tc163_stage(S_{label},{called})',
    ]


def checks(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
        *seek('S_initial[.COMPLETION = NORMAL]', 'First163Review', 'old'),
        'S_old.CURRENT = (pcallcontext_old)',
        'pcallcontext_old.TARGET = CLOSURE_TARGET n_old',
        'pcallcontext_old.INSTANCE = (n_old)',
        'S_old.TODO = (TYPE_FALLTHROUGH porigin_fallthrough_old) :: ptask_old*',
        'porigin_fallthrough_old = pcallcontext_old.FUNCTION',
        '$object_body(S_old.OBJECTS[n_old]) = METHODCLOSURE porigin_method_old porigin_site_old porigin_first eps',
        '$closure_method_origin(S_old,porigin_method_old) = (pmethoddesc_old)',
        'pmethoddesc_old.OWNER = porigin_first',
        '$closure_scope_at(S_old.CLOSURESCOPES,n_old) = (pclosurescope_old)',
        'pclosurescope_old.LEXICAL = porigin_layer',
        'pclosurescope_old.CALLED = porigin_first',
        '$class_at(S_old.CLASSES,porigin_layer) = (pclassdesc_layer)',
        '$class_at(S_old.CLASSES,porigin_first) = (pclassdesc_first)',
        'pclassdesc_layer.NAME = $ptascii("Layer163Review")',
        'pclassdesc_first.NAME = $ptascii("First163Review")',
        'pcallcontext_old.LEXICAL_CLASS = (porigin_layer)',
        'pcallcontext_old.CALLED_CLASS = (porigin_first)',
        '$constant_callable_first(S_old.CONSTANTCLOSURES,porigin_site_old) = (pconstantclosure_first)',
        '$(pconstantclosure_first.OBJECT < n_old)',
        '$trait_real_birth_at(S_old.CLASSCONSTANTHISTORY,pconstantclosure_first.OBJECT) = ((porigin_site_old,ptraitcachecause))',
        '$trait_fcc_birth_owner(S_old,pconstantclosure_first) = (porigin_first)',
        '$trait_fcc_scope_receipt(S_old,pconstantclosure_first,pmethoddesc_old,pclosurescope_old) = (porigin_first)',
        '$trait_fcc_clone_scope(S_old,S_old.CONSTANTCLOSURES,pmethoddesc_old,pclosurescope_old) = (porigin_first)',
        '$trait_fcc_scope_owner(S_old,pmethoddesc_old,porigin_site_old,porigin_first,pclosurescope_old) = (porigin_first)',
        '$method_closure_functions(S_old,n_old,pmethoddesc_old) = (pfunction_base,pfunction_view)',
        'pfunction_base = pmethoddesc_old.FUNCTION',
        'pfunction_view =/= pfunction_base',
        '$trait_fcc_parameter_function(S_old,n_old,pmethoddesc_old) = (pfunction_view)',
        'pcallcontext_old.FUNCTION = pfunction_base.ORIGIN',
        '$trait_fcc_target_name(S_old,CLOSURE_TARGET n_old) = ($ptascii("Layer163Review::stop"))',
        '$captured_method_diagnostic(S_old) = eps',
        '$call_function_kind(S_old) = $ptascii("method")',
        '$call_current_valid(S_old)', '$call_descriptors_valid(S_old)',
        'porigin_physical = $origin_source(pfunction_base.ORIGIN)',
        'porigin_physical =/= pfunction_base.ORIGIN',
        '$call_function_kind(S_old[.CURRENT = (pcallcontext_old[.FUNCTION = porigin_physical])]) = $ptascii("function")',
        '$call_function_kind(S_old[.CURRENT = (pcallcontext_old[.LEXICAL_CLASS = (porigin_first)])]) = $ptascii("function")',
        *seek('S_old', 'Later163Review', 'later'),
        'S_later.CURRENT = (pcallcontext_later)',
        'pcallcontext_later.TARGET = CLOSURE_TARGET n_later',
        'pcallcontext_later.INSTANCE = (n_later)',
        'S_later.TODO = (TYPE_FALLTHROUGH porigin_fallthrough_later) :: ptask_later*',
        'porigin_fallthrough_later = pcallcontext_later.FUNCTION',
        '$object_body(S_later.OBJECTS[n_later]) = METHODCLOSURE porigin_method_later porigin_site_later porigin_later eps',
        '$closure_method_origin(S_later,porigin_method_later) = (pmethoddesc_later)',
        '$closure_scope_at(S_later.CLOSURESCOPES,n_later) = (pclosurescope_later)',
        'pclosurescope_later.LEXICAL = porigin_first',
        'pclosurescope_later.CALLED = porigin_later',
        '$class_at(S_later.CLASSES,porigin_later) = (pclassdesc_later)',
        'pclassdesc_later.NAME = $ptascii("Later163Review")',
        'pcallcontext_later.LEXICAL_CLASS = (porigin_first)',
        'pcallcontext_later.CALLED_CLASS = (porigin_later)',
        '$trait_fcc_scope_owner(S_later,pmethoddesc_later,porigin_site_later,porigin_later,pclosurescope_later) = (porigin_later)',
        '$trait_fcc_target_name(S_later,CLOSURE_TARGET n_later) = ($ptascii("First163Review::stop"))',
        '$call_function_kind(S_later) = $ptascii("method")',
        '$call_current_valid(S_later)', '$call_descriptors_valid(S_later)',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='trait-captured-method-kind-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
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
        conditions = checks(checked['fixture'], os.fsencode(source))
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + condition + '\n' for condition in conditions))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(conditions), reached_conditions=len(conditions)-2,
                      derived_guards=2, fixture_sha256=sha(fixture))
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

#!/usr/bin/env python3
"""Reach copied trait parent type checks from the retained source originals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/trait_captured_parent_view_cases.json'
SELECTED = ('trait-alt-before-parent-capture', 'trait-parent-before-alt-fatal',
            'cross-parent-lexical-capture')
PREFIX = r'''
dec $tc164_stage(pstate,ptbytes,ptbytes) : bool
def $tc164_stage(S,ptbytes_lexical,ptbytes_called) = true
  -- if S.TODO = [TYPE_RECEIVE porigin 0]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $closure_scope_at(S.CLOSURESCOPES,n) = (pclosurescope)
  -- if $class_at(S.CLASSES,pclosurescope.LEXICAL) = (pclassdesc_lexical)
  -- if $class_at(S.CLASSES,pclosurescope.CALLED) = (pclassdesc_called)
  -- if pclassdesc_lexical.NAME = ptbytes_lexical
  -- if pclassdesc_called.NAME = ptbytes_called
def $tc164_stage(S,ptbytes_lexical,ptbytes_called) = false -- otherwise
dec $tc164_seek(pstate,ptbytes,ptbytes,nat) : pstate
def $tc164_seek(S,ptbytes_lexical,ptbytes_called,n) = S
  -- if $tc164_stage(S,ptbytes_lexical,ptbytes_called)
def $tc164_seek(S,ptbytes_lexical,ptbytes_called,0) = S
  -- if ~$tc164_stage(S,ptbytes_lexical,ptbytes_called)
def $tc164_seek(S,ptbytes_lexical,ptbytes_called,n) = $tc164_seek(S_next,ptbytes_lexical,ptbytes_called,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$tc164_stage(S,ptbytes_lexical,ptbytes_called)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $tc164_seek(S,ptbytes_lexical,ptbytes_called,n) = S -- otherwise
dec $tc164_output_item(pevent) : ptbytes
def $tc164_output_item(OUTPUT ptbytes) = ptbytes
def $tc164_output_item(pevent) = eps -- otherwise
dec $tc164_output(pevent*) : ptbytes
def $tc164_output(eps) = eps
def $tc164_output(pevent :: pevent_tail*) = $tc164_output_item(pevent) ++ $tc164_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def name(text):
    return '$ptascii(' + json.dumps(text) + ')'


def stage(label, previous, lexical, called, expected_type, argument, output):
    s = 'S_' + label
    first = previous == 'S_initial'
    start = previous + '[.COMPLETION = NORMAL]'
    if not first:
        start = 'S_' + label + '_advance[.COMPLETION = NORMAL]'
    checks = ([] if first else [f'S_{label}_advance = $drive_steps({previous},1)'])
    checks += [
        f'{s}_raw = $tc164_seek({start},{name(lexical)},{name(called)},16384)',
        fr'{s}_raw.COMPLETION = NORMAL \/ {s}_raw.COMPLETION = BUDGET',
        f'{s} = {s}_raw[.COMPLETION = NORMAL]',
        f'$tc164_stage({s},{name(lexical)},{name(called)})',
        f'{s}.TODO = [TYPE_RECEIVE porigin_{label} 0]',
        f'{s}.CURRENT = (pcallcontext_{label})',
        f'pcallcontext_{label}.TARGET = CLOSURE_TARGET n_{label}',
        f'pcallcontext_{label}.INSTANCE = (n_{label})',
        f'pcallcontext_{label}.ARGC = 1',
        f'$object_body({s}.OBJECTS[n_{label}]) = METHODCLOSURE porigin_method_{label} porigin_site_{label} porigin_owner_{label} eps',
        f'$closure_method_origin({s},porigin_method_{label}) = (pmethoddesc_{label})',
        f'$closure_scope_at({s}.CLOSURESCOPES,n_{label}) = (pclosurescope_{label})',
        f'$class_at({s}.CLASSES,pclosurescope_{label}.LEXICAL) = (pclassdesc_lexical_{label})',
        f'$class_at({s}.CLASSES,pclosurescope_{label}.CALLED) = (pclassdesc_called_{label})',
        f'pclassdesc_lexical_{label}.NAME = {name(lexical)}',
        f'pclassdesc_called_{label}.NAME = {name(called)}',
        f'pcallcontext_{label}.LEXICAL_CLASS = (pclosurescope_{label}.LEXICAL)',
        f'pcallcontext_{label}.CALLED_CLASS = (pclosurescope_{label}.CALLED)',
        f'$trait_fcc_scope_owner({s},pmethoddesc_{label},porigin_site_{label},porigin_owner_{label},pclosurescope_{label}) = (porigin_owner_{label})',
        f'$method_closure_functions({s},n_{label},pmethoddesc_{label}) = (pfunction_base_{label},pfunction_view_{label})',
        f'$trait_fcc_parameter_function({s},n_{label},pmethoddesc_{label}) = (pfunction_view_{label})',
        f'$receiving_function({s},porigin_{label}) = (pfunction_view_{label})',
        f'pfunction_base_{label}.SIGNATURE.PARAMETERS = [psparam_base_{label}]',
        f'pfunction_view_{label}.SIGNATURE.PARAMETERS = [psparam_{label}]',
        f'psparam_{label}.TYPE = {expected_type}',
        f'$lookup({s}.ENV,psparam_{label}.NAME) = (n_value_{label})',
        f'{s}.STORE[n_value_{label}] = DEFINED (POBJECT n_argument_{label})',
        f'{s}.OBJECTS[n_argument_{label}] = INSTANCE porigin_argument_{label}',
        f'$class_at({s}.CLASSES,porigin_argument_{label}) = (pclassdesc_argument_{label})',
        f'pclassdesc_argument_{label}.NAME = {name(argument)}',
        f'$typed_receive_valid({s},porigin_{label},0)',
        f'$call_current_valid({s})',
        f'$call_descriptors_valid({s})',
        f'$tc164_output({s}.EVENTS) = {encoded(output)}',
    ]
    if label == 'old':
        checks += [
            f'{s}.OBJECTS[n_old] = METHODCLOSURE porigin_method_old porigin_site_old porigin_owner_old eps',
            'pfunction_base_old =/= pfunction_view_old',
        ]
    return checks


def type_branches(*atoms):
    return '[' + ', '.join('(PTBRANCH ([' + atom + ']))' for atom in atoms) + ']'


def class_atom(text):
    return 'PTCLASS ' + name(text)


def checks(row, fixture, filename):
    case = row['id']
    stdout = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    common = [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', '~S_initial.COMPILESTOP',
    ]
    if case == 'trait-alt-before-parent-capture':
        common += stage('old', 'S_initial', 'Layer164ReviewA', 'First164ReviewA',
                        type_branches(class_atom('Alt164ReviewA'), 'PTPARENT'),
                        'Alt164ReviewA', b'old:')
        common += [
            'psparam_base_old.TYPE = ' + type_branches(class_atom('Alt164ReviewA'), class_atom('Base164ReviewA')),
            '$trait_fcc_parameter_branches(S_old,psparam_old.TYPE,POBJECT n_argument_old) = (true)',
            '~$trait_fcc_parameter_parent_fatal(S_old,psparam_old.TYPE,POBJECT n_argument_old)',
        ]
        common += stage('later', 'S_old', 'First164ReviewA', 'Later164ReviewA',
                        type_branches(class_atom('Alt164ReviewA'), class_atom('Base164ReviewA')),
                        'Base164ReviewA', stdout.split(b'later:', 1)[0] + b'later:')
        common += [
            '$trait_fcc_parameter_branches(S_later,psparam_later.TYPE,POBJECT n_argument_later) = (true)',
            '~$trait_fcc_parameter_parent_fatal(S_later,psparam_later.TYPE,POBJECT n_argument_later)',
        ]
    elif case == 'trait-parent-before-alt-fatal':
        common += stage('later', 'S_initial', 'First164ReviewB', 'Later164ReviewB',
                        type_branches(class_atom('Base164ReviewB'), class_atom('Alt164ReviewB')),
                        'Alt164ReviewB', b'later:')
        common += [
            '$trait_fcc_parameter_branches(S_later,psparam_later.TYPE,POBJECT n_argument_later) = (true)',
            '~$trait_fcc_parameter_parent_fatal(S_later,psparam_later.TYPE,POBJECT n_argument_later)',
        ]
        common += stage('old', 'S_later', 'Layer164ReviewB', 'First164ReviewB',
                        type_branches('PTPARENT', class_atom('Alt164ReviewB')),
                        'Alt164ReviewB', stdout)
        common += [
            'psparam_base_old.TYPE = ' + type_branches(class_atom('Base164ReviewB'), class_atom('Alt164ReviewB')),
            '$trait_fcc_parameter_branches(S_old,psparam_old.TYPE,POBJECT n_argument_old) = eps',
            '$trait_fcc_parameter_parent_fatal(S_old,psparam_old.TYPE,POBJECT n_argument_old)',
            '$typed_parameter_conversion_at(S_old,psparam_old.TYPE,POBJECT n_argument_old,$typed_caller_strict(S_old)) = TYPEDEPENDENT "parameter parent scope has no parent"',
            'S_fatal = $typed_parameter_value(S_old,pfunction_view_old,0,POBJECT n_argument_old)',
            'S_fatal.COMPLETION = FATAL ($ptascii("Cannot access \\"parent\\" when current class scope has no parent")) z_fatal',
            'S_fatal.EVENTS = S_old.EVENTS',
            'S_actual = $drive_steps(S_old,1)',
            'S_actual.COMPLETION = REQUESTFATAL ($ptascii("Error")) ($ptascii("Cannot access \\"parent\\" when current class scope has no parent")) z_fatal',
            '$tc164_output(S_actual.EVENTS) = $tc164_output(S_old.EVENTS)',
        ]
    elif case == 'cross-parent-lexical-capture':
        common += stage('first', 'S_initial', 'FirstCross164', 'LaterCross164',
                        type_branches(class_atom('BaseA164')), 'BaseA164', b'later-a:')
        common += [
            'pclassdesc_lexical_first.PARENT = (' + name('BaseA164') + ')',
            'pclassdesc_called_first.PARENT = (' + name('BaseB164') + ')',
            '$trait_fcc_parameter_branches(S_first,psparam_first.TYPE,POBJECT n_argument_first) = (true)',
            '~$trait_fcc_parameter_parent_fatal(S_first,psparam_first.TYPE,POBJECT n_argument_first)',
            '$lookup($global_table_view(S_first).ENV,' + name('old') + ') = (n_old_cell)',
            'S_first.STORE[n_old_cell] = DEFINED (POBJECT n_old)',
            'S_first.OBJECTS[n_old] = METHODCLOSURE porigin_old_method porigin_old_site porigin_old_owner eps',
            '$closure_method_origin(S_first,porigin_old_method) = (pmethoddesc_old)',
            '$closure_scope_at(S_first.CLOSURESCOPES,n_old) = (pclosurescope_old)',
            '$class_at(S_first.CLASSES,pclosurescope_old.LEXICAL) = (pclassdesc_old_lexical)',
            'pclassdesc_old_lexical.NAME = ' + name('LayerCross164'),
            'pclosurescope_old.CALLED = pclosurescope_first.LEXICAL',
            '$trait_fcc_parameter_function(S_first,n_old,pmethoddesc_old) = (pfunction_old_view)',
            'pfunction_old_view =/= pmethoddesc_old.FUNCTION',
            'pmethoddesc_old.FUNCTION.SIGNATURE.PARAMETERS = [psparam_old_base]',
            'psparam_old_base.TYPE = ' + type_branches(class_atom('BaseA164')),
            'pfunction_old_view.SIGNATURE.PARAMETERS = [psparam_old]',
            'psparam_old.TYPE = ' + type_branches('PTPARENT'),
        ]
        prefix = stdout.split(b'later-b-error:', 1)[0]
        common += stage('second', 'S_first', 'FirstCross164', 'LaterCross164',
                        type_branches(class_atom('BaseA164')), 'BaseB164', prefix)
        common += [
            '$trait_fcc_parameter_branches(S_second,psparam_second.TYPE,POBJECT n_argument_second) = (false)',
            '~$trait_fcc_parameter_parent_fatal(S_second,psparam_second.TYPE,POBJECT n_argument_second)',
            '$typed_parameter_conversion(S_second,psparam_second,POBJECT n_argument_second) = TYPEREJECT',
        ]
    else:
        raise AssertionError(case)
    return common


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    data = json.loads(CATALOGUE.read_text())
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    reports = []
    for case in SELECTED:
        row, = [r for r in data['cases'] if r['id'] == case]
        raw = Path(tempfile.mkdtemp(prefix='trait-captured-parent-view-', dir=ROOT / '.tools'))
        source = raw / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256']
        watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, source,
                   Path(__file__), ROOT / '_build/default/adapter/main.exe',
                   ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
        before = {str(path): sha(path) for path in watched}
        report = {'passed': False, 'case': case, 'source_sha256': row['source_sha256'],
                  'inputs_before': before, 'raw': str(raw)}
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
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            fixture = raw / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + condition + '\n' for condition in conditions))
            result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                           '--sl', *map(str, modules), str(fixture)],
                                          raw / 'numeric', 1200, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report.update(passed=True, conditions=len(conditions), fixture_sha256=sha(fixture))
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
            reports.append(report)
        assert report['passed']
    assert len(reports) == len(SELECTED)


if __name__ == '__main__':
    main()

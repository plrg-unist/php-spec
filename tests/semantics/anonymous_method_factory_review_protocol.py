#!/usr/bin/env python3
"""Independent named-method factories: lexical receivers, imports and lazy linking."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_method_factory_cases.json'
PREFIX = r'''
dec $class178_review_output(pevent) : ptbytes
def $class178_review_output(OUTPUT ptbytes) = ptbytes
def $class178_review_output(pevent) = eps -- otherwise
dec $class178_review_outputs(pevent*) : ptbytes
def $class178_review_outputs(eps) = eps
def $class178_review_outputs(pevent :: pevent_tail*) = $class178_review_output(pevent) ++ $class178_review_outputs(pevent_tail*)
dec $class178_review_front(pstate,nat) : bool
def $class178_review_front(S,0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) = (pclassdesc)
  -- if $class_named(S.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)
def $class178_review_front(S,1) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail*
def $class178_review_front(S,2) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_pending(S,porigin) =/= eps
def $class178_review_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
def $class178_review_front(S,n) = false -- otherwise
dec $class178_review_seek(pstate,nat,nat) : pstate
def $class178_review_seek(S,n_front,0) = S
def $class178_review_seek(S,n_front,n) = S
  -- if $(n > 0)
  -- if $class178_review_front(S,n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class178_review_seek(S,n_front,n) = $class178_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class178_review_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $class178_review_named(pclassdesc*,ptbytes) : pclassdesc?
def $class178_review_named(eps,ptbytes) = eps
def $class178_review_named(pclassdesc :: pclassdesc_tail*,ptbytes) = (pclassdesc) -- if pclassdesc.NAME = ptbytes
def $class178_review_named(pclassdesc :: pclassdesc_tail*,ptbytes) = $class178_review_named(pclassdesc_tail*,ptbytes) -- if pclassdesc.NAME =/= ptbytes
dec $class178_review_replace(pclassdesc*,pclassdesc) : pclassdesc*
def $class178_review_replace(eps,pclassdesc) = eps
def $class178_review_replace(pclassdesc :: pclassdesc_tail*,pclassdesc_new) = pclassdesc_new :: pclassdesc_tail* -- if pclassdesc.ORIGIN = pclassdesc_new.ORIGIN
def $class178_review_replace(pclassdesc :: pclassdesc_tail*,pclassdesc_new) = pclassdesc :: $class178_review_replace(pclassdesc_tail*,pclassdesc_new) -- if pclassdesc.ORIGIN =/= pclassdesc_new.ORIGIN
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def initial(fixture, filename, state='S_initial'):
    return [state + ' = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            state + '.COMPLETION = BUDGET /\\ ~' + state + '.COMPILESTOP']


def seek(parent, state, front):
    return [state + '_found = $class178_review_seek(' + parent + ',' + str(front) + ',3000)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$class178_review_front(' + state + ',' + str(front) + ')']


def final(row, state, filename):
    stdout = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [state + '.COMPLETION = NORMAL /\\ ' + state + '.TODO = eps /\\ ' + state + '.CURRENT = eps /\\ ' + state + '.FRAMES = eps',
            '$class178_review_outputs(' + state + '.EVENTS) = ' + term(stdout),
            '$class_state_valid(' + state + ') /\\ $property_state_valid(' + state + ')',
            '$declaration_history_valid(' + state + ')']


def inherited(row, fixture, filename):
    checks = initial(fixture, filename) + [
        *seek('S_initial', 'S_first', 0),
        'S_first.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_first,porigin_new) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(b'Probe178InstanceFactory@anonymous\0' + filename + b':6$0'),
        '$class_named(S_first.CLASSNAMES,$ptascii("probe178instancefactory")) = (porigin_owner)',
        '$class_at(S_first.CLASSES,porigin_owner) = (pclassdesc_owner)',
        '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc_make)',
        'pmethoddesc_make.OWNER = porigin_owner /\\ ~pmethoddesc_make.STATIC',
        '$effective_method(S_first,pclassdesc.ORIGIN,$ptascii("make"),|S_first.CLASSES|) = (pmethoddesc_make)',
        '$class_link_at(S_first.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_owner)',
    ]
    for index, (state, value) in enumerate([('S_first', 3), ('S_second', 8), ('S_third', 1)]):
        if index:
            prior = ['S_first', 'S_second'][index - 1]
            checks += [state + '_start = $drive_steps(' + prior + ',1)', *seek(state + '_start', state, 0)]
        context = 'pcallcontext_' + str(index)
        cell = 'n_value' + str(index)
        receiver = 'n_factory' if index < 2 else 'n_child'
        called = 'porigin_owner' if index < 2 else 'pclassdesc.ORIGIN'
        checks += [
            state + '.ORIGIN = (porigin_new)',
            '$anonymous_new_descriptor(' + state + ',porigin_new) = (pclassdesc)',
            state + '.CURRENT = (' + context + ')',
            context + '.FUNCTION = pmethoddesc_make.FUNCTION.ORIGIN',
            context + '.TARGET = METHOD_TARGET ' + receiver + ' pmethoddesc_make.FUNCTION.ORIGIN',
            context + '.LEXICAL_CLASS = (porigin_owner) /\\ ' + context + '.CALLED_CLASS = (' + called + ')',
            '$method_current_scope(' + state + ') = (porigin_owner)',
            '$lookup(' + state + '.ENV,$ptascii("value")) = (' + cell + ')',
            state + '.STORE[' + cell + '] = DEFINED (PINT ' + str(value) + ')',
            '$call_current_valid(' + state + ')',
        ]
    return checks + [
        'S_first.OBJECTS[n_factory] = INSTANCE porigin_owner',
        'S_third.OBJECTS[n_child] = INSTANCE pclassdesc.ORIGIN /\\ n_child =/= n_factory',
        '$class178_review_outputs(S_third.EVENTS) = $ptascii("Probe178InstanceFactory;Probe178InstanceFactory;Probe178InstanceFactory;")',
        '~$call_current_valid(S_third[.CURRENT = (pcallcontext_2[.LEXICAL_CLASS = (pclassdesc.ORIGIN)])])',
        '~$call_current_valid(S_third[.CURRENT = (pcallcontext_2[.CALLED_CLASS = (porigin_owner)])])',
        'S_done = $drive_steps(S_third,5000)',
        *final(row, 'S_done', filename),
    ]


def namespaces(row, fixture, filename):
    return initial(fixture, filename) + [
        *seek('S_initial', 'S_pre', 0),
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(b'Probe178App\\Factory@anonymous\0' + filename + b':10$0'),
        'pclassdesc.PARENT = (' + term(b'Probe178App\\Factory') + ')',
        '$class_named(S_pre.CLASSNAMES,' + term(b'probe178app\\factory') + ') = (porigin_owner)',
        '$class_named(S_pre.CLASSNAMES,' + term(b'probe178library\\ancestor') + ') = (porigin_ancestor)',
        '$class_at(S_pre.CLASSES,porigin_owner) = (pclassdesc_owner)',
        '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc_make)',
        'pmethoddesc_make.STATIC /\\ pmethoddesc_make.OWNER = porigin_owner',
        'pmethoddesc_make.FUNCTION.ENV.NAMESPACE = $ptascii("Probe178App")',
        '$pllookup(pmethoddesc_make.FUNCTION.ENV.CLASSES,$ptascii("ancestoralias")) = (' + term(b'Probe178Library\\Ancestor') + ')',
        '$pllookup(pmethoddesc_make.FUNCTION.ENV.CLASSES,$ptascii("owneralias")) = (' + term(b'Probe178App\\Factory') + ')',
        '$class_link_at(S_pre.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_ancestor)',
        '$class_link_at(S_pre.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_owner)',
        'S_pre.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = STATIC_METHOD_TARGET porigin_owner pmethoddesc_make.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (porigin_owner) /\\ pcallcontext.CALLED_CLASS = (porigin_owner)',
        '$call_current_valid(S_pre) /\\ S_pre.EVENTS = eps',
        'S_bad_import = S_pre[.CLASSES = $class178_review_replace(S_pre.CLASSES,pclassdesc_owner[.METHODS = [pmethoddesc_make[.FUNCTION = pmethoddesc_make.FUNCTION[.ENV = pmethoddesc_make.FUNCTION.ENV[.CLASSES = eps]]]]])]',
        '~$declaration_history_valid(S_bad_import)',
        'S_done = $drive_steps(S_pre,5000)',
        *final(row, 'S_done', filename),
    ]


def reference(row, fixture, filename):
    return initial(fixture, filename) + [
        *seek('S_initial', 'S_pre', 1),
        'S_pre.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*',
        'S_pre.CURRENT = (pcallcontext)',
        'pcallcontext.FUNCTION = porigin_ctor',
        'pcallcontext.RECEIVER = (n_object)',
        'S_pre.OBJECTS[n_object] = INSTANCE porigin_class',
        '$class_at(S_pre.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(b'Probe178ReferenceFactory@anonymous\0' + filename + b':4$0'),
        '$receiving_function(S_pre,porigin_ctor) = (pfunction)',
        '$promotion_task_valid(S_pre,porigin_ctor,0)',
        '$promotion_descriptor(S_pre,pfunction,0) = (ppropertydesc)',
        '$promotion_raw(S_pre,pfunction,0) = (psraw)',
        'psraw.BYREF /\\ ~ppropertydesc.READONLY /\\ ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '$lookup(S_pre.ENV,$ptascii("value")) = (n_value)',
        '$lookup($global_table_view(S_pre).ENV,$ptascii("value")) = (n_value)',
        'S_pre.STORE[n_value] = DEFINED (PINT 4)',
        '$location_slot(S_pre,PROPERTY n_object ppropertydesc.KEY) = UNDEFINED',
        '~$propref_source_present(S_pre.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)',
        'S_written = $drive_steps(S_pre,1)',
        'S_written.COMPLETION = BUDGET /\\ S_written.EVENTS = eps',
        '$objectprops_at(S_written.OBJECTPROPS,n_object) = (ppropertyslot_written_slots*)',
        '$property_slot_at(ppropertyslot_written_slots*,ppropertydesc.KEY) = (ppropertyslot_written)',
        'ppropertyslot_written.STATE = PROP_VALUE (ALIAS n_value)',
        '$propref_source_present(S_written.PROPREFS,n_value,OBJECT_PROP_SOURCE n_object ppropertydesc.KEY ppropertydesc.ORIGIN)',
        '$proprefs_valid(S_written)',
        '$propref_at(S_written.PROPREFS,n_value) = (ppropref)',
        'S_wrong_decl = S_written[.PROPREFS = [ppropref[.SOURCES = [OBJECT_PROP_SOURCE n_object ppropertydesc.KEY pclassdesc.ORIGIN]]]]',
        '~$proprefs_valid(S_wrong_decl)',
        'S_done = $drive_steps(S_written[.COMPLETION = NORMAL],5000)',
        *final(row, 'S_done', filename),
        'S_done.STORE[n_value] = DEFINED (PINT 8)',
        '$objectprops_at(S_done.OBJECTPROPS,n_object) = (ppropertyslot_done_slots*)',
        '$property_slot_at(ppropertyslot_done_slots*,ppropertydesc.KEY) = (ppropertyslot_done)',
        'ppropertyslot_done.STATE = PROP_VALUE (ALIAS n_value)',
    ]


def lazy(rows, fixtures, filenames):
    called, skipped = rows
    called_fixture, skipped_fixture = fixtures
    called_file, skipped_file = filenames
    message = base64.b64decode(called['stderr_template_base64']).split(b'Fatal error: ', 1)[1].split(b' in {FILE} on line ', 1)[0]
    return initial(called_fixture, called_file) + [
        *seek('S_initial', 'S_pending', 2),
        'S_pending.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_pending,porigin_new) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(b'Probe178FinalParent@anonymous\0' + called_file + b':7$0'),
        '~pclassdesc.EARLY',
        '$class178_review_outputs(S_pending.EVENTS) = $ptascii("before;enter;")',
        'S_pending.OBJECTS = eps',
        'S_pending.CURRENT = (pcallcontext)',
        '$class_named(S_pending.CLASSNAMES,$ptascii("probe178conflictfactory")) = (porigin_owner)',
        'pcallcontext.LEXICAL_CLASS = (porigin_owner) /\\ pcallcontext.CALLED_CLASS = (porigin_owner)',
        '$call_current_valid(S_pending)',
        '$class_named(S_pending.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pending.DECLARATIONS,pclassdesc.ORIGIN)',
        'S_fail = $drive_steps(S_pending,1)',
        'S_fail.COMPLETION = STATICBYTES ' + term(message) + ' 9',
        'S_fail.EVENTS = S_pending.EVENTS /\\ S_fail.OBJECTS = eps',
        '$class_named(S_fail.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_fail.DECLARATIONS,pclassdesc.ORIGIN)',
        *initial(skipped_fixture, skipped_file, 'S_skipped_initial'),
        'S_skipped = $drive_steps(S_skipped_initial[.COMPLETION = NORMAL],5000)',
        *final(skipped, 'S_skipped', skipped_file),
        '$class178_review_named(S_skipped.CLASSES,' + term(b'Probe178SkippedParent@anonymous\0' + skipped_file + b':6$0') + ') = (pclassdesc_skipped)',
        '~pclassdesc_skipped.EARLY',
        '$class_named(S_skipped.CLASSNAMES,$ptlc(pclassdesc_skipped.NAME)) = eps',
        '$class_link_at(S_skipped.LINKEDPARENTS,pclassdesc_skipped.ORIGIN) = eps',
        '~$anonymous_runtime_declaration(S_skipped.DECLARATIONS,pclassdesc_skipped.ORIGIN)',
    ]


def denial_compile(rows, fixtures, filenames):
    denied, compile_error = rows
    denied_fixture, compile_fixture = fixtures
    denied_file, compile_file = filenames
    message = base64.b64decode(compile_error['stderr_template_base64']).split(b'Fatal error: ', 1)[1].split(b' in {FILE} on line ', 1)[0]
    return initial(denied_fixture, denied_file) + [
        *seek('S_initial', 'S_pre', 0),
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc)',
        '$class_named(S_pre.CLASSNAMES,$ptascii("probe178unrelatedfactory")) = (porigin_owner)',
        'S_pre.CURRENT = (pcallcontext)',
        'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
        '$method_current_scope(S_pre) = (porigin_owner)',
        '$method_named(pclassdesc.METHODS,$ptascii("__construct")) = (pmethoddesc_ctor)',
        'pmethoddesc_ctor.VISIBILITY = PROPERTY_PROTECTED',
        '~$method_accessible(S_pre,pmethoddesc_ctor,(porigin_owner))',
        '$call_current_valid(S_pre)',
        '$class178_review_outputs(S_pre.EVENTS) = $ptascii("before;")',
        *seek('S_pre', 'S_throw', 3),
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "Error"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("Call to protected Probe178ScopeParent@anonymous::__construct() from scope Probe178UnrelatedFactory"))',
        'S_throw.EVENTS = S_pre.EVENTS',
        'S_done = $drive_steps(S_throw,5000)',
        *final(denied, 'S_done', denied_file),
        'S_compile = $php_run(' + compile_fixture + ',0,' + json.dumps(base64.b64encode(compile_file).decode()) + ')',
        'S_compile.COMPLETION = STATICBYTES ' + term(message) + ' 6',
        'S_compile.EVENTS = eps /\\ S_compile.OBJECTS = eps /\\ S_compile.CLASSNAMES = eps',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    rows = {r['id']: r for r in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['method-factory-instance-inherited-lexical-owner',
                'method-factory-namespaces-imports-and-related-parent',
                'method-factory-reference-formal-and-promoted-source',
                'method-factory-lazy-final-conflict-before-argument',
                'method-factory-skipped-lazy-final-conflict',
                'method-factory-unrelated-lexical-constructor-denial',
                'method-factory-uncalled-body-property-compile-error']
    raw = Path(tempfile.mkdtemp(prefix='class178-review-state-', dir=ROOT / '.tools'))
    modules = [ROOT / n for n in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [CATALOGUE, Path(__file__), ROOT / 'spec/semantics/modules.json',
               ROOT / 'spec/semantics/383-anonymous-classes.watsup', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(p): sha(p) for p in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'affinity': sorted(os.sched_getaffinity(0)), 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        fixtures, filenames = {}, {}
        for name in selected:
            source = raw / (name + '.php')
            source.write_text(rows[name]['source'])
            assert sha(source) == rows[name]['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            fixtures[name], filenames[name] = checked['fixture'], os.fsencode(source)
        def grouped(function, names):
            return function([rows[n] for n in names], [fixtures[n] for n in names], [filenames[n] for n in names])
        groups = [('inherited_instance_lexical_scope', inherited(rows[selected[0]], fixtures[selected[0]], filenames[selected[0]])),
                  ('namespace_import_source_identity', namespaces(rows[selected[1]], fixtures[selected[1]], filenames[selected[1]])),
                  ('reference_formal_promoted_source', reference(rows[selected[2]], fixtures[selected[2]], filenames[selected[2]])),
                  ('called_skipped_lazy_link_order', grouped(lazy, selected[3:5])),
                  ('unrelated_constructor_scope_compile_order', grouped(denial_compile, selected[5:]))]
        code, calls, counts = PREFIX, [], {}
        for index, (name, checks) in enumerate(groups):
            function = '$class178_review_group' + str(index)
            code += 'dec ' + function + '() : bool\ndef ' + function + '() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks)
            calls.append(function + '()')
            counts[name] = len(checks)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + ' /\\ '.join(calls) + '\n')
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)]
        result = cross.invoke.process(command, raw / 'numeric', 1200, ROOT)
        report.update(command=command, exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), conditions=counts, fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter: adapter.close()
        finally:
            if frontend: frontend.close()
        report['inputs_after'] = {str(p): sha(p) for p in watched}
        report['inputs_stable'] = report['inputs_after'] == before
        report['passed'] = report['passed'] and report['inputs_stable']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

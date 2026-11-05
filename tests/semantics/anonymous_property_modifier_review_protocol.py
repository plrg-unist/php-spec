#!/usr/bin/env python3
"""Independent anonymous setter scope, storage and inheritance fronts."""
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
CATALOGUE = ROOT / 'tests/semantics/anonymous_property_modifier_cases.json'
PREFIX = r'''
dec $class174_review_front(pstate,nat) : bool
def $class174_review_front(S,0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) =/= eps
def $class174_review_front(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS =/= eps
  -- if S.TODO = (EVAL (NExprAssign (NExprPropertyFetch expression_receiver (NIdentifier (BYTES text) metadata_name) metadata_property) expression_value metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("value")
def $class174_review_front(S,n) = false -- otherwise
dec $class174_review_seek(pstate,nat,nat) : pstate
def $class174_review_seek(S,n_front,0) = S
def $class174_review_seek(S,n_front,n) = S
  -- if $(n > 0)
  -- if $class174_review_front(S,n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class174_review_seek(S,n_front,n) = $class174_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class174_review_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $class174_review_output_item(pevent) : ptbytes
def $class174_review_output_item(OUTPUT ptbytes) = ptbytes
def $class174_review_output_item(pevent) = eps -- otherwise
dec $class174_review_outputs(pevent*) : ptbytes
def $class174_review_outputs(eps) = eps
def $class174_review_outputs(pevent :: pevent_tail*) = $class174_review_output_item(pevent) ++ $class174_review_outputs(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def final_checks(row, state, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [
        state + '.COMPLETION = NORMAL /\\ ' + state + '.TODO = eps /\\ ' + state + '.CURRENT = eps',
        '$class174_review_outputs(' + state + '.EVENTS) = ' + term(expected),
        '$class_state_valid(' + state + ') /\\ $property_state_valid(' + state + ')',
        '$declaration_history_valid(' + state + ')',
    ]


def checks(row, fixture, filename):
    name = row['id']
    compile_error = name == 'asymmetric-untyped-property-compile-error'
    caller = name == 'asymmetric-anonymous-caller-and-declaring-display'
    static = name == 'asymmetric-static-setter-storage-and-denials'
    narrow = name == 'asymmetric-parent-setter-narrowing-before-argument'
    out = ['program_source = ' + fixture,
           'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')']
    if compile_error:
        stderr = base64.b64decode(row['stderr_template_base64'])
        message = stderr.split(b'Fatal error: ', 1)[1].split(b' in {FILE} on line ', 1)[0]
        return out + ['S_initial.COMPLETION = STATICBYTES ' + term(message) + ' 4',
                      'S_initial.EVENTS = eps', 'S_initial.OBJECTS = eps']
    out += ['S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP']
    if caller:
        target_name = b'class@anonymous\0' + filename + b':2$0'
        caller_name = b'class@anonymous\0' + filename + b':3$1'
        return out + [
            'S_scope = $class174_review_seek(S_initial,1,2000)',
            '$class174_review_front(S_scope,1) /\\ S_scope.COMPLETION = BUDGET',
            'S_scope.CURRENT = (pcallcontext)',
            '$lookup($global_table_view(S_scope).ENV,$ptascii("target")) = (n_cell_target)',
            'S_scope.STORE[n_cell_target] = DEFINED (POBJECT n_target)',
            'S_scope.OBJECTS[n_target] = INSTANCE porigin_target',
            '$class_at(S_scope.CLASSES,porigin_target) = (pclassdesc_target)',
            'pclassdesc_target.NAME = ' + term(target_name),
            '$lookup($global_table_view(S_scope).ENV,$ptascii("caller")) = (n_cell_caller)',
            'S_scope.STORE[n_cell_caller] = DEFINED (POBJECT n_caller)',
            'S_scope.OBJECTS[n_caller] = INSTANCE porigin_caller',
            '$class_at(S_scope.CLASSES,porigin_caller) = (pclassdesc_caller)',
            'pclassdesc_caller.NAME = ' + term(caller_name),
            'porigin_target =/= porigin_caller /\\ pclassdesc_target.NAME =/= pclassdesc_caller.NAME',
            '$c_string(pclassdesc_target.NAME) = $c_string(pclassdesc_caller.NAME)',
            'pcallcontext.LEXICAL_CLASS = (porigin_caller) /\\ pcallcontext.CALLED_CLASS = (porigin_caller)',
            '$call_current_valid(S_scope)',
            'pclassdesc_target.PROPERTIES = [ppropertydesc_value]',
            'ppropertydesc_value.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc_value.SETVISIBILITY = (PROPERTY_PRIVATE)',
            'ppropertydesc_value.KEY = $ptascii("value") /\\ ppropertydesc_value.FINAL',
            '$property_declaring_name(S_scope.CLASSES,ppropertydesc_value.ORIGIN) = pclassdesc_target.NAME',
            '$property_instance_set_desc(S_scope,n_target,$ptascii("value")) = (ppropertydesc_value)',
            '~$class_static_set_allowed(S_scope,ppropertydesc_value)',
            '$property_set_denied(S_scope,n_target,$ptascii("value"))',
            '$class_static_set_scope(S_scope) = $ptascii("scope class@anonymous")',
            '$class_static_set_message(S_scope,ppropertydesc_value,$ptascii("modify")) = $ptascii("Cannot modify private(set) property class@anonymous::$value from scope class@anonymous")',
            'S_wrong_scope = S_scope[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_target)])]',
            '$class_static_set_allowed(S_wrong_scope,ppropertydesc_value)',
            '~$call_current_valid(S_wrong_scope)',
            '$location_slot(S_scope,PROPERTY n_target ppropertydesc_value.KEY) = DEFINED (PINT 5)',
            'S_done = $drive_steps(S_scope[.COMPLETION = NORMAL],4000)',
            *final_checks(row,'S_done',filename),
            '$location_slot(S_done,PROPERTY n_target ppropertydesc_value.KEY) = DEFINED (PINT 5)',
        ]
    line = 2 if static else (5 if narrow else 3)
    prefix = b'class@anonymous' if static else (b'Probe174NarrowBase@anonymous' if narrow else b'Probe174WeakerBase@anonymous')
    class_name = prefix + b'\0' + filename + b':' + str(line).encode() + b'$0'
    out += [
        'S_pre = $class174_review_seek(S_initial,0,1000)',
        '$class174_review_front(S_pre,0) /\\ S_pre.COMPLETION = BUDGET',
        'S_pre.ORIGIN = (PORIGIN 0 pcpath_new)',
        'porigin_new = PORIGIN 0 pcpath_new',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc_raw)',
        'pclassdesc_raw.NAME = ' + term(class_name),
    ]
    if static:
        return out + [
            'pclassdesc_raw.PROPERTIES = [ppropertydesc_count,ppropertydesc_other]',
            'ppropertydesc_count.STATIC /\\ ppropertydesc_other.STATIC',
            'ppropertydesc_count.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc_other.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_count.SETVISIBILITY = (PROPERTY_PRIVATE) /\\ ppropertydesc_other.SETVISIBILITY = (PROPERTY_PROTECTED)',
            'ppropertydesc_count.FINAL /\\ ~ppropertydesc_other.FINAL',
            'ppropertydesc_count.KEY = $ptascii("count") /\\ ppropertydesc_other.KEY = $ptascii("other")',
            'S_forged = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_raw[.PROPERTIES = [ppropertydesc_count[.SETVISIBILITY = eps],ppropertydesc_other]])]',
            '$anonymous_new_descriptor(S_forged,porigin_new) = eps',
            'S_done = $drive_steps(S_pre[.COMPLETION = NORMAL],4000)',
            *final_checks(row,'S_done',filename),
            '$class_static_at(S_done.CLASSSTATICS,ppropertydesc_count.ORIGIN) = (pclassstatic_count)',
            '$class_static_at(S_done.CLASSSTATICS,ppropertydesc_other.ORIGIN) = (pclassstatic_other)',
            'pclassstatic_count.STATE = PROP_VALUE (DIRECT (PINT 5))',
            'pclassstatic_other.STATE = PROP_VALUE (DIRECT (PINT 7))',
            '$class_statics_valid(S_done)',
            '$anonymous_new_descriptor(S_done,porigin_new) = (pclassdesc_raw)',
        ]
    out += [
        '~pclassdesc_raw.EARLY',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        'pclassdesc_raw.PROPERTIES = [ppropertydesc_value]',
        'ppropertydesc_value.KEY = $ptascii("value") /\\ ppropertydesc_value.VISIBILITY = PROPERTY_PUBLIC',
    ]
    if narrow:
        stderr = base64.b64decode(row['stderr_template_base64'])
        message = stderr.split(b'Fatal error: ', 1)[1].split(b' in {FILE} on line ', 1)[0]
        return out + [
            'ppropertydesc_value.SETVISIBILITY = (PROPERTY_PRIVATE) /\\ ppropertydesc_value.FINAL',
            '$class_named(S_pre.CLASSNAMES,$ptascii("probe174narrowbase")) = (porigin_base)',
            '$class_at(S_pre.CLASSES,porigin_base) = (pclassdesc_base)',
            'pclassdesc_base.PROPERTIES = [ppropertydesc_base]',
            'ppropertydesc_base.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ ~ppropertydesc_base.FINAL',
            '$ppproperty_inherit_message(pclassdesc_raw.NAME,pclassdesc_base.NAME,ppropertydesc_base,ppropertydesc_value) = (' + term(message) + ')',
            'S_pre.EVENTS = [OUTPUT $ptascii("before;")]',
            'S_fatal = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
            'S_fatal.COMPLETION = STATICBYTES ' + term(message) + ' 5',
            'S_fatal.EVENTS = S_pre.EVENTS /\\ S_fatal.OBJECTS = eps',
            '$class_named(S_fatal.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
            '~$anonymous_runtime_declaration(S_fatal.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        ]
    return out + [
        'ppropertydesc_value.SETVISIBILITY = eps /\\ ~ppropertydesc_value.FINAL /\\ ~ppropertydesc_value.READONLY',
        'ppropertydesc_value.ORIGIN = PORIGIN 0 pcpath_property',
        '$(|pcpath_property| >= 2)',
        'pcpath_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]',
        '$origin_node(S_pre.SOURCES,PORIGIN 0 pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 129) phpType18 phpType56 (SEQUENCE eps) metadata)',
        '$class_named(S_pre.CLASSNAMES,$ptascii("probe174weakerbase")) = (porigin_base)',
        '$class_at(S_pre.CLASSES,porigin_base) = (pclassdesc_base)',
        'pclassdesc_base.PROPERTIES = [ppropertydesc_base]',
        'ppropertydesc_base.SETVISIBILITY = (PROPERTY_PROTECTED)',
        'S_forged = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_raw[.PROPERTIES = [ppropertydesc_value[.SETVISIBILITY = (PROPERTY_PROTECTED)]]])]',
        '$anonymous_new_descriptor(S_forged,porigin_new) = eps',
        'S_done = $drive_steps(S_pre[.COMPLETION = NORMAL],4000)',
        *final_checks(row,'S_done',filename),
        '$class_link_at(S_done.LINKEDPARENTS,pclassdesc_raw.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$lookup($global_table_view(S_done).ENV,$ptascii("object")) = (n_cell)',
        'S_done.STORE[n_cell] = DEFINED (POBJECT n_object)',
        'S_done.OBJECTS[n_object] = INSTANCE pclassdesc_raw.ORIGIN',
        '$location_slot(S_done,PROPERTY n_object ppropertydesc_value.KEY) = DEFINED (PINT 8)',
        '$class_static_set_allowed(S_done,ppropertydesc_value)',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']:row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['asymmetric-anonymous-caller-and-declaring-display',
                'asymmetric-static-setter-storage-and-denials',
                'asymmetric-inherited-weaker-setter-success',
                'asymmetric-parent-setter-narrowing-before-argument',
                'asymmetric-untyped-property-compile-error']
    raw = Path(tempfile.mkdtemp(prefix='class174-review-state-',dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/modules.json',CATALOGUE,Path(__file__),
               ROOT / '.tools/php/bin/php',ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe',ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    watched += [ROOT / 'spec/semantics' / name for name in
                ['200-static-set-compiler.watsup','201-static-set-runtime.watsup','383-anonymous-classes.watsup']]
    before = {str(path):sha(path) for path in watched}
    report = {'passed':False,'raw':str(raw),'inputs_before':before,
              'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'affinity':sorted(os.sched_getaffinity(0)),'environment':{'LC_ALL':'C','TZ':'UTC'}}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,
                           '-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],raw / 'adapter')
        code,groups,counts = PREFIX,[],{}
        for index,name in enumerate(selected):
            row = rows[name]
            path = raw / (name + '.php')
            path.write_text(row['source'])
            assert sha(path) == row['source_sha256']
            parsed = frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
            assert checked['ok']
            conditions = checks(row,checked['fixture'],os.fsencode(path))
            group = '$class174_review_group' + str(index)
            code += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n' + ''.join(
                '  -- if ' + condition + '\n' for condition in conditions)
            groups.append(group + '()')
            counts[name] = len(conditions)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + ' /\\ '.join(groups) + '\n')
        modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(fixture)]
        result = cross.invoke.process(command,raw / 'numeric',1200,ROOT)
        report.update(command=command,exit=result.returncode,stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'),conditions=counts,fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter:adapter.close()
        finally:
            if frontend:frontend.close()
        report['inputs_after'] = {str(path):sha(path) for path in watched}
        report['inputs_stable'] = report['inputs_after'] == before
        report['passed'] = report['passed'] and report['inputs_stable']
        (raw / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
        print(raw / 'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Independent implicit-interface projection, source scope and forgery checks."""
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
CATALOGUE = ROOT / 'tests/semantics/anonymous_trait_stringable_cases.json'
PREFIX = r'''
dec $class170_review_front(pstate, nat) : bool
def $class170_review_front(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_pending(S, porigin) =/= eps
def $class170_review_front(S, 1) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if S.OBJECTS[n] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin porigin_site porigin_called eps)
def $class170_review_front(S, n) = false -- otherwise
dec $class170_review_seek(pstate, nat, nat) : pstate
def $class170_review_seek(S, n_front, 0) = S
def $class170_review_seek(S, n_front, n) = S
  -- if $(n > 0) /\ $class170_review_front(S, n_front)
def $class170_review_seek(S, n_front, n) = $class170_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_front, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class170_review_front(S, n_front)
  -- if S.COMPLETION = BUDGET
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def checks(row, fixture, filename):
    parented = row['id'] == 'parented-interface-imported-stringable-capture'
    explicit = row['id'] == 'explicit-mixedcase-stringable-alias-control'
    missing_parent = row['id'] == 'parentless-stringable-parent-receive'
    prefix = 'Probe170Base@anonymous' if parented else 'sTrInGaBlE@anonymous' if explicit else 'class@anonymous'
    line = next(n for n, text in enumerate(row['source'].splitlines(), 1) if '$object = new class' in text)
    own = 'pclassdesc_live[.PROPERTIES = $trait_notice_own_properties(pclassdesc_live.PROPERTIES)][.CONSTANTS = $trait_notice_own_constants(pclassdesc_live.CONSTANTS)][.METHODS = $trait_notice_own_methods(pclassdesc_live.METHODS,pclassdesc_live.ORIGIN)]'
    result = [
        'program_source = ' + fixture,
        'S_start = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_start.COMPLETION = BUDGET /\\ ~S_start.COMPILESTOP',
        'S_pre = $class170_review_seek(S_start,0,100)',
        '$class170_review_front(S_pre,0) /\\ S_pre.COMPLETION = BUDGET',
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        '~pclassdesc_raw.EARLY',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        'pclassdesc_raw.NAME = $ptascii(' + json.dumps(prefix) + ') ++ [0] ++ ' + term(filename) + ' ++ [58] ++ $ntunsigned(' + str(line) + ') ++ [36,48]',
        'S_link = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
        'S_link.COMPLETION = BUDGET',
        '$class_at(S_link.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        'pclassdesc_live.NAME = pclassdesc_raw.NAME',
        'pclassdesc_live.INTERFACES = $trait_import_interfaces(pclassdesc_raw,pclassdesc_live.METHODS)',
        own + '[.INTERFACES = pclassdesc_raw.INTERFACES] = pclassdesc_raw',
        '$declaration_history_valid(S_link)',
        '$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$anonymous_new_descriptor(S_link,porigin_new) = (pclassdesc_live)',
        '$anonymous_new_available(S_link,pclassdesc_live)',
        '$class_origin_matches(S_link,pclassdesc_live.ORIGIN,$ptascii("Stringable"),|S_link.CLASSES|)',
        '$method_named(pclassdesc_live.METHODS,$ptascii("__toString")) = (pmethoddesc_string)',
        'pmethoddesc_string.OWNER = pclassdesc_live.ORIGIN /\\ pmethoddesc_string.VISIBILITY = PROPERTY_PUBLIC /\\ ~pmethoddesc_string.STATIC',
        'pmethoddesc_string.FUNCTION.ORIGIN = TRAIT_ORIGIN pclassdesc_live.ORIGIN porigin_string_source pmethoddesc_string.NAME',
        '$class_method_origin(S_link.CLASSES,porigin_string_source) = (pmethoddesc_string_source)',
        'S_drop = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_live[.INTERFACES = eps])]',
        '$anonymous_new_descriptor(S_drop,porigin_new) = eps',
        '~$declaration_history_valid(S_drop)',
        'S_duplicate = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_live[.INTERFACES = pclassdesc_live.INTERFACES ++ [$ptascii("Stringable")]])]',
        '$anonymous_new_descriptor(S_duplicate,porigin_new) = eps',
        'S_replace = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_live[.INTERFACES = [$ptascii("Unrelated170")]])]',
        '$anonymous_new_descriptor(S_replace,porigin_new) = eps',
        'S_missing_links = S_link[.LINKEDINTERFACES = S_pre.LINKEDINTERFACES]',
        '~$anonymous_new_available(S_missing_links,pclassdesc_live)',
        'S_allocate = $drive_steps(S_link[.COMPLETION = NORMAL],1)',
        'S_allocate.COMPLETION = BUDGET',
        'S_allocate.RESULT = KNOWN (POBJECT n_object)',
        'S_allocate.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        '(HOBJECT n_object) <- S_allocate.ALLOCATIONS',
        '$class_state_valid(S_allocate[.COMPLETION = NORMAL])',
    ]
    if parented:
        result += [
            'pclassdesc_raw.PARENT = ($ptascii("Probe170Base"))',
            'pclassdesc_raw.INTERFACES = [$ptascii("Probe170I")]',
            'pclassdesc_live.INTERFACES = [$ptascii("Probe170I"),$ptascii("Stringable")]',
            '$class_named(S_link.CLASSNAMES,$ptascii("probe170base")) = (porigin_base)',
            '$class_link_at(S_link.LINKEDPARENTS,pclassdesc_live.ORIGIN) = (SOURCE_PARENT porigin_base)',
            '$class_named(S_link.CLASSNAMES,$ptascii("probe170i")) = (porigin_interface)',
            '$pil_at(S_link.LINKEDINTERFACES,pclassdesc_live.ORIGIN) = (PILTARGETS ([PILSOURCE $ptascii("Probe170I") porigin_interface,PILBUILTIN $ptascii("Stringable")]))',
            own + ' =/= pclassdesc_raw',
        ]
    elif explicit:
        result += [
            'pclassdesc_raw.PARENT = eps',
            'pclassdesc_raw.INTERFACES = [$ptascii("sTrInGaBlE")]',
            'pclassdesc_live.INTERFACES = pclassdesc_raw.INTERFACES',
            own + ' = pclassdesc_raw',
            '$pil_at(S_link.LINKEDINTERFACES,pclassdesc_live.ORIGIN) = (PILTARGETS ([PILBUILTIN $ptascii("sTrInGaBlE")]))',
            'pmethoddesc_string_source.NAME = $ptascii("render")',
            '$origin_source(pmethoddesc_string.FUNCTION.ORIGIN) = pmethoddesc_string_source.FUNCTION.ORIGIN',
        ]
    else:
        result += [
            'pclassdesc_raw.PARENT = eps /\\ pclassdesc_raw.INTERFACES = eps',
            'pclassdesc_live.INTERFACES = [$ptascii("Stringable")]',
            own + ' =/= pclassdesc_raw',
            '$class_link_at(S_link.LINKEDPARENTS,pclassdesc_live.ORIGIN) = eps',
            '$pil_at(S_link.LINKEDINTERFACES,pclassdesc_live.ORIGIN) = (PILTARGETS ([PILBUILTIN $ptascii("Stringable")]))',
            'pmethoddesc_string_source.NAME = $ptascii("__toString")',
        ]
    if not explicit:
        type_atom = 'PTPARENT' if missing_parent else 'PTCLASS ' + ('$ptascii("Probe170Base")' if parented else 'pclassdesc_live.NAME')
        result += [
            '$method_named(pclassdesc_live.METHODS,$ptascii(' + json.dumps('q' if parented else 'm') + ')) = (pmethoddesc_capture)',
            'pmethoddesc_capture.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
            'psparam.TYPE = [(PTBRANCH ([' + type_atom + ']))]',
            'S_receive = $class170_review_seek(S_allocate,1,500)',
            '$class170_review_front(S_receive,1) /\\ S_receive.COMPLETION = BUDGET',
            'S_receive.TODO = (TYPE_RECEIVE pmethoddesc_capture.FUNCTION.ORIGIN 0) :: ptask_receive_tail*',
            'S_receive.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_capture',
            'pcallcontext.INSTANCE = (n_capture)',
            'pcallcontext.LEXICAL_CLASS = (pclassdesc_live.ORIGIN) /\\ pcallcontext.CALLED_CLASS = (pclassdesc_live.ORIGIN)',
            'S_receive.OBJECTS[n_capture] = CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_capture.FUNCTION.ORIGIN porigin_site pclassdesc_live.ORIGIN eps)',
            '$closure_scope_at(S_receive.CLOSURESCOPES,n_capture) = (pclosurescope)',
            'pclosurescope.LEXICAL = pclassdesc_live.ORIGIN /\\ pclosurescope.CALLED = pclassdesc_live.ORIGIN',
            '$class_constant_callable_method_history_ordinary(S_receive,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = (pclassdesc_live.ORIGIN)',
            'pmethoddesc_capture.FUNCTION.ORIGIN = TRAIT_ORIGIN pclassdesc_live.ORIGIN porigin_capture_source pmethoddesc_capture.NAME',
            '$class_method_origin(S_receive.CLASSES,porigin_capture_source) = (pmethoddesc_capture_source)',
            '$class_at(S_receive.CLASSES,pmethoddesc_capture_source.OWNER) = (pclassdesc_trait)',
            'pclassdesc_trait.KIND = "trait"',
            '$class_constant_callable_method_history_ordinary(S_receive,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope[.CALLED = pclassdesc_trait.ORIGIN]) = eps',
            '$call_current_valid(S_receive)',
        ]
        if not missing_parent:
            result.append('$method_closure_functions(S_receive,n_capture,pmethoddesc_capture) = (pmethoddesc_capture.FUNCTION,pmethoddesc_capture.FUNCTION)')
    if missing_parent:
        stderr = base64.b64decode(row['stderr_template_base64']).replace(b'{FILE}', filename)
        result += [
            '$trait_real_birth_at(S_receive.CLASSCONSTANTHISTORY,n_capture) = eps',
            '$trait_fcc_scope_owner(S_receive,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = (pclassdesc_live.ORIGIN)',
            '$trait_fcc_parameter_function(S_receive,n_capture,pmethoddesc_capture) = (pfunction_view)',
            'pfunction_view.SIGNATURE.PARAMETERS = psparam :: eps',
            '~$ppsupported_signature(pfunction_view.SIGNATURE)',
            '$call_supported_signature(S_receive,pfunction_view)',
            'S_receive.LINKEDINTERFACES = [{OWNER pclassdesc_live.ORIGIN,TARGETS ([PILBUILTIN $ptascii("Stringable")])}]',
            'pclassdesc_double = pclassdesc_live[.INTERFACES = [$ptascii("Stringable"),$ptascii("Stringable")]]',
            'S_synced = S_receive[.CLASSES = $trait_class_set(S_receive.CLASSES,pclassdesc_double)][.LINKEDINTERFACES = [{OWNER pclassdesc_live.ORIGIN,TARGETS ([PILBUILTIN $ptascii("Stringable"),PILBUILTIN $ptascii("Stringable")])}]]',
            '$anonymous_interface_targets_valid(S_synced,pclassdesc_double)',
            '$class_constant_callable_method_history_ordinary(S_synced,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = (pclassdesc_live.ORIGIN)',
            '~$declaration_history_valid(S_synced)',
            '$trait_fcc_scope_owner(S_synced,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = eps',
            'S_receive.EVENTS = [OUTPUT $ptascii("before;"),OUTPUT $ptascii("captured;")]',
            '$eval_exception_trace(S_receive) = ptraceframe :: ptraceframe_tail*',
            'ptraceframe.CLASS = (pclassdesc_live.NAME)',
            '$error_trace_call(ptraceframe) = $ptascii("class@anonymous::m")',
            'S_fatal = $drive_steps(S_receive[.COMPLETION = NORMAL],1)',
            'S_fatal.COMPLETION = REQUESTFATAL $ptascii("Error") $ptascii("Cannot access \\"parent\\" when current class scope has no parent") 4',
            'S_fatal.EVENTS = S_receive.EVENTS ++ [STDERR ' + term(stderr) + ']',
        ]
    return result


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    cases = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['parentless-imported-stringable-capture', 'parented-interface-imported-stringable-capture',
                'explicit-mixedcase-stringable-alias-control', 'parentless-stringable-parent-receive']
    raw = Path(tempfile.mkdtemp(prefix='class170-review-state-', dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/modules.json', *(ROOT / 'spec/semantics' / name for name in
               ['189-internal-interface-prototypes.watsup', '307-trait-callable-target-fixups.watsup', '383-anonymous-classes.watsup']),
               ROOT / '.tools/php/bin/php', ROOT / 'tests/semantics/profile.json', CATALOGUE,
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', Path(__file__)]
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'affinity': sorted(os.sched_getaffinity(0))}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        code, names, counts = PREFIX, [], {}
        for i, name in enumerate(selected):
            row = cases[name]
            source = raw / (name + '.php')
            source.write_text(row['source'])
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            function = '$class170_review_group' + str(i)
            code += 'dec ' + function + '() : bool\ndef ' + function + '() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in conditions)
            names.append(function + '()')
            counts[name] = len(conditions)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + ' /\\ '.join(names) + '\n')
        modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)]
        result = cross.invoke.process(command, raw / 'numeric', 1200, ROOT)
        report.update(command=command, exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), conditions=counts, fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['inputs_stable'] = before == report['inputs_after']
        report['passed'] = report['passed'] and report['inputs_stable']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

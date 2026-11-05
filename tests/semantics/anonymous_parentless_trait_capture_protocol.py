#!/usr/bin/env python3
"""Source-reached deferred parentless trait capture and receive boundary."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_parentless_trait_capture_cases.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def positive(fixture, filename):
    run = lambda steps: '$php_run(program_source,' + str(steps) + ',' + json.dumps(base64.b64encode(filename).decode()) + ')'
    return [
        'program_source = ' + fixture,
        'S_pre = ' + run(8),
        'S_pre.COMPLETION = BUDGET',
        'S_pre.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE statement*) metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*',
        'statement* = [statement_use]',
        '$anonymous_parentless_trait_node(NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE statement*) metadata_class)',
        '$anonymous_trait_use_count(statement*) = 1',
        '~$anonymous_class_node(NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE (statement_use :: statement_use :: eps)) metadata_class)',
        'S_pre.ORIGIN = (PORIGIN 0 pcpath)',
        '$source_unit(S_pre.SOURCES,0) = (pcunit)',
        '$compilation_projection(S_pre,pcunit) = (ppinstalled)',
        '$class_at(ppinstalled.CLASSES,PORIGIN 0 (pcpath ++ [PCFIELD 0])) = (pclassdesc_raw)',
        '$class_at(S_pre.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_raw)',
        'pclassdesc_raw.PARENT = eps /\\ pclassdesc_raw.INTERFACES = eps /\\ ~pclassdesc_raw.EARLY',
        '$anonymous_class_name(' + term(filename) + ',8,0) = (pclassdesc_raw.NAME)',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        '$anonymous_new_pending(S_pre,PORIGIN 0 pcpath) = (pclassdesc_raw)',
        '~$anonymous_new_available(S_pre,pclassdesc_raw)',
        'S_link = ' + run(9),
        'S_link.COMPLETION = BUDGET',
        '$class_at(S_link.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        'pclassdesc_live[.PROPERTIES = $trait_notice_own_properties(pclassdesc_live.PROPERTIES)][.CONSTANTS = $trait_notice_own_constants(pclassdesc_live.CONSTANTS)][.METHODS = $trait_notice_own_methods(pclassdesc_live.METHODS,pclassdesc_live.ORIGIN)] = pclassdesc_raw',
        '$class_named(S_link.CLASSNAMES,$ptlc(pclassdesc_live.NAME)) = (pclassdesc_live.ORIGIN)',
        '$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$class_link_at(S_link.LINKEDPARENTS,pclassdesc_live.ORIGIN) = eps',
        '$pil_at(S_link.LINKEDINTERFACES,pclassdesc_live.ORIGIN) = eps',
        '$declaration_history_valid(S_link)',
        '$anonymous_new_descriptor(S_link,PORIGIN 0 pcpath) = (pclassdesc_live)',
        '$anonymous_new_available(S_link,pclassdesc_live)',
        '$anonymous_new_pending(S_link,PORIGIN 0 pcpath) = eps',
        'pclassdesc_live.METHODS = pmethoddesc_imported :: pmethoddesc_tail*',
        '$trait_imported_origin(pmethoddesc_imported.FUNCTION.ORIGIN)',
        'pclassdesc_forged = pclassdesc_live[.METHODS = pclassdesc_live.METHODS ++ [pmethoddesc_imported]]',
        'S_forged = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_forged)]',
        '~$declaration_history_valid(S_forged)',
        '$anonymous_new_descriptor(S_forged,PORIGIN 0 pcpath) = eps',
        'S_alloc = ' + run(10),
        'S_alloc.COMPLETION = BUDGET',
        'S_alloc.RESULT = KNOWN (POBJECT n_object)',
        'S_alloc.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        '(HOBJECT n_object) <- S_alloc.ALLOCATIONS',
        '$class_state_valid(S_alloc[.COMPLETION = NORMAL])',
        '$heap_valid($heap_graph(S_alloc))',
    ]


def negative(fixture, filename):
    run = lambda steps: '$php_run(program_source,' + str(steps) + ',' + json.dumps(base64.b64encode(filename).decode()) + ')'
    stderr = (b'Fatal error: Cannot access "parent" when current class scope has no parent in '
              + filename + b' on line 3\nStack trace:\n#0 ' + filename
              + b'(10): class@anonymous::take(Object(stdClass))\n#1 {main}\n')
    return [
        'program_source = ' + fixture,
        'S = ' + run(81),
        'S.COMPLETION = BUDGET',
        'S.TODO = (TYPE_RECEIVE porigin_method 0) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n',
        'pcallcontext.INSTANCE = (n)',
        'pcallcontext.FUNCTION = porigin_method',
        'S.OBJECTS[n] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_method porigin_site porigin_requested eps)',
        '$closure_scope_at(S.CLOSURESCOPES,n) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_requested /\\ pclosurescope.CALLED = porigin_requested',
        '$class_at(S.CLASSES,porigin_requested) = (pclassdesc)',
        'pclassdesc.KIND = "class" /\\ pclassdesc.PARENT = eps /\\ pclassdesc.INTERFACES = eps',
        '$class_link_at(S.LINKEDPARENTS,porigin_requested) = eps',
        '$pil_at(S.LINKEDINTERFACES,porigin_requested) = eps',
        '$origin_node(S.SOURCES,porigin_requested) = (pcnode_class)',
        '$anonymous_parentless_trait_node(pcnode_class)',
        '$class_named(S.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (porigin_requested)',
        '$anonymous_runtime_declaration(S.DECLARATIONS,porigin_requested)',
        '$closure_method_origin(S,porigin_method) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_requested',
        'pmethoddesc.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_requested porigin_source ptbytes',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
        'psparam.TYPE = [(PTBRANCH ([PTPARENT]))]',
        '$constant_callable_record(S.CONSTANTCLOSURES,n) = (pconstantclosure)',
        '$constant_callable_record_valid(S,pconstantclosure)',
        '$class_constant_callable_method_history_ordinary(S,pmethoddesc,porigin_site,porigin_requested,pclosurescope) = (porigin_requested)',
        '$trait_fcc_scope_owner(S,pmethoddesc,porigin_site,porigin_requested,pclosurescope) = (porigin_requested)',
        '$trait_fcc_parameter_function(S,n,pmethoddesc) = (pfunction_view)',
        'pfunction_view.SIGNATURE.PARAMETERS = psparam :: eps',
        '$call_supported_signature(S,pfunction_view)',
        'S_bad_link = S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK porigin_requested STDCLASS_PARENT]]',
        '$class_constant_callable_method_history_ordinary(S_bad_link,pmethoddesc,porigin_site,porigin_requested,pclosurescope) = (porigin_requested)',
        '$trait_fcc_scope_owner(S_bad_link,pmethoddesc,porigin_site,porigin_requested,pclosurescope) = eps',
        'pclassdesc_bad = pclassdesc[.PARENT = ($ptascii("stdClass"))]',
        'S_bad_parent = S[.CLASSES = $trait_class_set(S.CLASSES,pclassdesc_bad)]',
        '$trait_fcc_scope_owner(S_bad_parent,pmethoddesc,porigin_site,porigin_requested,pclosurescope) = eps',
        '$eval_exception_trace(S) = ptraceframe :: ptraceframe_tail*',
        'ptraceframe.CLASS = (pclassdesc.NAME)',
        '$error_trace_call(ptraceframe) = $ptascii("class@anonymous::take")',
        'S_fatal = ' + run(82),
        'S_fatal.COMPLETION = REQUESTFATAL $ptascii("Error") $ptascii("Cannot access \\"parent\\" when current class scope has no parent") 3',
        'S_fatal.EVENTS = S.EVENTS ++ [STDERR ' + term(stderr) + ']',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    cases = json.loads(CATALOGUE.read_text())['cases']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    for row, checks in ((cases[0], positive), (cases[1], negative)):
        raw = Path(tempfile.mkdtemp(prefix='anonymous-parentless-trait-', dir=ROOT / '.tools'))
        source = raw / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256']
        watched = [ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/207-error-handler-runtime.watsup',
                   ROOT / 'spec/semantics/307-trait-callable-target-fixups.watsup',
                   ROOT / 'spec/semantics/383-anonymous-classes.watsup', CATALOGUE,
                   source, Path(__file__), ROOT / '_build/default/adapter/main.exe',
                   ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
        before = {str(path): sha(path) for path in watched}
        report = {'passed': False, 'case': row['id'], 'source_sha256': row['source_sha256'],
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
            conditions = checks(checked['fixture'], os.fsencode(source))
            fixture = raw / 'protocol.watsup'
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + condition + '\n' for condition in conditions))
            result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                           '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
            report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                          stderr=result.stderr.decode(errors='replace'),
                          conditions=len(conditions), fixture_sha256=sha(fixture))
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['passed'] = True
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

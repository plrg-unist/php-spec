#!/usr/bin/env python3
"""Method factory runtime counters and source-derived compiler context refusals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_method_factory_cases.json'
PREFIX = r'''
dec $factory178_gate(pstate, ptbytes) : bool
def $factory178_gate(S, eps) = true
def $factory178_gate(S, ptbytes) = true
  -- if ptbytes =/= eps
  -- if $lookup($global_table_view(S).ENV,ptbytes) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
def $factory178_gate(S, ptbytes) = false -- otherwise
dec $factory178_front(pstate, ptbytes, ptbytes) : bool
def $factory178_front(S, ptbytes_method, ptbytes_gate) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = SCOPED_TARGET porigin_owner porigin_method porigin_owner eps poperand_selector
  -- if $class_at(S.CLASSES,porigin_owner) = (pclassdesc_owner)
  -- if $method_named(pclassdesc_owner.METHODS,ptbytes_method) = (pmethoddesc)
  -- if pmethoddesc.FUNCTION.ORIGIN = porigin_method
  -- if $factory178_gate(S,ptbytes_gate)
def $factory178_front(S, ptbytes_method, ptbytes_gate) = false -- otherwise
dec $factory178_seek(pstate, ptbytes, ptbytes, nat) : pstate
def $factory178_seek(S, ptbytes_method, ptbytes_gate, 0) = S
def $factory178_seek(S, ptbytes_method, ptbytes_gate, n) = S
  -- if $(n > 0) /\ $factory178_front(S,ptbytes_method,ptbytes_gate)
def $factory178_seek(S, ptbytes_method, ptbytes_gate, n) = $factory178_seek($drive_steps(S[.COMPLETION = NORMAL],1),ptbytes_method,ptbytes_gate,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$factory178_front(S,ptbytes_method,ptbytes_gate)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $factory178_seek(S, ptbytes_method, ptbytes_gate, n) = S -- otherwise
dec $factory178_output_item(pevent) : ptbytes
def $factory178_output_item(OUTPUT ptbytes) = ptbytes
def $factory178_output_item(pevent) = eps -- otherwise
dec $factory178_output(pevent*) : ptbytes
def $factory178_output(eps) = eps
def $factory178_output(pevent :: pevent_tail*) = $factory178_output_item(pevent) ++ $factory178_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def final_checks(row, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$factory178_output(S_done.EVENTS) = ' + term(expected),
            r'$class_state_valid(S_done) /\ $property_state_valid(S_done)',
            r'$declaration_history_valid(S_done) /\ $heap_valid($heap_graph(S_done))']


def scope(state, owner, method):
    return [state + '.CURRENT = (pcallcontext_' + state.lower() + ')',
            'pcallcontext_' + state.lower() + '.TARGET = SCOPED_TARGET ' + owner + '.ORIGIN ' + method + '.FUNCTION.ORIGIN ' + owner + '.ORIGIN eps (KNOWN (PSTRING ' + owner + '.NAME))',
            'pcallcontext_' + state.lower() + '.LEXICAL_CLASS = (' + owner + '.ORIGIN)',
            'pcallcontext_' + state.lower() + '.CALLED_CLASS = (' + owner + '.ORIGIN)',
            '$call_current_valid(' + state + ')']


def instance(state, variable, name, origin):
    return ['$lookup($global_table_view(' + state + ').ENV,$ptascii("' + variable + '")) = (n_cell_' + name + ')',
            state + '.STORE[n_cell_' + name + '] = DEFINED (POBJECT n_' + name + ')',
            state + '.OBJECTS[n_' + name + '] = INSTANCE ' + origin]


def checks(row, fixture, filename):
    out = ['program_source = ' + fixture,
           'S_start = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
           r'S_start.COMPLETION = BUDGET /\ ~S_start.COMPILESTOP',
           '$source_unit(S_start.SOURCES,0) = (pcunit)',
           '$anonymous_compilation_unit(pcunit)',
           'S_start.OBJECTS = eps',
           '$declaration_history_valid(S_start)']
    if row['id'] == 'method-factory-static-defaults-root-counters-and-reuse':
        out += ['S_start.CLASSES = [pclassdesc_before,pclassdesc_child,pclassdesc_owner,pclassdesc_after]',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',S_start.CLASSES,eps,eps,0) = (3)',
                '$anonymous_class_name(' + term(filename) + ',2,0) = (pclassdesc_before.NAME)',
                '$anonymous_parent_class_name(pclassdesc_owner.NAME,' + term(filename) + ',5,1) = (pclassdesc_child.NAME)',
                '$anonymous_class_name(' + term(filename) + ',11,2) = (pclassdesc_after.NAME)',
                r'pclassdesc_owner.EARLY /\ ~pclassdesc_child.EARLY',
                'pclassdesc_child.PARENT = (pclassdesc_owner.NAME)',
                '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc)',
                'pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTCLASS pclassdesc_owner.NAME]))]',
                'S_first = $factory178_seek(S_start,$ptascii("make"),eps,3000)',
                r'$factory178_front(S_first,$ptascii("make"),eps) /\ S_first.COMPLETION = BUDGET',
                *scope('S_first','pclassdesc_owner','pmethoddesc'),
                '$lookup(S_first.ENV,$ptascii("value")) = (n_default)',
                'S_first.STORE[n_default] = DEFINED (PINT 3)',
                'S_first.ORIGIN = (porigin_new)',
                '$anonymous_new_pending(S_first,porigin_new) = (pclassdesc_child)',
                '~$anonymous_runtime_declaration(S_first.DECLARATIONS,pclassdesc_child.ORIGIN)',
                'S_link = $drive_steps(S_first[.COMPLETION = NORMAL],1)',
                r'S_link.COMPLETION = BUDGET /\ S_link.ORIGIN = S_first.ORIGIN',
                '$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_child.ORIGIN)',
                '$anonymous_new_name(S_link,porigin_new) = (pclassdesc_child.NAME)',
                '$declaration_history_valid(S_link)',
                'S_second = $factory178_seek(S_link,$ptascii("make"),$ptascii("first"),3000)',
                r'$factory178_front(S_second,$ptascii("make"),$ptascii("first")) /\ S_second.COMPLETION = BUDGET',
                *scope('S_second','pclassdesc_owner','pmethoddesc'),
                'S_second.ORIGIN = S_first.ORIGIN',
                '$lookup(S_second.ENV,$ptascii("value")) = (n_explicit)',
                'S_second.STORE[n_explicit] = DEFINED (PINT 8)',
                '$anonymous_new_name(S_second,porigin_new) = (pclassdesc_child.NAME)',
                'S_done = $drive_steps(S_second[.COMPLETION = NORMAL],8192)',
                *final_checks(row,filename),
                *instance('S_done','first','first','pclassdesc_child.ORIGIN'),
                *instance('S_done','second','second','pclassdesc_child.ORIGIN'),
                'n_first =/= n_second',
                '$anonymous_parent_class_name(pclassdesc_owner.NAME,' + term(filename) + ',5,2) = (ptbytes_wrong)',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',$trait_class_set(S_start.CLASSES,pclassdesc_child[.NAME = ptbytes_wrong]),eps,eps,0) = eps']
    elif row['id'] == 'method-factory-reversed-template-calls-and-counters':
        out += ['S_start.CLASSES = [pclassdesc_left,pclassdesc_right,pclassdesc_owner]',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',S_start.CLASSES,eps,eps,0) = (2)',
                '$anonymous_class_name(' + term(filename) + ',3,0) = (pclassdesc_left.NAME)',
                '$anonymous_class_name(' + term(filename) + ',4,1) = (pclassdesc_right.NAME)',
                '$method_named(pclassdesc_owner.METHODS,$ptascii("left")) = (pmethoddesc_left)',
                '$method_named(pclassdesc_owner.METHODS,$ptascii("right")) = (pmethoddesc_right)',
                'S_right = $factory178_seek(S_start,$ptascii("right"),eps,2000)',
                r'$factory178_front(S_right,$ptascii("right"),eps) /\ S_right.COMPLETION = BUDGET',
                *scope('S_right','pclassdesc_owner','pmethoddesc_right'),
                'S_right.ORIGIN = (porigin_right)',
                '$anonymous_new_name(S_right,porigin_right) = (pclassdesc_right.NAME)',
                'S_left = $factory178_seek(S_right,$ptascii("left"),eps,3000)',
                r'$factory178_front(S_left,$ptascii("left"),eps) /\ S_left.COMPLETION = BUDGET',
                *scope('S_left','pclassdesc_owner','pmethoddesc_left'),
                'S_left.ORIGIN = (porigin_left)',
                '$anonymous_new_name(S_left,porigin_left) = (pclassdesc_left.NAME)',
                'porigin_left =/= porigin_right',
                'S_again = $factory178_seek(S_left,$ptascii("right"),$ptascii("left"),3000)',
                r'$factory178_front(S_again,$ptascii("right"),$ptascii("left")) /\ S_again.COMPLETION = BUDGET',
                *scope('S_again','pclassdesc_owner','pmethoddesc_right'),
                'S_again.ORIGIN = (porigin_right)',
                'S_done = $drive_steps(S_again[.COMPLETION = NORMAL],8192)',
                *final_checks(row,filename),
                *instance('S_done','right','right','pclassdesc_right.ORIGIN'),
                *instance('S_done','left','left','pclassdesc_left.ORIGIN'),
                *instance('S_done','again','again','pclassdesc_right.ORIGIN'),
                r'n_right =/= n_left /\ n_right =/= n_again',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',[pclassdesc_right,pclassdesc_left,pclassdesc_owner],eps,eps,0) = eps']
    else:
        out += ['S_start.CLASSES = [pclassdesc_before,pclassdesc_child,pclassdesc_owner,pclassdesc_after]',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',S_start.CLASSES,eps,eps,0) = (4)',
                '$anonymous_class_name(' + term(filename) + ',2,0) = (pclassdesc_before.NAME)',
                '$anonymous_class_name(' + term(filename) + ',5,1) = (pclassdesc_child.NAME)',
                '$anonymous_class_name(' + term(filename) + ',8,3) = (pclassdesc_after.NAME)',
                r'~pclassdesc_owner.EARLY /\ pclassdesc_child.EARLY',
                '$class_named(S_start.CLASSNAMES,$ptlc(pclassdesc_owner.NAME)) = eps',
                '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc)',
                'S_first = $factory178_seek(S_start,$ptascii("make"),eps,3000)',
                r'$factory178_front(S_first,$ptascii("make"),eps) /\ S_first.COMPLETION = BUDGET',
                *scope('S_first','pclassdesc_owner','pmethoddesc'),
                '$class_named(S_first.CLASSNAMES,$ptlc(pclassdesc_owner.NAME)) = (pclassdesc_owner.ORIGIN)',
                '$anonymous_runtime_declaration(S_first.DECLARATIONS,pclassdesc_owner.ORIGIN)',
                '$declaration_history_valid(S_first)',
                'S_second = $factory178_seek(S_first,$ptascii("make"),$ptascii("first"),3000)',
                r'$factory178_front(S_second,$ptascii("make"),$ptascii("first")) /\ S_second.COMPLETION = BUDGET',
                'S_first.ORIGIN = S_second.ORIGIN',
                'S_done = $drive_steps(S_second[.COMPLETION = NORMAL],8192)',
                *final_checks(row,filename),
                *instance('S_done','first','first','pclassdesc_child.ORIGIN'),
                *instance('S_done','second','second','pclassdesc_child.ORIGIN'),
                'n_first =/= n_second',
                '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',$trait_class_set(S_start.CLASSES,pclassdesc_owner[.EARLY = true]),eps,eps,0) = eps']
    return out


def pure_checks(fixture, filename):
    """Source-derived local context queries, not a reached transient P state."""
    return ['P_complete = $ppstart(0,' + fixture + ',' + term(filename) + ')',
            r'P_complete.COMPLETION = PPCNORMAL /\ $ppimage_unit(P_complete)',
            'P_complete.CLASSES = [pclassdesc_before,pclassdesc_child,pclassdesc_owner,pclassdesc_after]',
            '$source_unit([P_complete.FOLD.SOURCE],0) = (pcunit)',
            '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
            'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
            'pclassdesc_child.ORIGIN = PORIGIN 0 pcpath_child',
            'pcpath_new = pcpath_child[0:$nabs($(|pcpath_child| - 1))]',
            '$origin_node([pcunit],pclassdesc_owner.ORIGIN) = (pcnode_owner)',
            '$plclasscontext(pcunit,pcpath_owner,' + term(filename) + ',pclassdesc_owner.LINE) = (ptcontext_owner)',
            '$anonymous_named_header(pcnode_owner,ptcontext_owner) = ((pchheader,z_owner))',
            'pchheader.NAME = pclassdesc_owner.NAME',
            '$origin_node([pcunit],pmethoddesc.FUNCTION.ORIGIN) = (NStmtClassMethod phpType14 phpType24 phpType4 phpType11 phpType16 phpType18 phpType47 metadata_method)',
            'ptcontext_method = $ppmethod_context(P_complete,pchheader,$ptascii("make"),$ppmethod_line(metadata_method))',
            'P_query = P_complete[.GOTOROOT = pcpath_method][.CLASSCONTEXT = (ptcontext_method)][.RETURNREF = false][.CLOSURE = false][.FOLD = P_complete.FOLD[.FUNCTION = pmethoddesc.FUNCTION.NAME][.CLASSCONTEXT = (ptcontext_method)][.CLOSURE = false][.CONSTANT = false][.DEFAULT = false]]',
            '$anonymous_factory_context(P_query,pcpath_new)',
            '~$anonymous_factory_context(P_complete,pcpath_new)',
            '~$anonymous_factory_context(P_query[.GOTOROOT = pcpath_owner],pcpath_new)',
            '~$anonymous_factory_context(P_query[.FOLD = P_query.FOLD[.FUNCTION = $ptascii("other")]],pcpath_new)',
            '~$anonymous_factory_context(P_query[.CLASSCONTEXT = eps],pcpath_new)',
            '~$anonymous_factory_context(P_query[.FOLD = P_query.FOLD[.CLASSCONTEXT = eps]],pcpath_new)',
            '~$anonymous_factory_context(P_query[.FOLD = P_query.FOLD[.CONSTANT = true]],pcpath_new)',
            '~$anonymous_factory_context(P_query[.FOLD = P_query.FOLD[.DEFAULT = true]],pcpath_new)',
            '~$anonymous_factory_context(P_query[.CLOSURE = true][.FOLD = P_query.FOLD[.CLOSURE = true]],pcpath_new)',
            'ptcontext_bad_namespace = ptcontext_method[.NAMESPACE = $ptascii("forged")]',
            'P_bad_namespace = P_query[.ENV = P_query.ENV[.NAMESPACE = $ptascii("forged")]][.CLASSCONTEXT = (ptcontext_bad_namespace)][.FOLD = P_query.FOLD[.CLASSCONTEXT = (ptcontext_bad_namespace)]]',
            '~$anonymous_factory_context(P_bad_namespace,pcpath_new)',
            'ptcontext_bad_import = ptcontext_method[.IMPORTS = [($ptascii("alias"),$ptascii("forged"))]]',
            'P_bad_import = P_query[.ENV = P_query.ENV[.CLASSES = ptcontext_bad_import.IMPORTS]][.CLASSCONTEXT = (ptcontext_bad_import)][.FOLD = P_query.FOLD[.CLASSCONTEXT = (ptcontext_bad_import)]]',
            '~$anonymous_factory_context(P_bad_import,pcpath_new)']


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    selected = ['method-factory-static-defaults-root-counters-and-reuse',
                'method-factory-reversed-template-calls-and-counters',
                'method-factory-conditional-owner-and-root-counters']
    rows = json.loads(CATALOGUE.read_text())['cases']
    raw = Path(tempfile.mkdtemp(prefix='anonymous-method-factories-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__),
               ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        code, counts, names = PREFIX, {}, []
        for index, name in enumerate(selected):
            row, = [r for r in rows if r['id'] == name]
            source = raw / (name + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            function = '$factory178_group' + str(index)
            code += 'dec ' + function + '() : bool\ndef ' + function + '() = true\n' + ''.join('  -- if ' + check + '\n' for check in conditions)
            counts[name] = len(conditions)
            names.append(function + '()')
            if index == 0:
                queries = pure_checks(checked['fixture'], os.fsencode(source))
                code += 'dec $factory178_pure() : bool\ndef $factory178_pure() = true\n' + ''.join('  -- if ' + query + '\n' for query in queries)
                counts['pure_source_derived_context_queries'] = len(queries)
                names.append('$factory178_pure()')
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + r' /\ '.join(names) + '\n')
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
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
        report['passed'] = report['passed'] and before == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()

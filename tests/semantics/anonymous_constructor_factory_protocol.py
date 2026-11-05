#!/usr/bin/env python3
"""Reached constructor factory counters and source-context refusals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker


ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_factory_cases.json'
SELECTED = ['ctor-early-counters-defaults-reuse', 'ctor-conditional-owner-deferred-counter']
TRACE_CASE = 'ctor-lazy-final-before-argument'
PREFIX = r'''
dec $ctor179_output_one(pevent) : ptbytes
def $ctor179_output_one(OUTPUT ptbytes) = ptbytes
def $ctor179_output_one(pevent) = eps -- otherwise
dec $ctor179_outputs(pevent*) : ptbytes
def $ctor179_outputs(eps) = eps
def $ctor179_outputs(pevent :: pevent_tail*) = $ctor179_output_one(pevent) ++ $ctor179_outputs(pevent_tail*)
dec $ctor179_trace_front(pstate) : bool
def $ctor179_trace_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__construct")
def $ctor179_trace_front(S) = false -- otherwise
dec $ctor179_trace_seek(pstate,nat) : pstate
def $ctor179_trace_seek(S,0) = S
def $ctor179_trace_seek(S,n) = S
  -- if $(n > 0) /\ $ctor179_trace_front(S)
def $ctor179_trace_seek(S,n) = $ctor179_trace_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$ctor179_trace_front(S) /\ (S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET)
def $ctor179_trace_seek(S,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def checks(row, fixture, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    conditional = row['id'] == SELECTED[1]
    child_line, after_line = (6, 11) if conditional else (5, 12)
    count, after_key = (4, 3) if conditional else (3, 2)
    out = ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
           r'S_start.COMPLETION = BUDGET /\ ~S_start.COMPILESTOP',
           '$source_unit(S_start.SOURCES,0) = (pcunit)',
           '$anonymous_compilation_unit(pcunit)',
           'S_start.CLASSES = [pclassdesc_before,pclassdesc_child,pclassdesc_owner,pclassdesc_after]',
           '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',S_start.CLASSES,eps,eps,0) = (' + str(count) + ')',
           '$anonymous_class_name(' + term(filename) + ',2,0) = (pclassdesc_before.NAME)',
           '$anonymous_class_name(' + term(filename) + ',' + str(child_line) + ',1) = (pclassdesc_child.NAME)',
           '$anonymous_class_name(' + term(filename) + ',' + str(after_line) + ',' + str(after_key) + ') = (pclassdesc_after.NAME)',
           '$method_named(pclassdesc_owner.METHODS,$ptascii("__construct")) = (pmethoddesc)',
           'pmethoddesc.OWNER = pclassdesc_owner.ORIGIN',
           'pmethoddesc.FUNCTION.NAME = pclassdesc_owner.NAME ++ $ptascii("::__construct")',
           'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
           'pclassdesc_child.ORIGIN = PORIGIN 0 pcpath_child',
           'pcpath_new = pcpath_child[0:$nabs($(|pcpath_child| - 1))]',
           '$origin_node(S_start.SOURCES,pmethoddesc.FUNCTION.ORIGIN) = (pcnode_method)',
           '$anonymous_method_factory_node(pcnode_method)',
           '$origin_node(S_start.SOURCES,PORIGIN 0 pcpath_new) = (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)',
           '$anonymous_new_descriptor(S_start,PORIGIN 0 pcpath_new) = (pclassdesc_child)',
           r'$class_state_valid(S_start) /\ $declaration_history_valid(S_start)',
           'S_done = $drive_steps(S_start[.COMPLETION = NORMAL],8192)',
           r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
           '$ctor179_outputs(S_done.EVENTS) = ' + term(expected),
           r'$class_state_valid(S_done) /\ $property_state_valid(S_done)',
           r'$declaration_history_valid(S_done) /\ $heap_valid($heap_graph(S_done))']
    if conditional:
        out += [r'~pclassdesc_owner.EARLY /\ pclassdesc_child.EARLY',
                '$class_named(S_start.CLASSNAMES,$ptlc(pclassdesc_owner.NAME)) = eps',
                '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_owner.NAME)) = (pclassdesc_owner.ORIGIN)']
    else:
        out += ['pclassdesc_owner.EARLY',
                '$class_named(S_start.CLASSNAMES,$ptlc(pclassdesc_owner.NAME)) = (pclassdesc_owner.ORIGIN)']
    out += ['$anonymous_class_name(' + term(filename) + ',' + str(child_line) + ',9) = (ptbytes_wrong)',
            '$anonymous_compiled_class_count(pcunit,' + term(filename) + ',$trait_class_set(S_start.CLASSES,pclassdesc_child[.NAME = ptbytes_wrong]),eps,eps,0) = eps',
            '$anonymous_new_descriptor(S_start[.CLASSES = $trait_class_set(S_start.CLASSES,pclassdesc_child[.NAME = ptbytes_wrong])],PORIGIN 0 pcpath_new) = eps']
    return out


def pure_checks(fixture, filename):
    return ['P_complete = $ppstart(0,' + fixture + ',' + term(filename) + ')',
            r'P_complete.COMPLETION = PPCNORMAL /\ $ppimage_unit(P_complete)',
            'P_complete.CLASSES = [pclassdesc_before,pclassdesc_child,pclassdesc_owner,pclassdesc_after]',
            '$source_unit([P_complete.FOLD.SOURCE],0) = (pcunit)',
            '$method_named(pclassdesc_owner.METHODS,$ptascii("__construct")) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
            'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
            'pclassdesc_child.ORIGIN = PORIGIN 0 pcpath_child',
            'pcpath_new = pcpath_child[0:$nabs($(|pcpath_child| - 1))]',
            '$origin_node([pcunit],pclassdesc_owner.ORIGIN) = (pcnode_owner)',
            '$plclasscontext(pcunit,pcpath_owner,' + term(filename) + ',pclassdesc_owner.LINE) = (ptcontext_owner)',
            '$anonymous_named_header(pcnode_owner,ptcontext_owner) = ((pchheader,z_owner))',
            '$origin_node([pcunit],pmethoddesc.FUNCTION.ORIGIN) = (NStmtClassMethod phpType14 phpType24 phpType4 phpType11 phpType16 phpType18 phpType47 metadata_method)',
            'ptcontext_method = $ppmethod_context(P_complete,pchheader,$ptascii("__construct"),$ppmethod_line(metadata_method))',
            'P_query = P_complete[.GOTOROOT = pcpath_method][.CLASSCONTEXT = (ptcontext_method)][.RETURNREF = false][.CLOSURE = false][.FOLD = P_complete.FOLD[.FUNCTION = pmethoddesc.FUNCTION.NAME][.CLASSCONTEXT = (ptcontext_method)][.CLOSURE = false][.CONSTANT = false][.DEFAULT = false]]',
            '$anonymous_factory_context(P_query,pcpath_new)',
            '~$anonymous_factory_context(P_query[.GOTOROOT = pcpath_owner],pcpath_new)',
            '~$anonymous_factory_context(P_query[.FOLD = P_query.FOLD[.FUNCTION = $ptascii("forged")]],pcpath_new)',
            '~$anonymous_factory_context(P_query[.CLASSCONTEXT = eps],pcpath_new)',
            '~$anonymous_factory_context(P_query[.FOLD = P_query.FOLD[.CLASSCONTEXT = eps]],pcpath_new)',
            '~$anonymous_factory_context(P_query[.FOLD = P_query.FOLD[.DEFAULT = true]],pcpath_new)']


def trace_checks(fixture, filename):
    return ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            r'S_start.COMPLETION = BUDGET /\ ~S_start.COMPILESTOP',
            'S_front = $ctor179_trace_seek(S_start,5000)',
            '$ctor179_trace_front(S_front)',
            'S_raw = S_front[.COMPLETION = NORMAL]',
            'S_raw.CURRENT = (pcallcontext)',
            '$trace_context_function(S_raw,pcallcontext) = $ptascii("__construct")',
            'PhpStep: S_raw ~> S_next',
            'S_next.COMPLETION = STATICBYTES $ptascii("Cannot override final method Ctor179FinalBase::value()") 8',
            '$eager_fatal_ready(S_raw,S_next.COMPLETION)',
            '|$eval_exception_trace(S_raw)| = 1',
            'S_next.TRACE = $eval_exception_trace(S_raw)',
            'S_eager = $eager_fatal_begin(S_raw,S_next)',
            'S_eager.COMPLETION = REQUESTFATAL $ptascii("CompileError") $ptascii("Cannot override final method Ctor179FinalBase::value()") 8']


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
    raw = Path(tempfile.mkdtemp(prefix='class179-protocol-', dir=ROOT / '.tools'))
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
        code, counts, groups = PREFIX, {}, []
        for index, name in enumerate(SELECTED):
            row = rows[name]
            source = raw / (name + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            group = '$ctor179_group' + str(index)
            code += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in conditions)
            counts[name] = len(conditions)
            groups.append(group + '()')
            if index == 0:
                queries = pure_checks(checked['fixture'], os.fsencode(source))
                code += 'dec $ctor179_pure() : bool\ndef $ctor179_pure() = true\n' + ''.join('  -- if ' + query + '\n' for query in queries)
                counts['pure_source_derived_context_queries'] = len(queries)
                groups.append('$ctor179_pure()')
        row = rows[TRACE_CASE]
        source = raw / (TRACE_CASE + '.php')
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256']
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        conditions = trace_checks(checked['fixture'], os.fsencode(source))
        code += 'dec $ctor179_trace_group() : bool\ndef $ctor179_trace_group() = true\n' + ''.join('  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n' for condition in conditions)
        counts[TRACE_CASE + '_reached_link'] = len(conditions)
        groups.append('$ctor179_trace_group()')
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + r' /\ '.join(groups) + '\n')
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 600, ROOT)
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

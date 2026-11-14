#!/usr/bin/env python3
"""Resolved scalar instanceof authenticates lexical class-name targets."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_scalar_resolved_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_scalar_qualified_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TRUTH, FALSE, ONE = prior.TRUTH, prior.FALSE, prior.ONE
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', TRUTH, 'StringReadAlias', 'PTPLAIN', 'stdClass'), FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', FALSE, 'StringReadPrefix\\Target', 'PTPLAIN', 'Missing\\Target'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', ('TERNARY', TRUTH, ('STRING', 'x', None), True), 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', ONE, 'stringreadprefix\\Target', 'PTPLAIN', 'Missing\\Deep\\Target'), FALSE, True), 'PINT 1'), ('COMPILED', 'PINT 2', ('ADD', 1, 1)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'INSTANCEOF':
        return base_value(checks, tag, tree)
    origin, expression, path = 'porigin_' + tag, 'expression_' + tag, 'pcpath_' + tag
    name, text = 'name_' + tag, 'text_' + tag
    requested = '$ptascii(' + json.dumps(tree[2]) + ')'
    target = '$ptascii(' + json.dumps(tree[4]) + ')'
    qualifier = tree[3]
    assert qualifier in ('PTPLAIN', 'PTFULL', 'PTRELATIVE')
    constructor = {'PTPLAIN': 'NName', 'PTFULL': 'NNameFullyQualified', 'PTRELATIVE': 'NNameRelative'}[qualifier]
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += [expression + ' = NExprInstanceof ' + expression + '_0 ' + name + ' metadata_' + tag,
               name + ' = ' + constructor + ' (BYTES ' + text + ') metadata_name_' + tag,
               '$ptast(' + name + ') = PTNAME ' + qualifier + ' (' + requested + ')',
               '$ptvalidname(' + requested + ', true)',
               '~($ptlc(' + requested + ') <- [$ptascii("self"), $ptascii("parent"), $ptascii("static")])',
               '$code_name(pcode_runtime.NAMES, ' + path + ') = ((' + target + ', eps))',
               '$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_' + tag + '_0)',
               '$origin_node(S.SOURCES, porigin_' + tag + '_0) = (' + expression + '_0)',
               '$origin_child((' + origin + '), [PCFIELD 1]) = (porigin_' + tag + '_name)',
               '$origin_node(S.SOURCES, porigin_' + tag + '_name) = (' + name + ')',
               'S.COMPLETION = NORMAL', 'S.CONSTCONTEXT = eps']
    context, environment, reference = 'ptcontext_' + tag, 'plenv_' + tag, 'pnreference_' + tag
    checks += ['$source_unit(S.SOURCES, 0) = (pcunit_' + tag + ')',
               '$plclasscontext(pcunit_' + tag + ', ' + path + ', $call_sourcefile(S.FILES, ' + origin + '), 5) = (' + context + ')',
               environment + ' = $plempty(false)[.NAMESPACE = ' + context + '.NAMESPACE][.CLASSES = ' + context + '.IMPORTS]',
               '$pnclassresolve(' + environment + ', ' + name + ') = PNRESOLVED ' + reference,
               reference + '.RESOLVED = (' + target + ')', reference + '.FALLBACK = eps']
    child = value(checks, tag + '_0', tree[1])[0]
    scalar = '[' + ', '.join('$ptascii(' + json.dumps(kind) + ')' for kind in ('null', 'bool', 'int', 'float')) + ']'
    resolved = 'S_instanceof_' + tag
    checks += ['~$pfcast_nan(' + child + ')',
               '$type_bytes(' + child + ') <- ' + scalar + r' \/ ($type_bytes(' + child + ') = $ptascii("string") /\\ $string_read_runtime_cast_quiet(CASTSTRING, ' + child + '))',
               resolved + ' = $resolve_at(S, KNOWN (' + child + '), 5)',
               resolved + ' = S[.RESULT = KNOWN (' + child + ')]',
               '$class_instanceof(' + resolved + ', ' + child + ', ' + target + ') = false',
               '$string_read_runtime_value(S, ' + origin + ') = (PBOOL false)',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(PBOOL false))']
    return 'PBOOL false', '0'


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES
conditions = prior.conditions


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Quiet nonNaN scalar named instanceof admits genuine lexical namespace/import/relative resolution through canonical whole-source plclasscontext, current nonempty source-file metadata and positive emitted line, unchanged pnclassresolve and exact CODE.NAMES target without fallback. Existing raw-identity PTPLAIN/PTFULL authority stays pointwise unchanged; mismatching PTPLAIN and PTRELATIVE use disjoint lexical authority. Exact root/both-child source, precision, NORMAL/CONSTCONTEXTeps, recursive scalar or quiet canonical nonNUL INTERNED value and whole resolve_at/class_instanceof state preserve REQUEST keys1/-1/0/-4 and Warning/Throwable/bounds/cleanup/budget histories. New lexical proof refuses noncanonical source, absent file metadata and mismatching resolved targets; the existing compiler-output trust boundary of raw-name equality remains. Keywords, dynamic names, owning values, NaN and wider contexts remain outside; no126/127/compiler/formatter/owner or held-boundary changes. Native originals reused once, fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)

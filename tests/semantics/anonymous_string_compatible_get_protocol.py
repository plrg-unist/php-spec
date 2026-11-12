#!/usr/bin/env python3
"""Check actual anonymous wider-Get contexts and unchanged factory bounds in SL."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_string_compatible_get_cases.json')
row = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def parameter(type_term, byref='false', variadic='false', default='ABSENT'):
    return ('SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (' + type_term +
            ') (BOOLEAN ' + byref + ') (BOOLEAN ' + variadic +
            ') (NExprVariable (BYTES text_parameter_union) metadata_name_union) (' +
            default + ') (SEQUENCE eps) metadata_parameter_union])')


def method(parameters, byref='false', returns='ABSENT', flags='1',
           body='statement_body_union*'):
    return ('NStmtClassMethod (SEQUENCE eps) (INTEGER ' + flags + ') (BOOLEAN ' +
            byref + ') (NIdentifier (BYTES text_method_union) metadata_method_name_union) (' +
            parameters + ') (' + returns + ') (SEQUENCE ' + body + ') metadata_method_union')


def render(case, fixture, filename):
    shape = '$ptascii("Vendor") ++ [92] ++ $ptascii("Shape")'
    checks = [
        'S = $php_run(' + fixture + ',0,' + filename + ')',
        'S.COMPLETION = BUDGET /\\ ~S.COMPILESTOP',
        '$source_unit(S.SOURCES,0) = (pcunit)',
        '$anonymous_unit(pcunit)',
        'S.EVENTS = eps /\\ S.ALLOCATIONS = eps',
        '$class_state_valid(S) /\\ $call_descriptors_valid(S) /\\ $declaration_history_valid(S)',
    ]
    for tag, statement, line, counter, expected in [
        ('nullable', 2, 5, 0, '[(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))]'),
        ('union', 4, 10, 1, '[(PTBRANCH ([PTCLASS (' + shape + ')])),(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"]))]'),
        ('mixed', 6, 15, 2, '[(PTBRANCH ([PTBUILTIN "mixed"]))]'),
    ]:
        v = lambda name: name + '_' + tag
        path, owner, raw_method, params, raw, owner_desc, function, param, context = (
            v(name) for name in ('pcpath', 'statement_owner', 'statement_method', 'phpType16',
                                'phpType18', 'pclassdesc', 'pfunction', 'psparam', 'ptcontext'))
        checks += [
            path + ' = [PCINDEX 0,PCFIELD 1,PCINDEX ' + str(statement) + ',PCFIELD 0,PCFIELD 1,PCFIELD 0]',
            '$origin_node(S.SOURCES,PORIGIN 0 ' + path + ') = (' + owner + ')',
            owner + ' = NStmtClass (SEQUENCE eps) (INTEGER 0) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE ' + v('statement_member') + '*) ' + v('metadata_owner'),
            '$anonymous_class_node(' + owner + ') /\\ ~$anonymous_owner_factory_node(' + owner + ')',
            '$class_at(S.CLASSES,PORIGIN 0 ' + path + ') = (' + owner_desc + ')',
            '$anonymous_class_name($base64(' + filename + '),' + str(line) + ',' + str(counter) + ') = (' + owner_desc + '.NAME)',
            owner_desc + '.PARENT = eps /\\ ' + owner_desc + '.EARLY /\\ ' + owner_desc + '.LINE = ' + str(line),
            '$method_named(' + owner_desc + '.METHODS,$ptascii("__get")) = (' + v('pmethoddesc') + ')',
            v('pmethoddesc') + '.OWNER = ' + owner_desc + '.ORIGIN',
            function + ' = ' + v('pmethoddesc') + '.FUNCTION',
            function + '.ORIGIN = PORIGIN 0 (' + path + ' ++ [PCFIELD 5,PCINDEX 1])',
            function + '.ENV.NAMESPACE = $ptascii("WiderAnon")',
            '$ptimport(' + function + '.ENV.CLASSES,$ptascii("Imported")) = (' + shape + ')',
            v('statement_member') + '*[1] = ' + raw_method,
            raw_method + ' = NStmtClassMethod (SEQUENCE eps) (INTEGER 1) (BOOLEAN false) (NIdentifier (BYTES ' + v('text_method') + ') ' + v('metadata_method_name') + ') ' + params + ' ABSENT (SEQUENCE ' + v('statement_body') + '*) ' + v('metadata_method'),
            params + ' = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES ' + v('text_parameter') + ') ' + v('metadata_name') + ') ABSENT (SEQUENCE eps) ' + v('metadata_parameter') + '])',
            function + '.SIGNATURE.PARAMETERS = [' + param + ']',
            param + '.TYPE = ' + expected + ' /\\ ' + param + '.NAME = $base64(' + v('text_parameter') + ')',
            context + ' = {NAMESPACE ' + function + '.ENV.NAMESPACE, IMPORTS ' + function + '.ENV.CLASSES, SCOPE PTKNOWN ' + owner_desc + '.NAME eps, POSITION PTPARAMETER, OWNER ' + owner_desc + '.NAME, MEMBER ' + v('pmethoddesc') + '.NAME, FILE $call_sourcefile(S.FILES,' + function + '.ORIGIN), LINE $psline(' + v('metadata_parameter') + ')}',
            '$ptype_normalize(' + raw + ',' + context + ') = PTOK ' + param + '.TYPE eps',
            '$property_empty_get_source(S,' + v('pmethoddesc') + ')',
            '$ppmethod_get_declaration_signature(' + function + '.SIGNATURE) /\\ ~$ppmethod_get_signature(' + function + '.SIGNATURE)',
            '$typed_conversion(' + param + '.TYPE,PSTRING ($ptascii("12")),false) = TYPEVALUE (PSTRING ($ptascii("12")))',
            '$anonymous_get_name_syntax(' + raw + ') /\\ $anonymous_member(' + raw_method + ')',
            '~$anonymous_get_factory_parameters(' + params + ') /\\ ~$anonymous_method_factory_node(' + raw_method + ')',
            '$anonymous_no_classes($pcwalk($pcchildren(' + raw_method + ',eps)))',
        ]
    checks += [
        '~$property_empty_get_name_type_at(phpType18_union,psparam_union.TYPE,ptcontext_union[.IMPORTS = eps])',
        '$anonymous_get_name_syntax(NIdentifier (BYTES "U1RSSU5H") eps)',
        '~$anonymous_get_name_syntax(ABSENT)',
        '~$anonymous_get_name_syntax(NUnionType (SEQUENCE eps) eps)',
        '~$anonymous_get_name_syntax(NUnionType (SEQUENCE ([NIdentifier (BYTES "c3RyaW5n") eps])) eps)',
        '~$anonymous_get_name_syntax(NIdentifier (BYTES "Ym9vbA==") eps)',
        '~$ppmethod_get_declaration_signature(pfunction_union.SIGNATURE[.PARAMETERS = [psparam_union[.TYPE = [(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"]))]]]])',
        '$anonymous_member(' + method(parameter('ABSENT')) + ')',
        '$anonymous_member(' + method(parameter('NIdentifier (BYTES "c3RyaW5n") eps')) + ')',
    ]
    for params in [
        parameter('phpType18_union', byref='true'),
        parameter('phpType18_union', variadic='true'),
        parameter('phpType18_union', default='NScalarString (BYTES "eA==") eps'),
    ]:
        checks.append('~$anonymous_member(' + method(params) + ')')
    checks += [
        '~$anonymous_member(' + method('phpType16_union', byref='true') + ')',
        '~$anonymous_member(' + method('phpType16_union', returns='NIdentifier (BYTES "aW50") eps') + ')',
        '~$anonymous_member(' + method('phpType16_union', flags='9') + ')',
        'statement_child = NStmtExpression (NExprNew (NStmtClass (SEQUENCE eps) (INTEGER 0) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE eps) metadata_owner_union) (SEQUENCE eps) eps) eps',
        'statement_factory = ' + method('phpType16_union', body='([statement_child])'),
        '$anonymous_member(statement_factory) /\\ ~$anonymous_no_classes($pcwalk($pcchildren(statement_factory,eps)))',
        '~$anonymous_method_factory_node(statement_factory)',
        'statement_factory_owner = NStmtClass (SEQUENCE eps) (INTEGER 0) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE ([statement_factory])) metadata_owner_union',
        '~$anonymous_owner_factory_node(statement_factory_owner) /\\ ~$anonymous_unit_node(statement_factory_owner)',
        '$heap_valid($heap_graph(S))',
    ]
    return ('dec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + check + '\n' for check in checks), len(checks))


if __name__ == '__main__':
    protocol.run({'anonymous-wider-get-actual-contexts': {'source': row['source']}},
                 (Path(__file__), CATALOGUE), fixture_renderer=render,
                 runner_flags=('--sl',))

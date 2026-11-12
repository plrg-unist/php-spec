#!/usr/bin/env python3
"""Check anonymous typed-Get compilation and retained header/factory bounds in SL."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_typed_get_member_cases.json')
row = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def parameter(type_term, byref='false', variadic='false', default='ABSENT'):
    return ('SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (' + type_term +
            ') (BOOLEAN ' + byref + ') (BOOLEAN ' + variadic +
            ') (NExprVariable (BYTES text_parameter) metadata_parameter_name) ' +
            '(' + default + ') (SEQUENCE eps) metadata_parameter])')


def method(parameters, byref='false', returns='ABSENT', flags='flags', body='statement_body*'):
    return ('NStmtClassMethod (SEQUENCE eps) (INTEGER ' + flags + ') (BOOLEAN ' +
            byref + ') (NIdentifier (BYTES text_method) metadata_method_name) (' +
            parameters + ') (' + returns + ') (SEQUENCE ' + body + ') metadata_method')


def render(case, fixture, filename):
    typed = 'NIdentifier (BYTES text_type) metadata_type'
    checks = [
        'program_source = ' + fixture,
        'pcunit = $pcsource(0,program_source)',
        'pcpath_class = [PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 0]',
        '$origin_node([pcunit],PORIGIN 0 pcpath_class) = (statement_owner)',
        'statement_owner = NStmtClass (SEQUENCE eps) (INTEGER 0) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement_member*) metadata_class',
        '$(|statement_member*| > 2)',
        'statement_member*[2] = statement_method',
        'statement_method = NStmtClassMethod (SEQUENCE eps) (INTEGER flags) (BOOLEAN false) (NIdentifier (BYTES text_method) metadata_method_name) phpType16 ABSENT (SEQUENCE statement_body*) metadata_method',
        'flags = 1 /\\ $ppmethod_get(flags,$base64(text_method))',
        'phpType16 = ' + parameter(typed),
        '$ptlc($base64(text_type)) = $ptascii("string") /\\ $ptvalidname($base64(text_parameter),false)',
        '$anonymous_member(statement_method) /\\ $anonymous_constructor_parameters(phpType16)',
        '~$anonymous_get_factory_parameters(phpType16)',
        '~$anonymous_magic_factory(flags,false,$base64(text_method),phpType16,ABSENT,statement_body*)',
        '~$anonymous_method_factory_node(statement_method)',
        '$anonymous_no_classes($pcwalk($pcchildren(statement_method,eps)))',
        '$anonymous_members(statement_member*) /\\ $anonymous_class_node(statement_owner)',
        '$anonymous_unit_node(statement_owner) /\\ $anonymous_unit(pcunit)',
        'S = $php_run(program_source,0,' + filename + ')',
        'S.COMPLETION = BUDGET /\\ ~S.COMPILESTOP',
        '$source_unit(S.SOURCES,0) = (pcunit)',
        '$class_at(S.CLASSES,PORIGIN 0 pcpath_class) = (pclassdesc)',
        'pclassdesc.LINE = 3 /\\ pclassdesc.PARENT = eps /\\ pclassdesc.EARLY',
        '$anonymous_class_name($base64(' + filename + '),3,0) = (pclassdesc.NAME)',
        '$method_named(pclassdesc.METHODS,$ptascii("__get")) = (pmethoddesc)',
        'pmethoddesc.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 (pcpath_class ++ [PCFIELD 5,PCINDEX 2])',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam]',
        'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ psparam.NAME = $base64(text_parameter)',
        '$ppmethod_get_declaration_signature(pmethoddesc.FUNCTION.SIGNATURE) /\\ ~$ppmethod_get_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        '$property_empty_get_source(S,pmethoddesc)',
        'S.EVENTS = eps /\\ S.ALLOCATIONS = eps',
        '$class_state_valid(S) /\\ $call_descriptors_valid(S) /\\ $declaration_history_valid(S)',
        '$heap_valid($heap_graph(S))',
        'phpType16_untyped = ' + parameter('ABSENT'),
        '$anonymous_get_factory_parameters(phpType16_untyped)',
        '$anonymous_member(' + method('phpType16_untyped') + ')',
    ]
    for parameters in [
        parameter('NNullableType (' + typed + ') metadata_type'),
        parameter('NIdentifier (BYTES "bWl4ZWQ=") metadata_type'),
        parameter(typed, byref='true'),
        parameter(typed, variadic='true'),
        parameter(typed, default='NScalarString (BYTES "eA==") eps'),
    ]:
        checks.append('~$anonymous_member(' + method(parameters) + ')')
    checks += [
        '~$anonymous_member(' + method('phpType16', byref='true') + ')',
        '~$anonymous_member(' + method('phpType16', returns='NIdentifier (BYTES text_type) metadata_type') + ')',
        '~$anonymous_member(' + method('phpType16', flags='9') + ')',
        'statement_child = NStmtExpression (NExprNew (NStmtClass (SEQUENCE eps) (INTEGER 0) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE statement_member*) metadata_class) (SEQUENCE eps) eps) eps',
        'statement_factory = ' + method('phpType16', body='([statement_child])'),
        '$anonymous_member(statement_factory)',
        '~$anonymous_no_classes($pcwalk($pcchildren(statement_factory,eps)))',
        '~$anonymous_method_factory_node(statement_factory)',
        '~$anonymous_owner_factory_members([statement_factory])',
        'statement_factory_owner = NStmtClass (SEQUENCE eps) (INTEGER 0) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE ([statement_factory])) metadata_class',
        '~$anonymous_owner_factory_node(statement_factory_owner) /\\ ~$anonymous_unit_node(statement_factory_owner)',
    ]
    return ('dec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + check + '\n' for check in checks), len(checks))


if __name__ == '__main__':
    protocol.run({'anonymous-typed-get-member-compiler': {'source': row['source']}},
                 (Path(__file__), CATALOGUE), fixture_renderer=render,
                 runner_flags=('--sl',))

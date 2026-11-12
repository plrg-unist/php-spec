#!/usr/bin/env python3
"""Check real wider Get types and retained syntax/enum guards in fixture SL."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_string_compatible_get_cases.json')
row = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def render(case, fixture, filename):
    checks = [
        'S = $php_run(' + fixture + ',0,' + filename + ')',
        'S.COMPLETION = BUDGET /\\ ~S.COMPILESTOP',
        'S.EVENTS = eps /\\ S.ALLOCATIONS = eps',
        '$class_state_valid(S) /\\ $call_descriptors_valid(S) /\\ $declaration_history_valid(S)',
    ]
    for tag, index, owner, expected, forged in [
        ('nullable', 1, 'NullableNameGet',
         '[(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))]',
         '[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"]))]'),
        ('union', 2, 'UnionNameGet',
         '[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"]))]',
         '[(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))]'),
        ('mixed', 3, 'MixedNameGet',
         '[(PTBRANCH ([PTBUILTIN "mixed"]))]',
         '[(PTBRANCH ([PTBUILTIN "string"]))]'),
    ]:
        v = lambda name: name + '_' + tag
        origin = 'PORIGIN 0 ([PCINDEX ' + str(index) + '])'
        owner_desc, method, function, parameter, raw, context, signature = (
            v(name) for name in ('pclassdesc', 'pmethoddesc', 'pfunction', 'psparam',
                                'phpType18', 'ptcontext', 'pssignature'))
        checks += [
            '$class_at(S.CLASSES,' + origin + ') = (' + owner_desc + ')',
            owner_desc + '.NAME = $ptascii("' + owner + '") /\\ ' + owner_desc + '.KIND = "class" /\\ ' + owner_desc + '.PARENT = eps',
            '$method_named(' + owner_desc + '.METHODS,$ptascii("__get")) = (' + method + ')',
            method + '.OWNER = ' + owner_desc + '.ORIGIN',
            function + ' = ' + method + '.FUNCTION',
            function + '.ORIGIN = PORIGIN 0 ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 2])',
            function + '.SIGNATURE.PARAMETERS = [' + parameter + ']',
            parameter + '.NAME = $ptascii("incoming") /\\ ' + parameter + '.TYPE = ' + expected,
            '~' + parameter + '.BYREF /\\ ~' + parameter + '.VARIADIC /\\ ' + parameter + '.REQUIRED /\\ ' + parameter + '.DEFAULT = PSNONE',
            function + '.SIGNATURE.RETURNS = eps /\\ ~' + function + '.SIGNATURE.BYREF',
            '$origin_node(S.SOURCES,PORIGIN 0 ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 2,PCFIELD 4,PCINDEX 0])) = (NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES ' + v('text_parameter') + ') ' + v('metadata_name') + ') ABSENT (SEQUENCE eps) ' + v('metadata_parameter') + ')',
            '$base64(' + v('text_parameter') + ') = ' + parameter + '.NAME',
            context + ' = {NAMESPACE ' + function + '.ENV.NAMESPACE, IMPORTS ' + function + '.ENV.CLASSES, SCOPE PTKNOWN ' + owner_desc + '.NAME eps, POSITION PTPARAMETER, OWNER ' + owner_desc + '.NAME, MEMBER ' + method + '.NAME, FILE $call_sourcefile(S.FILES,' + function + '.ORIGIN), LINE $psline(' + v('metadata_parameter') + ')}',
            '$ptype_normalize(' + raw + ',' + context + ') = PTOK ' + parameter + '.TYPE eps',
            '$property_empty_get_name_type_at(' + raw + ',' + parameter + '.TYPE,' + context + ')',
            '~$property_empty_get_name_type(' + raw + ',' + parameter + '.TYPE)',
            '$ppmethod_get_declaration_signature(' + function + '.SIGNATURE) /\\ ~$ppmethod_get_signature(' + function + '.SIGNATURE)',
            '$property_empty_get_source(S,' + method + ')',
            '$typed_exact(' + parameter + '.TYPE,PSTRING ($ptascii("12")))',
            '$typed_conversion(' + parameter + '.TYPE,PSTRING ($ptascii("12")),false) = TYPEVALUE (PSTRING ($ptascii("12")))',
            signature + ' = ' + function + '.SIGNATURE[.PARAMETERS = [' + parameter + '[.TYPE = ' + forged + ']]]',
            '$ppmethod_get_declaration_signature(' + signature + ') /\\ $typed_exact(' + forged + ',PSTRING ($ptascii("12")))',
            '~$property_empty_get_name_type_at(' + raw + ',' + forged + ',' + context + ')',
            'pclassdesc_enum_' + tag + ' = ' + owner_desc + '[.KIND = "enum"][.PROPERTIES = eps][.METHODS = [' + method + ']]',
            'S_enum_' + tag + ' = S[.CLASSES = [pclassdesc_enum_' + tag + ']]',
            '$enum_forbidden(S_enum_' + tag + ',pclassdesc_enum_' + tag + ',$enum_forbidden_names()) = ($ptascii("__get"))',
            '$enum_class_verify(S_enum_' + tag + ',pclassdesc_enum_' + tag + ') = METHOD_ISSUE ($ptascii("Enum ' + owner + ' cannot include magic method __get")) pclassdesc_enum_' + tag + '.LINE',
        ]
    checks += [
        '$property_empty_get_name_type_at(ABSENT,eps,ptcontext_nullable)',
        '$property_empty_get_name_type_at(NIdentifier (BYTES "U1RSSU5H") eps,[(PTBRANCH ([PTBUILTIN "string"]))],ptcontext_nullable)',
        '~$property_empty_get_name_type_at(ABSENT,psparam_nullable.TYPE,ptcontext_nullable)',
        '~$property_empty_get_name_type_at(NIdentifier (BYTES "c3RyaW5n") eps,eps,ptcontext_nullable)',
        '~$property_empty_get_name_type_at(NIdentifier (BYTES "Ym9vbA==") eps,[(PTBRANCH ([PTBUILTIN "bool"]))],ptcontext_nullable)',
        '~$ppmethod_get_declaration_signature(pfunction_nullable.SIGNATURE[.PARAMETERS = [psparam_nullable[.TYPE = [(PTBRANCH ([PTBUILTIN "bool"]))]]]])',
        'phpType18_empty = NUnionType (SEQUENCE eps) eps',
        '~$property_empty_get_wider_name_syntax(phpType18_empty)',
        '~$property_empty_get_name_type_at(phpType18_empty,eps,ptcontext_nullable)',
        'phpType18_single = NUnionType (SEQUENCE ([NIdentifier (BYTES "c3RyaW5n") eps])) eps',
        '~$property_empty_get_wider_name_syntax(phpType18_single)',
        '~$property_empty_get_name_type_at(phpType18_single,[(PTBRANCH ([PTBUILTIN "string"]))],ptcontext_nullable)',
        '$heap_valid($heap_graph(S))',
    ]
    return ('dec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + check + '\n' for check in checks), len(checks))


if __name__ == '__main__':
    protocol.run({'string-compatible-get-compiled-types': {'source': row['source']}},
                 (Path(__file__), CATALOGUE), fixture_renderer=render,
                 runner_flags=('--sl',))

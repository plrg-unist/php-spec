#!/usr/bin/env python3
"""Authenticate signed FLOAT ASTs without folding payloads or widening types."""
import base64
import json

import supplied_optional_float_default_producer_reference_notice_review_state as literal_review
import supplied_optional_unary_float_int_default_producer_reference_notice_review_state as promoted_review
import supplied_optional_unary_float_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    lines = ['S_return.DEFAULTCACHE = eps',
        '~$reference_notice_producer_arguments(phpType6_producer, phpType16_producer, pfunction_producer.SIGNATURE)']
    if case['kind'] != 'singleton':
        return lines
    encoded = lambda text: json.dumps(base64.b64encode(text.encode()).decode())
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    normalized = lambda name: '[(PTBRANCH ([PTBUILTIN ' + json.dumps(name) + ']))]'

    def floating(bits='401e000000000000', metadata='eps'):
        return 'NScalarFloat (FLOAT ' + json.dumps(bits) + ') (' + metadata + ')'

    def signed(sign='Minus', bits='401e000000000000', leaf_metadata='eps', metadata='eps'):
        return 'NExprUnary' + sign + ' (' + floating(bits, leaf_metadata) + ') (' + metadata + ')'

    def raw(default=None, raw_type='ABSENT', byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') (' + raw_type
            + ') (BOOLEAN ' + byref + ') (BOOLEAN ' + variadic
            + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (signed() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, kind='float', checked_type='eps', byref='false', variadic='false', required='false'):
        default = '(PSDEFAULT (' + signed() + ') ' + json.dumps(kind) + ')' if default is None else default
        return ('psparam[.NAME = $ptascii("peer")][.TYPE = ' + checked_type
            + '][.BYREF = ' + byref + '][.VARIADIC = ' + variadic
            + '][.REQUIRED = ' + required + '][.DEFAULT = ' + default + ']')

    def argument(name='x', named='ABSENT', unpack='false'):
        return 'NArg ' + named + ' (NExprVariable (BYTES ' + encoded(name) + ') eps) (BOOLEAN ' + unpack + ') (BOOLEAN false) eps'

    def proof(raws=None, parameters=None, actuals=None):
        raws = [raw()] if raws is None else raws
        parameters = [parameter()] if parameters is None else parameters
        actuals = [argument()] if actuals is None else actuals
        signature = 'pfunction_producer.SIGNATURE[.PARAMETERS = [' + ', '.join(parameters) + ']][.RETURNS = eps][.BYREF = false]'
        return ('$reference_notice_producer_arguments(SEQUENCE ([' + ', '.join(actuals)
            + ']), SEQUENCE ([' + ', '.join(raws) + ']), ' + signature + ')')

    # Execute just the three changed pure queries at this fresh source cut.
    for previous, count in ((literal_review, 1), (promoted_review, 2)):
        affected = [line for line in previous.independent_controls(case)
            if 'NExprUnary' in line and 'NScalarFloat' in line]
        assert len(affected) == count and all(not line.startswith('~') for line in affected)
        lines += affected
    for sign in ('Plus', 'Minus'):
        for bits in ('401e000000000000', '0000000000000000', '8000000000000000', '0000000000000001', '7fefffffffffffff'):
            default = signed(sign, bits)
            for raw_type, checked_type in (('ABSENT', 'eps'), (typename('FLoAt'), normalized('float'))):
                for byref in ('false', 'true'):
                    lines.append(proof([raw(default, raw_type, byref)],
                        [parameter('(PSDEFAULT (' + default + ') "float")', checked_type=checked_type, byref=byref)]))
    exact = signed(leaf_metadata='[MstartLine 7]', metadata='[MstartLine 8]')
    lines.append(proof([raw(exact)], [parameter('(PSDEFAULT (' + exact + ') "float")')]))
    for default in (signed('Plus'), signed('Plus', 'c01e000000000000'), floating('c01e000000000000'),
            signed(bits='401e000000000001'), signed(leaf_metadata='[MstartLine 7]'), signed(metadata='[MstartLine 8]')):
        lines.append('~' + proof(parameters=[parameter('(PSDEFAULT (' + default + ') "float")')]))
    for kind in ('int', 'string', 'bool', 'null', 'deferred', 'FLOAT'):
        lines.append('~' + proof(parameters=[parameter(kind=kind)]))
    for default in ('PSNONE', 'PSDEFAULTUNSUPPORTED "unproved unary FLOAT"'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    for default in ('NExprUnaryPlus (' + signed() + ') eps',
            'NExprUnaryMinus (' + signed('Plus') + ') eps',
            'NExprUnaryPlus (NScalarString (BYTES "Ny41") eps) eps',
            'NExprUnaryMinus (NExprConstFetch (NName (BYTES "c2V2ZW4=") eps) eps) eps'):
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "float")')]))
    for name in ('int', 'bool', 'string', 'mixed', 'array', 'callable'):
        lines.append('~' + proof([raw(raw_type=typename(name))], [parameter(checked_type=normalized(name))]))
    for tag in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        lines.append('~' + proof([raw(raw_type=tag + ' (BYTES "ZmxvYXQ=") eps')], [parameter(checked_type=normalized('float'))]))
    for raw_type, checked_type in (
            ('NNullableType (' + typename('float') + ') eps', '[(PTBRANCH ([PTBUILTIN "float"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NUnionType (SEQUENCE ([' + typename('float') + ', ' + typename('int') + '])) eps', '[(PTBRANCH ([PTBUILTIN "float"])), (PTBRANCH ([PTBUILTIN "int"]))]')):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(checked_type=checked_type)]))
    lines += ['~' + proof([raw(raw_type=typename('float\x00'))], [parameter(checked_type=normalized('float'))]),
        '~' + proof(parameters=[parameter(checked_type=normalized('float'))]),
        '~' + proof([raw(raw_type=typename('float'))])]
    for sign in ('Plus', 'Minus'):
        default = 'NExprUnary' + sign + ' (NScalarInt (INTEGER 7) eps) eps'
        checked = '(PSDEFAULT (' + default + ') "float")'
        lines += [proof([raw(default, typename('float'))], [parameter(checked, checked_type=normalized('float'))]),
            '~' + proof([raw(default)], [parameter(checked)])]
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for actuals in ([argument('http_response_header')], [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')],
            [argument(unpack='true')], [argument(), argument()]):
        lines.append('~' + proof(actuals=actuals))
    required_raw, required = raw('ABSENT', typename('int')), parameter('PSNONE', checked_type=normalized('int'), required='true')
    lines += [proof([required_raw, raw()], [required, parameter()], [argument()] * 2),
        proof([raw(), raw()], [parameter(), parameter()], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, raw()], [required, parameter()]),
        '~' + proof(raws=[]), '~' + proof(parameters=[]), proof(actuals=[])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

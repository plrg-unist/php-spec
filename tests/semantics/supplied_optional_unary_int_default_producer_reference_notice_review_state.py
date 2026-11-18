#!/usr/bin/env python3
"""Distinguish exact signed defaults from folded values and wider numeric ASTs."""
import base64
import json

import supplied_optional_unary_int_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    lines = ['S_return.DEFAULTCACHE = eps',
        '$call_target(S_full, pfunction_producer.NAME, eps) = (pfunction_survived)',
        'pfunction_survived.SIGNATURE = pfunction_producer.SIGNATURE']
    if case['kind'] != 'singleton':
        return lines
    encoded = lambda text: json.dumps(base64.b64encode(text.encode()).decode())
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    normalized = lambda name: '[(PTBRANCH ([PTBUILTIN ' + json.dumps(name) + ']))]'

    def integer(value, metadata='eps'):
        value = '$(' + str(value) + ')' if value < 0 else str(value)
        return 'NScalarInt (INTEGER ' + value + ') (' + metadata + ')'

    def signed(sign='Minus', value=7, leaf_metadata='eps', metadata='eps'):
        return 'NExprUnary' + sign + ' (' + integer(value, leaf_metadata) + ') (' + metadata + ')'

    def raw(default=None, raw_type='ABSENT', byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') (' + raw_type
            + ') (BOOLEAN ' + byref + ') (BOOLEAN ' + variadic
            + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (signed() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, kind='int', checked_type='eps', byref='false', variadic='false', required='false'):
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

    for sign, values in (('Plus', (-9223372036854775808, -1, 0, 7, 9223372036854775807)),
            ('Minus', (-9223372036854775807, -1, 0, 7, 9223372036854775807))):
        for value in values:
            default = signed(sign, value)
            for raw_type, checked_type in (('ABSENT', 'eps'), (typename('InT'), normalized('int'))):
                for byref in ('false', 'true'):
                    lines.append(proof([raw(default, raw_type, byref)],
                        [parameter('(PSDEFAULT (' + default + ') "int")', checked_type=checked_type, byref=byref)]))
    for sign in ('Plus', 'Minus'):
        for value in (-9223372036854775809, 9223372036854775808):
            default = signed(sign, value)
            lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "int")')]))
    minimum_negation = signed('Minus', -9223372036854775808)
    lines.append('~' + proof([raw(minimum_negation)], [parameter('(PSDEFAULT (' + minimum_negation + ') "int")')]))
    exact = signed(leaf_metadata='[MstartLine 7]', metadata='[MstartLine 8]')
    lines.append(proof([raw(exact)], [parameter('(PSDEFAULT (' + exact + ') "int")')]))
    for default in (signed('Plus'), signed('Plus', -7), signed(value=8), integer(-7),
            signed(leaf_metadata='[MstartLine 7]'), signed(metadata='[MstartLine 8]')):
        lines.append('~' + proof(parameters=[parameter('(PSDEFAULT (' + default + ') "int")')]))
    for kind in ('float', 'string', 'bool', 'deferred', 'INT'):
        lines.append('~' + proof(parameters=[parameter(kind=kind)]))
    for default in ('PSNONE', 'PSDEFAULTUNSUPPORTED "unproved signed default"'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    for default in ('NExprUnaryPlus (' + signed() + ') eps',
            'NExprUnaryMinus (' + signed('Plus') + ') eps',
            'NExprUnaryMinus (NScalarFloat (FLOAT "401c000000000000") eps) eps',
            'NExprUnaryPlus (NScalarString (BYTES "Nw==") eps) eps',
            'NExprUnaryMinus (NExprConstFetch (NName (BYTES "c2V2ZW4=") eps) eps) eps'):
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "int")')]))
    for name in ('float', 'bool', 'string', 'mixed', 'array', 'callable'):
        lines.append('~' + proof([raw(raw_type=typename(name))], [parameter(checked_type=normalized(name))]))
    for tag in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        lines.append('~' + proof([raw(raw_type=tag + ' (BYTES "aW50") eps')], [parameter(checked_type=normalized('int'))]))
    for raw_type, checked_type in (
            ('NNullableType (' + typename('int') + ') eps', '[(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NUnionType (SEQUENCE ([' + typename('int') + ', ' + typename('float') + '])) eps', '[(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "float"]))]')):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(checked_type=checked_type)]))
    lines += ['~' + proof([raw(raw_type=typename('int\x00'))], [parameter(checked_type=normalized('int'))]),
        '~' + proof(parameters=[parameter(checked_type=normalized('int'))]),
        '~' + proof([raw(raw_type=typename('int'))])]
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for actuals in ([argument('http_response_header')], [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')],
            [argument(unpack='true')], [argument(), argument()]):
        lines.append('~' + proof(actuals=actuals))
    required_raw, required = raw('ABSENT'), parameter('PSNONE', required='true')
    literal = integer(7)
    literal_raw, literal_parameter = raw(literal), parameter('(PSDEFAULT (' + literal + ') "int")')
    lines += [proof([required_raw, raw(), literal_raw], [required, parameter(), literal_parameter], [argument()] * 3),
        proof([literal_raw, raw()], [literal_parameter, parameter()], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, raw()], [required, parameter()]),
        '~' + proof(raws=[]), '~' + proof(parameters=[]), proof(actuals=[])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

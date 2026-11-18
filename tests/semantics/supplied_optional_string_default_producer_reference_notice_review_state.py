#!/usr/bin/env python3
"""Keep string defaults byte-exact and separate declaration checks from coercion."""
import base64
import json

import supplied_optional_string_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    if case['kind'] == 'array':
        return ['S_return.DEFAULTCACHE = eps']
    lines = ['S_return.DEFAULTCACHE = eps']
    encoded = lambda value: json.dumps(base64.b64encode(value.encode()).decode())
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    normalized = lambda kind: '[(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))]'
    string_type = normalized('string')

    def literal(value='seven', metadata='eps'):
        return 'NScalarString (BYTES ' + encoded(value) + ') (' + metadata + ')'

    def raw(default=None, raw_type=None, byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') ('
            + (typename('sTrInG') if raw_type is None else raw_type) + ') (BOOLEAN '
            + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (literal() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, kind='string', checked_type=string_type, byref='false', variadic='false', required='false'):
        value = '(PSDEFAULT (' + literal() + ') ' + json.dumps(kind) + ')' if default is None else default
        return ('psparam[.NAME = $ptascii("peer")][.TYPE = ' + checked_type + '][.BYREF = '
            + byref + '][.VARIADIC = ' + variadic + '][.REQUIRED = ' + required + '][.DEFAULT = ' + value + ']')

    def argument(name='x', named='ABSENT', unpack='false'):
        return 'NArg ' + named + ' (NExprVariable (BYTES ' + encoded(name) + ') eps) (BOOLEAN ' + unpack + ') (BOOLEAN false) eps'

    def proof(raws=None, parameters=None, actuals=None):
        raws = [raw()] if raws is None else raws
        parameters = [parameter()] if parameters is None else parameters
        actuals = [argument()] if actuals is None else actuals
        signature = 'pfunction_producer.SIGNATURE[.PARAMETERS = [' + ', '.join(parameters) + ']][.RETURNS = eps][.BYREF = false]'
        return ('$reference_notice_producer_arguments(SEQUENCE ([' + ', '.join(actuals)
            + ']), SEQUENCE ([' + ', '.join(raws) + ']), ' + signature + ')')

    for value in ('seven', 'SEVEN', '', '7', '01', '1e3', 'a b'):
        default = literal(value)
        for raw_type, checked_type in (('ABSENT', 'eps'), (typename('string'), string_type)):
            for byref in ('false', 'true'):
                lines.append(proof([raw(default, raw_type, byref)],
                    [parameter('(PSDEFAULT (' + default + ') "string")', checked_type=checked_type, byref=byref)]))
    for spelling in ('string', 'STRING', 'sTrInG'):
        lines.append(proof([raw(raw_type=typename(spelling))]))
    for kind in ('int', 'float', 'bool', 'null', 'deferred', 'STRING'):
        lines.append('~' + proof(parameters=[parameter(kind=kind)]))
    for default in ('PSNONE', 'PSDEFAULTUNSUPPORTED "unproved string default"',
            '(PSDEFAULT (' + literal('SEVEN') + ') "string")',
            '(PSDEFAULT (' + literal('7') + ') "string")',
            '(PSDEFAULT (' + literal(metadata='[MstartLine 99]') + ') "string")',
            '(PSDEFAULT (NScalarInt (INTEGER 7) eps) "string")'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    for default in ('NScalarInt (INTEGER 7) eps', 'NScalarFloat (FLOAT "401c000000000000") eps',
            'NExprConstFetch (NName (BYTES "c2V2ZW4=") eps) eps'):
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "string")')]))
    for kind in ('int', 'float', 'bool', 'mixed', 'array', 'true'):
        lines.append('~' + proof([raw(raw_type=typename(kind))], [parameter(checked_type=normalized(kind))]))
    lines += ['~' + proof([raw(raw_type='ABSENT')]), '~' + proof(parameters=[parameter(checked_type='eps')])]
    for tag in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        lines.append('~' + proof([raw(raw_type=tag + ' (BYTES "c3RyaW5n") eps')]))
    for raw_type, checked_type in (
            ('NNullableType (' + typename('string') + ') eps', '[(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NUnionType (SEQUENCE ([' + typename('string') + ', ' + typename('int') + '])) eps', '[(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "int"]))]')):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(checked_type=checked_type)]))
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for actuals in ([argument('http_response_header')], [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')],
            [argument(unpack='true')], [argument(), argument()]):
        lines.append('~' + proof(actuals=actuals))
    required_raw = raw('ABSENT', typename('int'))
    required = parameter('PSNONE', checked_type=normalized('int'), required='true')
    integral = 'NScalarInt (INTEGER 7) eps'
    integral_raw = raw(integral, typename('int'))
    integral_parameter = parameter('(PSDEFAULT (' + integral + ') "int")', checked_type=normalized('int'))
    lines += [proof([required_raw, raw()], [required, parameter()], [argument()] * 2),
        proof([integral_raw, raw()], [integral_parameter, parameter()], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, raw()], [required, parameter()]),
        '~' + proof(parameters=[]), '~' + proof(raws=[]), proof(actuals=[]),
        '$typed_conversion_at(S_return, ' + string_type + ', PINT 17, false) = TYPESTRING (PINT 17)',
        '$typed_conversion_at(S_return, ' + string_type + ', PINT 17, true) = TYPEREJECT']
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

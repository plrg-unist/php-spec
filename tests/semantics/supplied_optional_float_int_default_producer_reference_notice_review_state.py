#!/usr/bin/env python3
"""Distinguish promoted INT defaults from supplied FLOAT values and forged headers."""
import base64
import json

import supplied_optional_float_int_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    lines = ['S_args.DEFAULTCACHE = eps',
        'S_received.DEFAULTCACHE = S_args.DEFAULTCACHE']
    if case['kind'] != 'singleton':
        return lines
    encoded = lambda text: json.dumps(base64.b64encode(text.encode()).decode())
    integer = lambda value, metadata='eps': ('NScalarInt (INTEGER '
        + ('$(' + str(value) + ')' if value < 0 else str(value)) + ') (' + metadata + ')')
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    floating = '[(PTBRANCH ([PTBUILTIN "float"]))]'
    integral = '[(PTBRANCH ([PTBUILTIN "int"]))]'

    def raw(default=None, raw_type=None, byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') ('
            + (typename('FLoAt') if raw_type is None else raw_type) + ') (BOOLEAN '
            + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (integer(7) if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, normalized=floating, byref='false', variadic='false', required='false'):
        value = '(PSDEFAULT (' + integer(7) + ') "float")' if default is None else default
        return ('psparam[.NAME = $ptascii("peer")][.TYPE = ' + normalized + '][.BYREF = '
            + byref + '][.VARIADIC = ' + variadic + '][.REQUIRED = ' + required + '][.DEFAULT = ' + value + ']')

    def argument(name='x', named='ABSENT', unpack='false'):
        return ('NArg ' + named + ' (NExprVariable (BYTES ' + encoded(name)
            + ') eps) (BOOLEAN ' + unpack + ') (BOOLEAN false) eps')

    def proof(raws=None, parameters=None, actuals=None):
        raws = [raw()] if raws is None else raws
        parameters = [parameter()] if parameters is None else parameters
        actuals = [argument()] if actuals is None else actuals
        sequence = lambda values: 'SEQUENCE ([' + ', '.join(values) + '])'
        signature = ('pfunction_producer.SIGNATURE[.PARAMETERS = [' + ', '.join(parameters)
            + ']][.RETURNS = eps][.BYREF = false]')
        return '$reference_notice_producer_arguments(' + sequence(actuals) + ', ' + sequence(raws) + ', ' + signature + ')'

    lines.append(proof())
    for value in (-9223372036854775808, -1, 0, 2147483648, 9223372036854775807):
        default = integer(value)
        lines.append(proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "float")')]))
    for value in (-9223372036854775809, 9223372036854775808):
        default = integer(value)
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "float")')]))
    for byref in ('false', 'true'):
        lines.append(proof([raw(byref=byref)], [parameter(byref=byref)]))
    for bad in ('PSNONE', '(PSDEFAULT (' + integer(7) + ') "int")',
            '(PSDEFAULT (' + integer(8) + ') "float")',
            '(PSDEFAULT (' + integer(7, '[MstartLine 99]') + ') "float")',
            '(PSDEFAULT (NScalarFloat (FLOAT "401c000000000000") eps) "float")',
            'PSDEFAULTUNSUPPORTED "unproved default"'):
        lines.append('~' + proof(parameters=[parameter(bad)]))
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for normalized in ('eps', integral, floating[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        lines.append('~' + proof(parameters=[parameter(normalized=normalized)]))
    for raw_type in ('ABSENT', typename('int'), typename('float\x00'),
            'NNameFullyQualified (BYTES "ZmxvYXQ=") eps',
            'NNullableType (' + typename('float') + ') eps'):
        lines.append('~' + proof(raws=[raw(raw_type=raw_type)]))
    nullable = floating[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
    for raw_type in ('NNullableType (' + typename('float') + ') eps',
            'NUnionType (SEQUENCE ([' + typename('float') + ', ' + typename('null') + '])) eps'):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(normalized=nullable)]))
    for default in ('NScalarFloat (FLOAT "401c000000000000") eps',
            'NExprUnaryMinus (' + integer(7) + ') eps', 'NScalarString (BYTES "Nw==") eps'):
        lines.append(('' if default.startswith('NScalarFloat ') or default == 'NExprUnaryMinus (' + integer(7) + ') eps' else '~') + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "float")')]))
    for actuals in ([argument(), argument()], [argument('http_response_header')],
            [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')], [argument(unpack='true')]):
        lines.append('~' + proof(actuals=actuals))
    old_default = '(PSDEFAULT (' + integer(7) + ') "int")'
    for raw_type, normalized in (('ABSENT', 'eps'), (typename('int'), integral)):
        lines += [proof([raw(raw_type=raw_type)], [parameter(old_default, normalized)]),
            '~' + proof([raw(raw_type=raw_type)], [parameter(normalized=normalized)])]
    required_raw = raw('ABSENT', typename('int'))
    required = parameter('PSNONE', integral, required='true')
    old_raw, old = raw(raw_type=typename('int')), parameter(old_default, integral)
    lines += ['~' + proof(raws=[]), '~' + proof(parameters=[]), proof(actuals=[]),
        proof([required_raw, raw()], [required, parameter()], [argument()] * 2),
        proof([old_raw, raw()], [old, parameter()], [argument()] * 2),
        proof([raw(), raw()], [parameter(), parameter()], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, raw()], [required, parameter()], [argument()])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

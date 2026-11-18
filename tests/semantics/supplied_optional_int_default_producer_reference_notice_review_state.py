#!/usr/bin/env python3
"""Probe default authentication and the boundary of the supplied-argument view."""
import base64
import json

import supplied_optional_int_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    lines = ['$call_target(S_full, pfunction_producer.NAME, eps) = (pfunction_survived)',
        'pfunction_survived.SIGNATURE = pfunction_producer.SIGNATURE']
    if case['kind'] != 'singleton':
        return lines
    encoded = lambda text: json.dumps(base64.b64encode(text.encode()).decode())
    integer = lambda value, metadata='eps': ('NScalarInt (INTEGER '
        + ('$('+str(value)+')' if value < 0 else str(value)) + ') (' + metadata + ')')
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'

    def raw(default=None, raw_type='ABSENT', byref='false', variadic='false', attributes='eps', flags=0, hooks='eps'):
        return ('NParam (SEQUENCE ' + attributes + ') (INTEGER ' + str(flags) + ') ('
            + raw_type + ') (BOOLEAN ' + byref + ') (BOOLEAN ' + variadic
            + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (integer(7) if default is None else default) + ') (SEQUENCE ' + hooks + ') eps')

    def parameter(default=None, normalized='eps', byref='false', variadic='false', required='false'):
        return ('{ NAME $ptascii("peer"), TYPE (' + normalized + '), BYREF ' + byref
            + ', VARIADIC ' + variadic + ', REQUIRED ' + required + ', DEFAULT '
            + ('(PSDEFAULT (' + integer(7) + ') "int")' if default is None else default) + ' }')

    def argument(name='x', named='ABSENT', unpack='false'):
        return ('NArg ' + named + ' (NExprVariable (BYTES ' + encoded(name)
            + ') eps) (BOOLEAN ' + unpack + ') (BOOLEAN false) eps')

    def proof(raws=None, parameters=None, actuals=None):
        raws = [raw()] if raws is None else raws
        parameters = [parameter()] if parameters is None else parameters
        actuals = [argument()] if actuals is None else actuals
        sequence = lambda values: 'SEQUENCE ([' + ', '.join(values) + '])'
        signature = '{ PARAMETERS ([' + ', '.join(parameters) + ']), RETURNS eps, BYREF false }'
        return ('$reference_notice_producer_arguments(' + sequence(actuals) + ', '
            + sequence(raws) + ', ' + signature + ')')

    lines.append(proof())
    for value in (-9223372036854775808, -1, 0, 2147483648, 9223372036854775807):
        default = integer(value)
        lines.append(proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "int")')]))
    for value in (-9223372036854775809, 9223372036854775808):
        default = integer(value)
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "int")')]))
    for raw_type, normalized in (('ABSENT', 'eps'), (typename('InT'), '[(PTBRANCH ([PTBUILTIN "int"]))]')):
        for byref in ('false', 'true'):
            lines.append(proof([raw(raw_type=raw_type, byref=byref)], [parameter(normalized=normalized, byref=byref)]))
    lines += ['~' + proof(parameters=[parameter(normalized='[(PTBRANCH ([PTBUILTIN "int"]))]')]),
        '~' + proof(raws=[raw(raw_type=typename('int'))]),
        '~' + proof(raws=[raw(raw_type='NNameFullyQualified (BYTES "aW50") eps')]),
        '~' + proof(raws=[raw(raw_type=typename('int\x00'))])]
    for name in ('array', 'float', 'bool', 'string', 'mixed', 'iterable', 'object', 'callable'):
        normalized = '[(PTBRANCH ([PTBUILTIN ' + json.dumps(name) + ']))]'
        lines += ['~' + proof([raw(raw_type=typename(name))], [parameter(normalized=normalized)]),
            '~' + proof([raw(raw_type=typename('int'))], [parameter(normalized=normalized)])]
    for bad_default in ('PSNONE', '(PSDEFAULT (' + integer(8) + ') "int")',
            '(PSDEFAULT (' + integer(7, '[MstartLine 99]') + ') "int")',
            '(PSDEFAULT (' + integer(7) + ') "float")', 'PSDEFAULTUNSUPPORTED "unproved default"'):
        lines.append('~' + proof(parameters=[parameter(bad_default)]))
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for default in ('ABSENT', 'NScalarFloat (FLOAT "401c000000000000") eps',
            'NExprUnaryMinus (' + integer(7) + ') eps', 'NExprVariable (BYTES "eA==") eps'):
        lines.append('~' + proof(raws=[raw(default)]))
    for actuals in ([argument(), argument()], [argument('http_response_header')],
            [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')], [argument(unpack='true')]):
        lines.append('~' + proof(actuals=actuals))
    lines += ['~' + proof(raws=[]), '~' + proof(parameters=[]),
        '~' + proof(raws=[raw(), raw()]), '~' + proof(parameters=[parameter(), parameter()]),
        proof(actuals=[])]
    required_raw, required = raw('ABSENT'), parameter('PSNONE', required='true')
    lines += [proof([required_raw], [required]),
        proof([required_raw, raw()], [required, parameter()], [argument(), argument()]),
        proof([raw(), raw()], [parameter(), parameter()], [argument(), argument()]),
        proof([required_raw, raw(), raw()], [required, parameter(), parameter()], [argument()] * 3),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument(), argument()]),
        '~' + proof([required_raw, raw()], [required, parameter()], [argument()])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

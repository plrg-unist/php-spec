#!/usr/bin/env python3
"""Check literal FLOAT identity and retained promoted-INT header controls."""
import base64
import json

import supplied_optional_float_default_producer_reference_notice_state as driver
import supplied_optional_float_int_default_producer_reference_notice_review_state as promoted

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    if case['kind'] == 'array':
        return ['S_return.DEFAULTCACHE = eps']
    lines = promoted.independent_controls(case)
    encoded = lambda value: json.dumps(base64.b64encode(value.encode()).decode())
    literal = lambda bits='401e000000000000', metadata='eps': 'NScalarFloat (FLOAT ' + json.dumps(bits) + ') (' + metadata + ')'
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    floating = '[(PTBRANCH ([PTBUILTIN "float"]))]'
    integral = '[(PTBRANCH ([PTBUILTIN "int"]))]'

    def raw(default=None, raw_type=None, byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') ('
            + (typename('FLoAt') if raw_type is None else raw_type) + ') (BOOLEAN '
            + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (literal() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, normalized=floating, byref='false', variadic='false', required='false'):
        value = '(PSDEFAULT (' + literal() + ') "float")' if default is None else default
        return ('psparam[.NAME = $ptascii("peer")][.TYPE = ' + normalized + '][.BYREF = '
            + byref + '][.VARIADIC = ' + variadic + '][.REQUIRED = ' + required + '][.DEFAULT = ' + value + ']')

    def proof(raws=None, parameters=None, count=1):
        raws = [raw()] if raws is None else raws
        parameters = [parameter()] if parameters is None else parameters
        actual = 'NArg ABSENT (NExprVariable (BYTES "eA==") eps) (BOOLEAN false) (BOOLEAN false) eps'
        signature = 'pfunction_producer.SIGNATURE[.PARAMETERS = [' + ', '.join(parameters) + ']][.RETURNS = eps][.BYREF = false]'
        return ('$reference_notice_producer_arguments(SEQUENCE ([' + ', '.join([actual] * count)
            + ']), SEQUENCE ([' + ', '.join(raws) + ']), ' + signature + ')')

    lines.append(proof())
    for bits in ('0000000000000000', '8000000000000000', '3ff0000000000000', '7ff0000000000000'):
        default = literal(bits)
        lines.append(proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "float")')]))
    for raw_type, normalized in (('ABSENT', 'eps'), (typename('float'), floating)):
        for byref in ('false', 'true'):
            lines.append(proof([raw(raw_type=raw_type, byref=byref)], [parameter(normalized=normalized, byref=byref)]))
    for default in ('PSNONE', '(PSDEFAULT (' + literal() + ') "int")',
            '(PSDEFAULT (' + literal('401c000000000000') + ') "float")',
            '(PSDEFAULT (' + literal(metadata='[MstartLine 99]') + ') "float")',
            '(PSDEFAULT (NScalarInt (INTEGER 7) eps) "float")', 'PSDEFAULTUNSUPPORTED "unproved default"'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    lines.append('~' + proof([raw(literal('0000000000000000'))],
        [parameter('(PSDEFAULT (' + literal('8000000000000000') + ') "float")')]))
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for name in ('int', 'bool', 'string', 'mixed', 'array', 'iterable'):
        normalized = '[(PTBRANCH ([PTBUILTIN ' + json.dumps(name) + ']))]'
        lines.append('~' + proof([raw(raw_type=typename(name))], [parameter(normalized=normalized)]))
    lines += ['~' + proof([raw(raw_type='ABSENT')]), '~' + proof(parameters=[parameter(normalized='eps')])]
    nullable = floating[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
    for raw_type in ('NNullableType (' + typename('float') + ') eps',
            'NUnionType (SEQUENCE ([' + typename('float') + ', ' + typename('null') + '])) eps'):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(normalized=nullable)]))
    unary = 'NExprUnaryMinus (' + literal() + ') eps'
    lines.append(proof([raw(unary)], [parameter('(PSDEFAULT (' + unary + ') "float")')]))
    required_raw = raw('ABSENT', typename('int'))
    required = parameter('PSNONE', integral, required='true')
    promoted_raw = raw('NScalarInt (INTEGER 7) eps')
    promoted_parameter = parameter('(PSDEFAULT (NScalarInt (INTEGER 7) eps) "float")')
    lines += [proof([required_raw, raw()], [required, parameter()], 2),
        proof([promoted_raw, raw()], [promoted_parameter, parameter()], 2),
        proof([raw(raw_type='ABSENT'), raw()], [parameter(normalized='eps'), parameter()], 2),
        '~' + proof([raw(), required_raw], [parameter(), required], 2),
        '~' + proof([required_raw, raw()], [required, parameter()]),
        '~' + proof(parameters=[]), '~' + proof(raws=[]), proof(count=0)]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

#!/usr/bin/env python3
"""Authenticate Boolean keyword spelling, both metadata layers and literal kinds."""
import base64
import json

import supplied_optional_bool_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    if case['kind'] == 'array':
        return ['S_return.DEFAULTCACHE = eps']
    lines = ['S_args.DEFAULTCACHE = eps', 'S_received.DEFAULTCACHE = S_args.DEFAULTCACHE']
    encoded = lambda value: json.dumps(base64.b64encode(value.encode()).decode())
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    boolean = '[(PTBRANCH ([PTBUILTIN "bool"]))]'
    integral = '[(PTBRANCH ([PTBUILTIN "int"]))]'
    floating = '[(PTBRANCH ([PTBUILTIN "float"]))]'

    def literal(name='TrUe', tag='NName', inner='eps', outer='eps'):
        return 'NExprConstFetch (' + tag + ' (BYTES ' + encoded(name) + ') (' + inner + ')) (' + outer + ')'

    def raw(default=None, raw_type=None, byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') ('
            + (typename('bOoL') if raw_type is None else raw_type) + ') (BOOLEAN '
            + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (literal() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, kind='true', normalized=boolean, byref='false', variadic='false', required='false'):
        value = '(PSDEFAULT (' + literal() + ') ' + json.dumps(kind) + ')' if default is None else default
        return ('psparam[.NAME = $ptascii("peer")][.TYPE = ' + normalized + '][.BYREF = '
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

    for name in ('true', 'TRUE', 'TrUe', 'false', 'FALSE', 'FaLsE'):
        default = literal(name)
        lines.append(proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') ' + json.dumps(name.lower()) + ')')]))
    for raw_type, normalized in (('ABSENT', 'eps'), (typename('bool'), boolean)):
        for byref in ('false', 'true'):
            lines.append(proof([raw(raw_type=raw_type, byref=byref)], [parameter(normalized=normalized, byref=byref)]))
    for kind in ('bool', 'false', 'TRUE', 'null', 'deferred', 'int'):
        lines.append('~' + proof(parameters=[parameter(kind=kind)]))
    for default in ('PSNONE', 'PSDEFAULTUNSUPPORTED "unproved default"',
            '(PSDEFAULT (' + literal('true') + ') "true")',
            '(PSDEFAULT (' + literal(inner='[MstartLine 99]') + ') "true")',
            '(PSDEFAULT (' + literal(outer='[MstartLine 99]') + ') "true")',
            '(PSDEFAULT (NScalarInt (INTEGER 1) eps) "true")'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    for tag in ('NNameFullyQualified', 'NNameRelative'):
        default = literal(tag=tag)
        lines.append(('' if tag == 'NNameFullyQualified' else '~') + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "true")')]))
    for name in ('null', 'Other', 'Other\\true', '\\true', 'true\x00', ''):
        default = literal(name)
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "true")')]))
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for name in ('int', 'float', 'string', 'mixed', 'array', 'true'):
        normalized = '[(PTBRANCH ([PTBUILTIN ' + json.dumps(name) + ']))]'
        lines.append(('' if name == 'true' else '~') + proof([raw(raw_type=typename(name))], [parameter(normalized=normalized)]))
    lines += ['~' + proof([raw(raw_type='ABSENT')]), '~' + proof(parameters=[parameter(normalized='eps')])]
    nullable = boolean[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
    for raw_type in ('NNullableType (' + typename('bool') + ') eps',
            'NUnionType (SEQUENCE ([' + typename('bool') + ', ' + typename('null') + '])) eps'):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(normalized=nullable)]))
    for actuals in ([argument(), argument()], [argument('http_response_header')],
            [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')], [argument(unpack='true')]):
        lines.append('~' + proof(actuals=actuals))
    required_raw = raw('ABSENT', typename('int'))
    required = parameter('PSNONE', normalized=integral, required='true')
    int_default = 'NScalarInt (INTEGER 7) eps'
    float_default = 'NScalarFloat (FLOAT "401e000000000000") eps'
    lines += [proof([raw(int_default, typename('int'))], [parameter('(PSDEFAULT (' + int_default + ') "int")', normalized=integral)]),
        proof([raw(int_default, typename('float'))], [parameter('(PSDEFAULT (' + int_default + ') "float")', normalized=floating)]),
        proof([raw(float_default, typename('float'))], [parameter('(PSDEFAULT (' + float_default + ') "float")', normalized=floating)]),
        proof([required_raw, raw()], [required, parameter()], [argument()] * 2),
        proof([raw(raw_type='ABSENT'), raw()], [parameter(normalized='eps'), parameter()], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, raw()], [required, parameter()]),
        '~' + proof(parameters=[]), '~' + proof(raws=[]), proof(actuals=[])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

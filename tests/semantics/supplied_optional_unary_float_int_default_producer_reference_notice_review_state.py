#!/usr/bin/env python3
"""Separate promoted signed INT defaults from forged kinds and FLOAT overflow."""
import base64
import json

import supplied_optional_float_int_default_producer_reference_notice_review_state as old_review
import supplied_optional_unary_float_int_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    lines = ['S_args.DEFAULTCACHE = eps', 'S_received.DEFAULTCACHE = S_args.DEFAULTCACHE']
    if case['kind'] != 'singleton':
        return lines
    encoded = lambda text: json.dumps(base64.b64encode(text.encode()).decode())
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    normalized = lambda name: '[(PTBRANCH ([PTBUILTIN ' + json.dumps(name) + ']))]'
    floating = normalized('float')

    def integer(value, metadata='eps'):
        value = '$(' + str(value) + ')' if value < 0 else str(value)
        return 'NScalarInt (INTEGER ' + value + ') (' + metadata + ')'

    def signed(sign='Minus', value=7, leaf_metadata='eps', metadata='eps'):
        return 'NExprUnary' + sign + ' (' + integer(value, leaf_metadata) + ') (' + metadata + ')'

    def raw(default=None, raw_type=None, byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') ('
            + (typename('FLOAT') if raw_type is None else raw_type) + ') (BOOLEAN '
            + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (signed() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, kind='float', checked_type=floating, byref='false', variadic='false', required='false'):
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

    # Run only the one changed old query, grounded in this fresh singleton.
    marker = 'NExprUnaryMinus (' + integer(7) + ') eps'
    affected = [line for line in old_review.independent_controls(case) if marker in line]
    assert len(affected) == 1 and not affected[0].startswith('~')
    lines += affected
    for sign, values in (('Plus', (-9223372036854775808, -1, 0, 7, 9223372036854775807)),
            ('Minus', (-9223372036854775807, -1, 0, 7, 9223372036854775807))):
        for value in values:
            default = signed(sign, value)
            for byref in ('false', 'true'):
                lines.append(proof([raw(default, byref=byref)],
                    [parameter('(PSDEFAULT (' + default + ') "float")', byref=byref)]))
    for spelling in ('float', 'fLoAt'):
        lines.append(proof([raw(raw_type=typename(spelling))]))
    for sign in ('Plus', 'Minus'):
        for value in (-9223372036854775809, 9223372036854775808):
            default = signed(sign, value)
            lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "float")')]))
    minimum_negation = signed('Minus', -9223372036854775808)
    lines.append('~' + proof([raw(minimum_negation)], [parameter('(PSDEFAULT (' + minimum_negation + ') "float")')]))
    exact = signed(leaf_metadata='[MstartLine 7]', metadata='[MstartLine 8]')
    lines.append(proof([raw(exact)], [parameter('(PSDEFAULT (' + exact + ') "float")')]))
    for default in (signed('Plus'), signed('Plus', -7), signed(value=8), integer(-7),
            signed(leaf_metadata='[MstartLine 7]'), signed(metadata='[MstartLine 8]')):
        lines.append('~' + proof(parameters=[parameter('(PSDEFAULT (' + default + ') "float")')]))
    for kind in ('int', 'string', 'bool', 'deferred', 'FLOAT'):
        lines.append('~' + proof(parameters=[parameter(kind=kind)]))
    for default in ('PSNONE', 'PSDEFAULTUNSUPPORTED "unproved signed promotion"'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    for default in ('NExprUnaryPlus (' + signed() + ') eps',
            'NExprUnaryMinus (' + signed('Plus') + ') eps',
            'NExprUnaryMinus (NScalarFloat (FLOAT "401c000000000000") eps) eps',
            'NExprUnaryPlus (NScalarFloat (FLOAT "401c000000000000") eps) eps',
            'NExprUnaryPlus (NScalarString (BYTES "Nw==") eps) eps',
            'NExprUnaryMinus (NExprConstFetch (NName (BYTES "c2V2ZW4=") eps) eps) eps'):
        lines.append(('' if default.startswith(('NExprUnaryMinus (NScalarFloat ', 'NExprUnaryPlus (NScalarFloat ')) else '~') + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "float")')]))
    for name in ('int', 'bool', 'string', 'mixed', 'array', 'callable', 'double'):
        lines.append('~' + proof([raw(raw_type=typename(name))], [parameter(checked_type=normalized(name))]))
    for tag in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        lines.append('~' + proof([raw(raw_type=tag + ' (BYTES "ZmxvYXQ=") eps')]))
    for raw_type, checked_type in (
            ('NNullableType (' + typename('float') + ') eps', '[(PTBRANCH ([PTBUILTIN "float"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NUnionType (SEQUENCE ([' + typename('float') + ', ' + typename('int') + '])) eps', '[(PTBRANCH ([PTBUILTIN "float"])), (PTBRANCH ([PTBUILTIN "int"]))]')):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(checked_type=checked_type)]))
    lines += ['~' + proof([raw(raw_type=typename('float\x00'))]),
        '~' + proof([raw(raw_type='ABSENT')], [parameter(checked_type='eps')]),
        '~' + proof([raw(raw_type='ABSENT')]), '~' + proof(parameters=[parameter(checked_type='eps')])]
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for actuals in ([argument('http_response_header')], [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')],
            [argument(unpack='true')], [argument(), argument()]):
        lines.append('~' + proof(actuals=actuals))
    required_raw, required = raw('ABSENT', typename('int')), parameter('PSNONE', checked_type=normalized('int'), required='true')
    old_raw, old = raw(raw_type='ABSENT'), parameter(kind='int', checked_type='eps')
    lines += [proof([required_raw, raw()], [required, parameter()], [argument()] * 2),
        proof([old_raw, raw()], [old, parameter()], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, raw()], [required, parameter()]),
        '~' + proof(raws=[]), '~' + proof(parameters=[]), proof(actuals=[])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

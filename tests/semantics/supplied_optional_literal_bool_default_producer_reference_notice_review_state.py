#!/usr/bin/env python3
"""Match literal Boolean formals and defaults without weak scalar coercion."""
import base64
import json

import supplied_optional_bool_default_producer_reference_notice_review_state as prior
import supplied_optional_literal_bool_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] not in ('false_byref', 'true_byval'):
        return []
    lines = ['S_receive.DEFAULTCACHE = eps', 'S_return.DEFAULTCACHE = eps']
    if case['kind'] != 'false_byref':
        return lines
    lines += prior.independent_controls({'kind': 'singleton'})[2:]
    encoded = lambda value: json.dumps(base64.b64encode(value.encode()).decode())
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    normalized = lambda kind: '[(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))]'

    def literal(name='TrUe', tag='NName', inner='eps', outer='eps'):
        return 'NExprConstFetch (' + tag + ' (BYTES ' + encoded(name) + ') (' + inner + ')) (' + outer + ')'

    def raw(default=None, raw_type=None, byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') ('
            + (typename('TrUe') if raw_type is None else raw_type) + ') (BOOLEAN '
            + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (literal() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, kind='true', checked_type=None, byref='false', variadic='false', required='false'):
        value = '(PSDEFAULT (' + literal() + ') ' + json.dumps(kind) + ')' if default is None else default
        return ('psparam[.NAME = $ptascii("peer")][.TYPE = '
            + (normalized('true') if checked_type is None else checked_type) + '][.BYREF = '
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

    for spelling in ('true', 'TRUE', 'TrUe', 'false', 'FALSE', 'FaLsE'):
        kind = spelling.lower()
        default = literal(spelling)
        for byref in ('false', 'true'):
            lines.append(proof([raw(default, typename(spelling), byref)],
                [parameter('(PSDEFAULT (' + default + ') ' + json.dumps(kind) + ')', checked_type=normalized(kind), byref=byref)]))
    for kind, opposite in (('true', 'false'), ('false', 'true')):
        default = literal(kind)
        checked = '(PSDEFAULT (' + default + ') ' + json.dumps(kind) + ')'
        for raw_type, checked_type in ((typename(opposite), normalized(kind)),
                (typename(kind), normalized(opposite)), (typename('bool'), normalized(kind)),
                (typename(kind), normalized('bool')), ('ABSENT', normalized(kind)), (typename(kind), 'eps')):
            lines.append('~' + proof([raw(default, raw_type)], [parameter(checked, checked_type=checked_type)]))
        for strict in ('false', 'true'):
            conversion = '$typed_conversion_at(S_receive, ' + normalized(kind) + ', '
            lines.append(conversion + 'PBOOL ' + kind + ', ' + strict + ') = TYPEVALUE (PBOOL ' + kind + ')')
            for value in ('PBOOL ' + opposite, 'PINT 0', 'PINT 1', 'PSTRING eps', 'PSTRING ($ptascii("1"))', 'PNULL'):
                lines.append(conversion + value + ', ' + strict + ') = TYPEREJECT')
    for kind in ('bool', 'false', 'TRUE', 'null', 'deferred'):
        lines.append('~' + proof(parameters=[parameter(kind=kind)]))
    for default in ('PSNONE', 'PSDEFAULTUNSUPPORTED "unproved literal default"',
            '(PSDEFAULT (' + literal('true') + ') "true")',
            '(PSDEFAULT (' + literal(inner='[MstartLine 99]') + ') "true")',
            '(PSDEFAULT (' + literal(outer='[MstartLine 99]') + ') "true")',
            '(PSDEFAULT (NScalarInt (INTEGER 1) eps) "true")'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    for tag in ('NNameFullyQualified', 'NNameRelative'):
        default = literal(tag=tag)
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "true")')]))
    for name in ('null', 'Other', 'Other\\true', '\\true', 'true\x00', ''):
        default = literal(name)
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "true")')]))
    for tag in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        lines.append('~' + proof([raw(raw_type=tag + ' (BYTES "dHJ1ZQ==") eps')]))
    for raw_type, checked_type in (
            ('NNullableType (' + typename('true') + ') eps', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
            ('NUnionType (SEQUENCE ([' + typename('true') + ', ' + typename('int') + '])) eps', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "int"]))]')):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(checked_type=checked_type)]))
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for actuals in ([argument('http_response_header')], [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')],
            [argument(unpack='true')], [argument(), argument()]):
        lines.append('~' + proof(actuals=actuals))
    required_raw = raw('ABSENT')
    required = parameter('PSNONE', required='true')
    false_default = literal('false')
    false_raw = raw(false_default, typename('false'), 'true')
    false_parameter = parameter('(PSDEFAULT (' + false_default + ') "false")', checked_type=normalized('false'), byref='true')
    lines += [proof([required_raw, false_raw], [required, false_parameter], [argument()] * 2),
        proof([raw(), false_raw], [parameter(), false_parameter], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, false_raw], [required, false_parameter]),
        '~' + proof(parameters=[]), '~' + proof(raws=[]), proof(actuals=[])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

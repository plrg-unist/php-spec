#!/usr/bin/env python3
"""Authenticate fully qualified Boolean defaults without admitting other constants."""
import base64
import json

import supplied_optional_literal_bool_default_producer_reference_notice_review_state as prior
import supplied_optional_fqn_bool_default_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    if case['kind'] != 'true_byval':
        return ['S_return.DEFAULTCACHE = eps']
    lines = prior.independent_controls({'kind': 'false_byref'})
    encoded = lambda value: json.dumps(base64.b64encode(value.encode()).decode())
    typename = lambda name: 'NIdentifier (BYTES ' + encoded(name) + ') eps'
    normalized = lambda kind: '[(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))]'

    def literal(name='TrUe', tag='NNameFullyQualified', inner='eps', outer='eps'):
        return 'NExprConstFetch (' + tag + ' (BYTES ' + encoded(name) + ') (' + inner + ')) (' + outer + ')'

    def raw(default=None, raw_type=None, byref='false', variadic='false', flags=0):
        return ('NParam (SEQUENCE eps) (INTEGER ' + str(flags) + ') ('
            + (typename('bOoL') if raw_type is None else raw_type) + ') (BOOLEAN '
            + byref + ') (BOOLEAN ' + variadic + ') (NExprVariable (BYTES "cGVlcg==") eps) ('
            + (literal() if default is None else default) + ') (SEQUENCE eps) eps')

    def parameter(default=None, kind='true', checked_type=None, byref='false', variadic='false', required='false'):
        value = '(PSDEFAULT (' + literal() + ') ' + json.dumps(kind) + ')' if default is None else default
        return ('psparam[.NAME = $ptascii("peer")][.TYPE = '
            + (normalized('bool') if checked_type is None else checked_type) + '][.BYREF = '
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
        for raw_type, checked_type in (('ABSENT', 'eps'), (typename('bool'), normalized('bool')),
                (typename(spelling), normalized(kind))):
            for byref in ('false', 'true'):
                lines.append(proof([raw(default, raw_type, byref)],
                    [parameter('(PSDEFAULT (' + default + ') ' + json.dumps(kind) + ')', checked_type=checked_type, byref=byref)]))
    for kind in ('bool', 'false', 'TRUE', 'null', 'deferred', 'int'):
        lines.append('~' + proof(parameters=[parameter(kind=kind)]))
    for name, kind in (('null', 'null'), ('deferred', 'deferred')):
        default = literal(name)
        lines.append('~' + proof([raw(default, 'ABSENT')],
            [parameter('(PSDEFAULT (' + default + ') ' + json.dumps(kind) + ')', checked_type='eps')]))
    for name in ('Other', 'Other\\true', '\\true', 'true\x00', ''):
        default = literal(name)
        lines.append('~' + proof([raw(default)], [parameter('(PSDEFAULT (' + default + ') "true")')]))
    for default in ('PSNONE', 'PSDEFAULTUNSUPPORTED "unproved FQN default"',
            '(PSDEFAULT (' + literal(tag='NName') + ') "true")',
            '(PSDEFAULT (' + literal('true') + ') "true")',
            '(PSDEFAULT (' + literal(inner='[MstartLine 99]') + ') "true")',
            '(PSDEFAULT (' + literal(outer='[MstartLine 99]') + ') "true")'):
        lines.append('~' + proof(parameters=[parameter(default)]))
    relative = literal(tag='NNameRelative')
    lines.append('~' + proof([raw(relative)], [parameter('(PSDEFAULT (' + relative + ') "true")')]))
    for raw_type, checked_type in ((typename('false'), normalized('false')), (typename('true'), normalized('false')),
            (typename('true'), normalized('bool')), ('ABSENT', normalized('bool')), (typename('bool'), 'eps')):
        lines.append('~' + proof([raw(raw_type=raw_type)], [parameter(checked_type=checked_type)]))
    for tag in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        lines.append('~' + proof([raw(raw_type=tag + ' (BYTES "Ym9vbA==") eps')]))
    nullable = 'NNullableType (' + typename('bool') + ') eps'
    lines.append('~' + proof([raw(raw_type=nullable)],
        [parameter(checked_type='[(PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))]')]))
    for change in ({'required': 'true'}, {'variadic': 'true'}, {'byref': 'true'}):
        lines.append('~' + proof(parameters=[parameter(**change)]))
    for change in ({'variadic': 'true'}, {'byref': 'true'}, {'flags': 1}):
        lines.append('~' + proof(raws=[raw(**change)]))
    for actuals in ([argument('http_response_header')], [argument(named='(NIdentifier (BYTES "cGVlcg==") eps)')],
            [argument(unpack='true')], [argument(), argument()]):
        lines.append('~' + proof(actuals=actuals))
    required_raw = raw('ABSENT', typename('int'))
    required = parameter('PSNONE', checked_type=normalized('int'), required='true')
    bare = literal(tag='NName')
    lines += [proof([required_raw, raw()], [required, parameter()], [argument()] * 2),
        proof([raw(bare), raw()], [parameter('(PSDEFAULT (' + bare + ') "true")'), parameter()], [argument()] * 2),
        '~' + proof([raw(), required_raw], [parameter(), required], [argument()] * 2),
        '~' + proof([required_raw, raw()], [required, parameter()]),
        '~' + proof(parameters=[]), '~' + proof(raws=[]), proof(actuals=[])]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

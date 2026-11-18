#!/usr/bin/env python3
"""Distinguish resolved alias bytes from raw names in reached producer states."""
import base64
import json

import scoped_case_stdclass_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    formal = case['side'] == 'formal'
    role = case['role_index'] if formal else 0
    encoded = lambda text: json.dumps(base64.b64encode(text.encode()).decode())
    raw_type = lambda name, tag='NName': driver.prior.raw_type(case, name, tag)

    def parameter(typename, index=role, byref=None, variadic='false'):
        suffix = '' if index == 0 else '_last'
        flag = str(index == 1).lower() if byref is None else byref
        return ('NParam (SEQUENCE eps) (INTEGER 0) (' + typename + ') (BOOLEAN ' + flag
            + ') (BOOLEAN ' + variadic + ') phpType10' + suffix
            + ' ABSENT (SEQUENCE eps) metadata_parameter' + suffix)

    def proof(name, target, context, normalized=None):
        typename = raw_type(name)
        checked_type = driver.prior.normalized(case, target) if normalized is None else normalized
        checked = signature
        if formal:
            arguments = [parameter(typename, index) for index in range(role + 1)]
            parameters = ['psparam' + ('' if index == 0 else '_last') + '[.TYPE = '
                + checked_type + ']' for index in range(role + 1)]
            checked += '[.PARAMETERS = [' + ', '.join(parameters) + ']]'
            arguments, returns = 'SEQUENCE ([' + ', '.join(arguments) + '])', 'phpType18'
        else:
            arguments, returns = 'phpType16', typename
            checked += '[.RETURNS = ' + checked_type + ']'
        return ('$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, '
            + arguments + ', ' + returns + ', ' + checked + ')')

    def context(alias, target, namespace='PeerScope138'):
        return (env + '[.NAMESPACE = $ptascii(' + json.dumps(namespace)
            + ')][.CLASSES = [($ptascii(' + json.dumps(alias) + '), $ptascii('
            + json.dumps(target) + '))]]')

    lines = []
    for target in ('STDCLASS', 'StDcLaSs'):
        ctx = context('pEeRbOx138', target)
        for name in ('PeerBox138', 'peerbox138', 'PEERBOX138'):
            lines += [proof(name, target, ctx), '~' + proof(name, target.swapcase(), ctx)]
        lines += ['~' + proof('PeerBox138', 'stdClass', ctx),
            '~' + proof('sTdClAsS', target, context('stdclass', 'Other')),
            '~' + proof('PeerBox138', target, context('unrelated', target)),
            '~' + proof('PeerBox138', target, env + '[.CLASSES = eps]')]
        if formal:
            for byref, variadic in (('false', 'false'), ('true', 'false'), ('true', 'true')):
                before = parameter(raw_type('PeerBox138'), byref=byref, variadic=variadic)
                after = parameter(raw_type(target, 'NNameFullyQualified'), byref=byref, variadic=variadic)
                lines.append('$reference_notice_producer_scoped_parameter_view(' + ctx + ', '
                    + before + ') = (' + after + ')')
        if case['shape'] == 'union':
            members = case['formal_members'] if formal else case['return_members']
            helper = '$reference_notice_producer_scoped_' + ('' if formal else 'return_') + 'union_view('
            atoms = lambda tag, members=members: '[' + ', '.join((tag + ' (BYTES ' + encoded('PeerBox138')
                + ') eps') if member == 'class' else 'NIdentifier (BYTES '
                + encoded(member) + ') eps' for member in members) + ']'
            original = atoms('NName')
            expected = original.replace('NName (BYTES ' + encoded('PeerBox138') + ')',
                'NNameFullyQualified (BYTES ' + encoded(target) + ')')
            lines += [helper + ctx + ', ' + original + ', false) = (' + expected + ')',
                helper + ctx + ', ' + original + ', true) = eps',
                helper + ctx + ', ' + atoms('NNameRelative') + ', false) = eps',
                helper + ctx + ', [' + original[1:-1] + ', NName (BYTES '
                    + encoded('PeerBox138') + ') eps], false) = eps']
            reversed_type = driver.prior.ordered.ordered.normalized(members[::-1], target)
            lines.append('~' + proof('PeerBox138', target, ctx, reversed_type))
            if not formal:
                for null_members in (['class', 'null'], ['null', 'class']):
                    original = atoms('NName', null_members)
                    expected = original.replace('NName (BYTES ' + encoded('PeerBox138') + ')',
                        'NNameFullyQualified (BYTES ' + encoded(target) + ')')
                    lines.append(helper + ctx + ', ' + original + ', false) = (' + expected + ')')
    if formal:
        ctx = context('PeerBox138', 'stdclass')
        lines += ['$reference_notice_producer_scoped_parameter_view(' + ctx + ', '
            + parameter(raw_type('PeerBox138')) + ') = ('
            + parameter(raw_type('stdclass', 'NNameFullyQualified')) + ')',
            '~' + proof('PeerBox138', 'stdClass', ctx)]
    if case.get('nullable_first'):
        lines += ['S_received_first.OBJECTPROPS = S_receive_first.OBJECTPROPS',
            'n_first =/= n_receive']
    if formal and case['shape'] == 'bare':
        for payload in ([0], [255], [0, 255], [255, 0, 255], [251, 255, 255],
                [0, 127, 128, 254, 255], list(range(8))):
            value = '[' + ', '.join(map(str, payload)) + ']'
            expected = json.dumps(base64.b64encode(bytes(payload)).decode())
            lines += ['$reference_notice_producer_type_encoding(' + value + ') = ' + expected,
                '$base64($reference_notice_producer_type_encoding(' + value + ')) = ' + value]
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    raise SystemExit(0 if driver.main() else 1)

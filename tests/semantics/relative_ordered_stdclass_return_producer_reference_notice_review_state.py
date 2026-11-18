#!/usr/bin/env python3
"""Check relative RETURN unions against fresh retirement states and aliased formals."""
import base64
import json

import global_relative_ordered_stdclass_return_producer_reference_notice_state as driver
import global_plain_ordered_stdclass_return_producer_reference_notice_state as ordered

author_controls = driver.controls


def independent_controls(case):
    if case['kind'] != 'object':
        return []
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'

    def proof(members=None, formals='phpType16', context=env, checked=signature):
        syntax = 'phpType18' if members is None else ordered.raw(members, 'stdClass', 'NNameRelative')
        if members is not None:
            checked += '[.RETURNS = ' + ordered.normalized(members, 'stdClass') + ']'
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, ' + formals + ', ' + syntax + ', ' + checked + ')'

    # These are the nine formerly negative pure queries whose scope now expands.
    lines = [proof(['int', 'class', 'null'])]
    for kind in ('float', 'bool', 'string', 'array', 'callable', 'false', 'true', 'iterable'):
        lines.append(proof(['class', kind]))

    # Both eight-member paths are maximal under the existing kind compatibility.
    for members in (
            ['class', 'array', 'int', 'float', 'string', 'null', 'false', 'callable'],
            ['iterable', 'int', 'float', 'class', 'string', 'null', 'true', 'callable']):
        lines.append(proof(members))
    for members in (
            ['class', 'array', 'int', 'float', 'string', 'null', 'false', 'callable', 'iterable'],
            ['class', 'array', 'int', 'float', 'string', 'null', 'bool', 'false', 'callable']):
        lines.append('~' + proof(members))

    alias = json.dumps(base64.b64encode(b'pEeRbOx134').decode())
    context = env + '[.CLASSES = [($ptascii("peerbox134"), $ptascii("stdClass")), ($ptascii("stdclass"), $ptascii("Other"))]]'
    for byref in ('false', 'true'):
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (NName (BYTES ' + alias + ') metadata_function) (BOOLEAN ' + byref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        viewed = parameter.replace('NName (BYTES ' + alias + ')', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")')
        checked = signature + '[.PARAMETERS = [psparam[.BYREF = ' + byref + '][.TYPE = ' + ordered.normalized(['class'], 'stdClass') + ']]]'
        lines += [
            '$reference_notice_producer_scoped_parameter_view(' + context + ', ' + parameter + ') = (' + viewed + ')',
            '$reference_notice_producer_scoped_parameter_view(' + context + ', ' + viewed + ') = (' + viewed + ')',
            proof(formals='SEQUENCE ([' + parameter + '])', context=context, checked=checked),
            proof(formals='SEQUENCE ([' + viewed + '])', context=context, checked=checked),
            '~' + proof(formals='SEQUENCE ([' + parameter + '])', checked=checked),
            '~' + proof(formals='SEQUENCE ([' + parameter + '])', context=context + '[.NAMESPACE = $ptascii("Other")]', checked=checked)]
        if byref == 'false':
            lines.append('~' + proof(formals='SEQUENCE ([' + parameter + '])', context=context))
        if byref == 'true':
            lines.append(proof(['int', 'class', 'null'], formals='SEQUENCE ([' + parameter + '])', context=context, checked=checked))
            for kind in ('float', 'bool', 'string', 'array', 'callable', 'false', 'true', 'iterable'):
                lines.append(proof(['class', kind], formals='SEQUENCE ([' + parameter + '])', context=context, checked=checked))

    lines += [
        '$typed_conversion_at(S_return, ' + signature + '.RETURNS, PINT 37, true) = TYPEREJECT',
        '$typed_conversion_at(S_return, ' + signature + '.RETURNS, PINT 37, false) = TYPESTRING (PINT 37)',
        '$typed_conversion_at(S_return, ' + signature + '.RETURNS, PNULL, true) = TYPEREJECT']
    return lines


def controls(case):
    return author_controls(case) + independent_controls(case)


if __name__ == '__main__':
    driver.controls = controls
    driver.__doc__ = __doc__
    raise SystemExit(0 if driver.main() else 1)

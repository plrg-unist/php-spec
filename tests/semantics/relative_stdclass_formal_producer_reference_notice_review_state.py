#!/usr/bin/env python3
"""Check relative FORMALs with relative RETURNs and exact mixed-formal class bytes."""
import base64
import json

import global_relative_stdclass_formal_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(index, case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    empty = env + '[.CLASSES = eps]'
    shadow = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]]'

    def proof(parameters='phpType16', returns='phpType18', context=env, checked=signature):
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, ' + parameters + ', ' + returns + ', ' + checked + ')'

    relative_return = 'NNameRelative (BYTES "c3RkQ2xhc3M=") metadata_return'
    checked_return = signature + '[.RETURNS = ' + driver.class_type('stdClass') + ']'
    lines = [proof(returns=relative_return, context=empty, checked=checked_return),
        proof(returns=relative_return, context=shadow, checked=checked_return),
        '~' + proof(returns=relative_return),
        '~' + proof(returns=relative_return, context=env + '[.NAMESPACE = $ptascii("Other")]', checked=checked_return)]
    if index == 0:
        byref = 'NParam (SEQUENCE eps) (INTEGER 0) (NNameRelative (BYTES text_formal) metadata_formal) (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        lines.append(proof(parameters='SEQUENCE ([' + byref + '])', returns=relative_return,
            context=shadow, checked=checked_return + '[.PARAMETERS = [psparam[.BYREF = true]]]'))
        for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
                ('(BOOLEAN false) (BOOLEAN false)', '(BOOLEAN true) (BOOLEAN false)'),
                (' ABSENT (SEQUENCE eps)', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps)'),
                ('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_formal]))')):
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (NNameRelative (BYTES text_formal) metadata_formal) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
            lines.append('~' + proof(parameters='SEQUENCE ([' + parameter.replace(before, after, 1) + '])'))
        return lines

    # Source case2 supplies the two actual CVs and independent formal names.
    # This derived signature tests exact syntax authentication, not reception of NULL.
    mixed = json.dumps(base64.b64encode(b'sTdClAsS').decode())
    first = 'NParam (SEQUENCE eps) (INTEGER 0) (NName (BYTES ' + mixed + ') metadata_parameter) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    first_fqn = first.replace('NName ', 'NNameFullyQualified ', 1)
    last_fqn = 'NParam (SEQUENCE eps) (INTEGER 0) (NNameFullyQualified (BYTES "c3RkQ2xhc3M=") metadata_formal) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_parameter_last'
    parameters = 'SEQUENCE ([' + first + ', phpType17_last])'
    mixed_type = driver.class_type('sTdClAsS')
    canonical = driver.class_type('stdClass')
    checked = signature + '[.PARAMETERS = [psparam[.TYPE = ' + mixed_type + '], psparam_last]]'
    view = '$reference_notice_producer_scoped_parameter_view('
    lines += [
        '$reference_notice_producer_global_parameter_view(' + first + ') = (' + first_fqn + ')',
        view + empty + ', ' + first + ') = (' + first + ')',
        view + empty + ', ' + first_fqn + ') = (' + first_fqn + ')',
        view + empty + ', phpType17_last) = (' + last_fqn + ')',
        proof(parameters=parameters, context=empty, checked=checked),
        proof(parameters=parameters.replace(first, first_fqn), context=empty, checked=checked),
        '~' + proof(parameters=parameters, context=empty, checked=checked.replace(mixed_type, canonical)),
        '~' + proof(parameters=parameters, context=empty, checked=checked.replace('psparam_last]', 'psparam_last[.TYPE = ' + mixed_type + ']]')),
        '~' + proof(parameters=parameters, context=shadow, checked=checked),
        proof(parameters=parameters.replace(first, first_fqn), context=shadow, checked=checked),
        '~' + proof(parameters=parameters, context=empty + '[.NAMESPACE = $ptascii("Other")]', checked=checked)]
    imported = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]]'
    lines += ['~' + proof(parameters=parameters, context=imported, checked=checked),
        proof(parameters=parameters, context=imported, checked=checked.replace(mixed_type, canonical))]
    return lines


def controls(index, case):
    return author_controls(index, case) + independent_controls(index, case)


if __name__ == '__main__':
    driver.controls = controls
    driver.__doc__ = __doc__
    raise SystemExit(0 if driver.main() else 1)

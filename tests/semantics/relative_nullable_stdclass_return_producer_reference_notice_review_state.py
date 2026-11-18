#!/usr/bin/env python3
"""Ground nullable relative RETURNs after ordinary formal-alias normalization."""
import base64
import json
from pathlib import Path

import relative_stdclass_return_producer_reference_notice_review_state as previous
import scoped_stdclass_return_producer_reference_notice_review_state as driver

CATALOGUE = Path(__file__).with_name('relative_nullable_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = previous.PREFIX


def normal(initial, case, front):
    original, inherited = previous.normal(initial, case, front)
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    singleton = previous.class_type('stdClass')
    nullable = singleton[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
    imports = '[($ptascii("peerbox"), $ptascii("stdClass")), ($ptascii("stdclass"), $ptascii("PeerRelativeNullable131\\\\Other"))]'
    reached = []
    for line in original:
        if line.startswith(signature + '.RETURNS = '):
            line = signature + '.RETURNS = ' + nullable
        elif line.startswith('phpType17 = '):
            line = line.replace('NNameFullyQualified (BYTES text_formal)', 'NName (BYTES text_formal)', 1)
        elif line.startswith('phpType18 = '):
            line = 'phpType18 = NNullableType (NNameRelative (BYTES text_return) metadata_return) metadata_nullable_return'
        elif line.startswith(env + '.NAMESPACE = '):
            line = env + '.NAMESPACE = eps /\\ ' + env + '.CLASSES = ' + imports
        elif line.startswith('$base64(text_formal) = '):
            line = '$base64(text_formal) = $ptascii("pEeRbOx")'
        elif line.startswith('$ptlc($base64(text_formal)) = '):
            line = '$ptlc($base64(text_formal)) = $ptascii("peerbox")'
        elif line.startswith('$reference_notice_producer_arguments('):
            line = '~' + line
        reached.append(line)
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith((
        '~$error_call_valid(', 'S_zero_', '$drive($drive(S_zero_', '~$named_reference_notice_object('))]
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    viewed = parameter.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    relative = 'NNameRelative (BYTES text_return) metadata_return'
    wrap = lambda raw: 'NNullableType (' + raw + ') metadata_nullable_return'

    def proof(raw='phpType18', formal='phpType17', context=env, returns=None):
        checked = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', SEQUENCE ([phpType7]), SEQUENCE ([' + formal + ']), ' + raw + ', ' + checked + ')'

    helper = lambda context, formal: '$reference_notice_producer_scoped_parameter_view(' + context + ', ' + formal + ')'
    derived += [helper(env, 'phpType17') + ' = (' + viewed + ')',
        helper(env, viewed) + ' = (' + viewed + ')', proof(formal=viewed),
        proof(raw=wrap(relative.replace('NNameRelative', 'NNameFullyQualified'))),
        '~' + proof(raw=wrap(relative.replace('NNameRelative', 'NName'))),
        '~' + proof(raw=wrap(relative.replace('NNameRelative', 'NIdentifier'))),
        '~' + proof(context=env + '[.NAMESPACE = $ptascii("Other")]'),
        '~' + proof(context=env + '[.CLASSES = eps]'),
        proof(formal=viewed, context=env + '[.CLASSES = eps]'),
        proof(formal=viewed, context=env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]]'),
        proof(returns='eps'), proof().replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + proof().replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        proof(raw=wrap(relative).replace('metadata_nullable_return', 'eps')),
        proof(formal=parameter.replace('metadata_parameter', 'eps')),
        '~' + proof(formal=parameter.replace('NName ', 'NNameRelative ', 1)),
        '~' + proof(raw=relative), proof(raw=relative, returns=singleton),
        '~' + proof(raw='NUnionType (SEQUENCE ([' + relative + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_nullable_return')]
    for name in ('Other', 'STDCLASS', 'sTdClAsS', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', '', 'int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NNameRelative (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        derived.append('~' + proof(raw=wrap(raw)))
    wrong = [singleton, previous.class_type('Other')[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]',
        previous.class_type('STDCLASS')[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]',
        '[(PTBRANCH ([PTBUILTIN "null"])), ' + singleton[1:],
        nullable[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]']
    for returns in wrong:
        derived.append('~' + proof(returns=returns))
    for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged nullable relative formal default"'):
        derived.append('~' + proof().replace(signature + ')', signature + '[.PARAMETERS = [psparam[' + update + ']]])'))
    for strict in ('true', 'false'):
        derived += ['$typed_conversion_at(S_return, ' + nullable + ', POBJECT n_old, ' + strict + ') = TYPEVALUE (POBJECT n_old)',
            '$typed_conversion_at(S_return, ' + nullable + ', PNULL, ' + strict + ') = TYPEVALUE PNULL']
        for value in ('PINT 7', 'PBOOL false', 'PSTRING ($ptascii("17"))'):
            derived.append('$typed_conversion_at(S_return, ' + nullable + ', ' + value + ', ' + strict + ') = TYPEREJECT')
    return reached, derived


def main():
    driver.CATALOGUE, driver.PREFIX, driver.normal = CATALOGUE, PREFIX, normal
    driver.__doc__ = __doc__
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

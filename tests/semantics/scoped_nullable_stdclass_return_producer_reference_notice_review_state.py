#!/usr/bin/env python3
"""Ground Param-first nullable FORMAL/RETURN aliases and object private Notice cells."""
import base64
import json
from pathlib import Path

import scoped_stdclass_return_producer_reference_notice_review_state as previous
from global_plain_nullable_stdclass_return_producer_reference_notice_review_state import nullable_type, prior as class_proofs

ROOT = previous.ROOT
CATALOGUE = Path(__file__).with_name('scoped_nullable_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = previous.PREFIX.replace('PeerScopedReturn127', 'PeerScopedNullableReturn128')
ordinary_normal = previous.normal


def normal(initial, case, front):
    original, inherited = ordinary_normal(initial, case, front)
    canonical = nullable_type('stdClass')
    singleton = class_proofs.class_type('stdClass')
    formal = 'NName (BYTES text_formal) metadata_formal'
    nullable_formal = 'NNullableType (' + formal + ') metadata_nullable_formal'
    reached = []
    for line in original:
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + canonical
        elif line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + canonical
        elif line.startswith('phpType17 = '):
            assert formal in line
            line = line.replace(formal, nullable_formal, 1)
        elif line.startswith('phpType18 = '):
            line = 'phpType18 = NNullableType (NName (BYTES text_return) metadata_return) metadata_nullable_return'
        reached.append(line)
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith(('~$error_call_valid(', '~$typed_return_task_valid(', 'S_zero_', '$drive($drive(S_zero_', '~$named_reference_notice_object('))]
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    viewed = parameter.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    raw_name = 'NName (BYTES text_return) metadata_return'
    wrap = lambda raw: 'NNullableType (' + raw + ') metadata_nullable_return'

    def proof(raw='phpType18', parameter_view='phpType17', context_env=env, returns=None):
        checked = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context_env + ', SEQUENCE ([phpType7]), SEQUENCE ([' + parameter_view + ']), ' + raw + ', ' + checked + ')'

    helper = lambda raw: '$reference_notice_producer_scoped_parameter_view(' + env + ', ' + raw + ')'
    scoped = proof()
    derived += [helper('phpType17') + ' = (' + viewed + ')', helper(viewed) + ' = (' + viewed + ')',
        scoped, proof(parameter_view=viewed), proof(raw=wrap('NNameFullyQualified (BYTES "c3RkQ2xhc3M=") metadata_return')),
        proof(returns='eps'), scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        proof(context_env=env + '[.NAMESPACE = eps]'), proof(context_env=env + '[.NAMESPACE = $ptascii("Other")]'),
        '~' + proof(context_env=env + '[.CLASSES = eps]'),
        '~' + proof(context_env=env + '[.NAMESPACE = eps][.CLASSES = eps]')]
    for spelling in ('PeerBox', 'pEeRbOx', 'PEERBOX'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(spelling.encode()).decode()) + ') metadata_return'
        derived.append(proof(raw=wrap(raw)))
    for tag in ('NNameFullyQualified', 'NNameRelative', 'NIdentifier'):
        derived.append('~' + proof(raw=wrap(raw_name.replace('NName ', tag + ' ', 1))))
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', 'int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        derived.append('~' + proof(raw=wrap(raw)))
    for name in ('int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        fake = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        derived.append('~' + proof(raw=wrap(raw), parameter_view=viewed, context_env=fake))
    for target in ('Other', 'STDCLASS', 'StDcLaSs'):
        fake = env + '[.CLASSES = [($ptascii("peerbox"), $ptascii(' + json.dumps(target) + '))]]'
        derived.append('~' + proof(parameter_view=viewed, context_env=fake))
    for returns in (nullable_type('Other'), nullable_type('STDCLASS'), singleton,
            '[(PTBRANCH ([PTBUILTIN "null"])), ' + singleton[1:], canonical[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        derived.append('~' + proof(returns=returns))
    derived += ['~' + proof(raw=raw_name),
        proof(raw='NUnionType (SEQUENCE ([' + raw_name + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_nullable_return'),
        proof(raw='NNullableType (NName (BYTES text_return) eps) metadata_nullable_return'),
        proof(raw='NNullableType (' + raw_name + ') eps'),
        proof(parameter_view=parameter.replace('metadata_nullable_formal', 'eps'))]
    for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged nullable scoped return formal default"'):
        derived.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = [psparam[' + update + ']]])'))
    for strict in ('true', 'false'):
        derived += ['$typed_conversion_at(S_return, ' + signature + '.RETURNS, PNULL, ' + strict + ') = TYPEVALUE PNULL',
            '$typed_conversion_at(S_return, ' + signature + '.RETURNS, POBJECT n_old, ' + strict + ') = TYPEVALUE (POBJECT n_old)',
            '$typed_conversion_at(S_return, ' + signature + '.RETURNS, PINT 7, ' + strict + ') = TYPEREJECT']
    return reached, derived


def main():
    previous.CATALOGUE, previous.PREFIX, previous.normal = CATALOGUE, PREFIX, normal
    previous.__doc__ = __doc__
    return previous.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

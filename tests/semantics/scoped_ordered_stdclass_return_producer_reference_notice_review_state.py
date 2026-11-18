#!/usr/bin/env python3
"""Ground opposite ordered FORMAL/RETURN alias unions and private object Notice cells."""
import base64
import json
from pathlib import Path

import scoped_nullable_stdclass_return_producer_reference_notice_review_state as previous
from global_plain_nullable_stdclass_return_producer_reference_notice_review_state import nullable_type, prior as class_proofs

ROOT = previous.ROOT
CATALOGUE = Path(__file__).with_name('scoped_ordered_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = previous.PREFIX.replace('PeerScopedNullableReturn128', 'PeerScopedOrderedReturn129')
nullable_normal = previous.normal


def normal(initial, case, front):
    original, inherited = nullable_normal(initial, case, front)
    singleton = class_proofs.class_type('stdClass')
    class_first = nullable_type('stdClass')
    null_first = '[(PTBRANCH ([PTBUILTIN "null"])), ' + singleton[1:]
    class_name = 'NName (BYTES text_return) metadata_return'
    null_name = 'NIdentifier (BYTES text_return_null) metadata_return_null'
    members = '[' + null_name + ', ' + class_name + ']'
    union = lambda sequence: 'NUnionType (SEQUENCE (' + sequence + ')) metadata_union_return'
    formal = 'NName (BYTES text_formal) metadata_formal'
    old_formal = 'NNullableType (' + formal + ') metadata_nullable_formal'
    union_formal = 'NUnionType (SEQUENCE ([' + formal + ', NIdentifier (BYTES text_formal_null) metadata_formal_null])) metadata_union_formal'
    reached = []
    for line in original:
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + null_first
        elif line.startswith('phpType17 = '):
            assert old_formal in line
            line = line.replace(old_formal, union_formal, 1)
        elif line.startswith('phpType18 = '):
            line = 'phpType18 = ' + union(members)
        reached.append(line)
    reached += ['$ptlc($base64(text_formal_null)) = $ptascii("null")',
        '$ptlc($base64(text_return_null)) = $ptascii("null")']
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith(('~$error_call_valid(', '~$typed_return_task_valid(', 'S_zero_', '$drive($drive(S_zero_', '~$named_reference_notice_object(', '$typed_conversion_at('))]
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    viewed = parameter.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    viewed_members = members.replace('NName (BYTES text_return)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)

    def proof(raw='phpType18', parameter_view='phpType17', context=env, returns=None):
        sig = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', SEQUENCE ([phpType7]), SEQUENCE ([' + parameter_view + ']), ' + raw + ', ' + sig + ')'

    view = lambda sequence, context=env, seen='false': '$reference_notice_producer_scoped_return_union_view(' + context + ', ' + sequence + ', ' + seen + ')'
    scoped = proof()
    derived += ['$reference_notice_producer_scoped_parameter_view(' + env + ', phpType17) = (' + viewed + ')',
        view(members) + ' = (' + viewed_members + ')',
        view(members, seen='true') + ' = eps', view('eps') + ' = eps', view('eps', seen='true') + ' = (eps)',
        scoped, proof(parameter_view=viewed), proof(raw=union(viewed_members)), proof(returns='eps'),
        scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        proof(context=env + '[.NAMESPACE = eps]'), proof(context=env + '[.NAMESPACE = $ptascii("Other")]'),
        '~' + proof(context=env + '[.CLASSES = eps]'), '~' + proof(context=env + '[.NAMESPACE = eps][.CLASSES = eps]')]
    reversed_members = '[' + class_name + ', ' + null_name + ']'
    derived += [proof(raw=union(reversed_members), returns=class_first), '~' + proof(raw=union(reversed_members)),
        '~' + proof(returns=class_first), '~' + proof(returns=singleton),
        view('[' + class_name + ', ' + class_name + ']') + ' = eps']
    for spelling in ('PeerBox', 'pEeRbOx', 'PEERBOX'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(spelling.encode()).decode()) + ') metadata_return'
        derived.append(proof(raw=union('[' + null_name + ', ' + raw + ']')))
    for tag in ('NNameFullyQualified', 'NNameRelative', 'NIdentifier'):
        changed = members.replace('NName ', tag + ' ', 1)
        derived += [view(changed) + ' = eps', '~' + proof(raw=union(changed))]
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', 'int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        derived.append('~' + proof(raw=union('[' + null_name + ', ' + raw + ']')))
    for name in ('int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        fake = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        derived.append('~' + proof(raw=union('[' + null_name + ', ' + raw + ']'), parameter_view=viewed, context=fake))
    for target in ('Other', 'STDCLASS', 'StDcLaSs'):
        fake = env + '[.CLASSES = [($ptascii("peerbox"), $ptascii(' + json.dumps(target) + '))]]'
        derived += [view(members, fake) + ' = eps', '~' + proof(parameter_view=viewed, context=fake)]
    for returns in ('[(PTBRANCH ([PTBUILTIN "null"])), ' + class_proofs.class_type('Other')[1:],
            '[(PTBRANCH ([PTBUILTIN "null"])), ' + class_proofs.class_type('STDCLASS')[1:],
            null_first[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        derived.append('~' + proof(returns=returns))
    derived += [proof(raw=union(members).replace('metadata_union_return', 'eps')),
        proof(raw=union(members).replace('metadata_return_null', 'eps')),
        proof(parameter_view=parameter.replace('metadata_union_formal', 'eps'))]
    return reached, derived


def main():
    previous.CATALOGUE, previous.PREFIX, previous.normal = CATALOGUE, PREFIX, normal
    previous.__doc__ = __doc__
    return previous.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

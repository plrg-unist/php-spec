#!/usr/bin/env python3
"""Check actual NULL reception, relative-only views and existing union conversions."""
import global_relative_nullable_ordered_stdclass_formal_producer_reference_notice_state as driver

author_controls = driver.controls


def independent_controls(index, case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    lines = []
    if case['nullable_first']:
        lines += ['$pfn_receive_seek(S_received_first, 1, 5000)[.COMPLETION = NORMAL] = S_receive',
            'S_received_first.OBJECTPROPS = S_receive_first.OBJECTPROPS',
            'n_first =/= n_receive',
            '~$typed_receive_valid(S_receive_first, porigin_first, 1)']
    if index == 0:
        # These four views replace the old135 identity expectations. The old bare
        # checked TYPE still rejects both wrapper forms, for either BYREF flag.
        for byref in ('false', 'true'):
            for typename in (
                    'NNullableType (NNameRelative (BYTES text_formal) metadata_formal) metadata_formal',
                    'NUnionType (SEQUENCE ([NNameRelative (BYTES text_formal) metadata_formal, NIdentifier (BYTES "bnVsbA==") metadata_formal])) metadata_formal'):
                parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + typename + ') (BOOLEAN ' + byref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
                viewed = parameter.replace('NNameRelative (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")')
                checked = signature + '[.PARAMETERS = [psparam[.BYREF = ' + byref + '][.TYPE = ' + driver.class_type('stdClass') + ']]]'
                lines += ['$reference_notice_producer_scoped_parameter_view(' + env + ', ' + parameter + ') = (' + viewed + ')',
                    '~$reference_notice_producer_scoped_header(' + env + ', phpType6_producer, SEQUENCE ([' + parameter + ']), phpType18, ' + checked + ')']
        return lines
    if case['shape'] != 'union':
        return lines

    normalized = driver.ordered.branches(case['formal_members'], 'stdClass')
    for strict in ('true', 'false'):
        lines.append('$typed_conversion_at(S_receive, ' + normalized + ', POBJECT n_object_receive, ' + strict + ') = TYPEVALUE (POBJECT n_object_receive)')
    if case['formal_members'] == ['class', 'null']:
        for strict in ('true', 'false'):
            lines += ['$typed_conversion_at(S_receive, ' + normalized + ', PNULL, ' + strict + ') = TYPEVALUE PNULL',
                '$typed_conversion_at(S_receive, ' + normalized + ', PINT 37, ' + strict + ') = TYPEREJECT']
        return lines
    lines += ['$typed_conversion_at(S_receive, ' + normalized + ', PINT 37, true) = TYPEREJECT',
        '$typed_conversion_at(S_receive, ' + normalized + ', PINT 37, false) = TYPESTRING (PINT 37)']
    raw = lambda members, tag='NNameRelative': driver.ordered.raw_type(members, 'stdClass', tag, indexed=False)
    members = lambda expression: expression.removeprefix('NUnionType (SEQUENCE (').removesuffix(')) metadata_formal_union')
    union_view = '$reference_notice_producer_relative_parameter_union_view('
    def view(items, context=env, seen='false'):
        return union_view + context + ', ' + items + ', ' + seen + ')'
    original = members(raw(case['formal_members']))
    canonical = members(raw(case['formal_members'], 'NNameFullyQualified'))
    lines += [view(original) + ' = (' + canonical + ')',
        view(original, env + '[.CLASSES = eps]') + ' = (' + canonical + ')',
        view(original, env + '[.NAMESPACE = $ptascii("Other")]') + ' = eps',
        view(original, seen='true') + ' = eps',
        view('eps') + ' = eps', view('eps', seen='true') + ' = (eps)',
        view(original.replace(' metadata_formal', ' eps')) + ' = (' + canonical.replace(' metadata_formal', ' eps') + ')',
        view(members(raw(['class', 'class']))) + ' = eps',
        view(members(raw(['int', 'float']))) + ' = eps']
    for tag in ('NName', 'NNameFullyQualified', 'NIdentifier'):
        lines.append(view(members(raw(case['formal_members'], tag))) + ' = eps')
    relative = 'NNameRelative (BYTES "c3RkQ2xhc3M=") metadata_formal'
    ordinary = relative.replace('NNameRelative', 'NName')
    nested = 'NIntersectionType (SEQUENCE ([' + relative + '])) metadata_formal'
    lines += [view('[' + relative + ', ' + ordinary + ']') + ' = eps',
        view('[' + relative + ', ' + nested + ']') + ' = eps']
    for name in ('"T3RoZXI="', '"U1REQ0xBU1M="', '"c3RkQ2xhc3MA"'):
        lines.append(view(original.replace('"c3RkQ2xhc3M="', name)) + ' = eps')
    # Identifier validation stays in the unchanged FQN folds, after the view.
    items = members(raw(['class', 'object']))
    lines.append(view(items) + ' = (' + items.replace('NNameRelative', 'NNameFullyQualified') + ')')
    parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw(['class', 'object']) + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    checked = signature + '[.PARAMETERS = [psparam[.TYPE = ' + driver.ordered.branches(['class', 'object'], 'stdClass') + ']]]'
    lines.append('~$reference_notice_producer_scoped_header(' + env + ', phpType6_producer, SEQUENCE ([' + parameter + ']), phpType18, ' + checked + ')')
    return lines


def controls(index, case):
    return author_controls(index, case) + independent_controls(index, case)


if __name__ == '__main__':
    driver.controls = controls
    driver.__doc__ = __doc__
    raise SystemExit(0 if driver.main() else 1)

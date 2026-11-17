#!/usr/bin/env python3
"""Independent full union authority, reached tags, array COW and source removal."""
from pathlib import Path

import class_array_union_parentless_short_reference_get_hook_review_state as prior
import class_builtin_union_parentless_short_reference_get_hook_review_protocol as headers

runner = prior.runner


def raw_type(case):
    members = []
    for member in case['raw_members']:
        if member is None:
            members.append(case['raw_kind'] + ' (BYTES text_raw) metadata_raw')
        else:
            members.append('NIdentifier (BYTES text_' + member + ') metadata_' + member)
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) metadata_union'


def fields(fixture, source, case):
    adapted = {**case, 'default': '[]'}
    checks = prior.fields(fixture, source, adapted)
    name = case['class_name'].encode()
    array_first = case['raw_order'] == 'array-class'
    substitutions = [
        (prior.headers.mask(name, array_first), headers.mask(name, case['raw_members'])),
        (prior.headers.mask(name.swapcase(), array_first), headers.mask(name.swapcase(), case['raw_members'])),
        (prior.headers.mask(name, not array_first), headers.mask(name, list(reversed(case['raw_members'])))),
    ]
    rows = []
    for check in checks:
        if check.startswith('phpType18 = NUnionType'):
            check = 'phpType18 = ' + raw_type(case)
        check = check.replace('$hook_short_reference_class_array_header(', headers.HELPER + '(')
        for before, after in substitutions:
            check = check.replace(before, after)
        if case['default'] == 'null':
            if check in ('S_front.ARRAYS[n_initial].ITEMS = eps', 'S_fetch.ARRAYS[n_fetcharray].ITEMS = eps'):
                continue
            check = check.replace('PARRAY n_initial', 'PNULL').replace('PARRAY n_fetcharray', 'PNULL')
        rows.append(check)
        if check == headers.HELPER + '(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows.append('~$hook_short_reference_class_array_header(phpType18,ppropertydesc.TYPE,ptcontext_property)')
    lines = [line.strip() for line in source.read_text().splitlines()]
    at = next(i for i, row in enumerate(rows) if row.startswith('S_array_cow = $lbr_seek('))
    reached = []
    previous = 'S_aliases'
    for i, stage in enumerate(case['reached']):
        state = 'S_reached' + str(i)
        marker = lines.index(stage['marker']) + 1
        reached += [state + ' = $lbr_seek(' + previous + ',' + str(marker) + ',30000)',
                    '$lbr_phase(' + state + ',' + str(marker) + ')', state + '.COMPLETION = NORMAL',
                    state + '.STORE[n_field] = DEFINED (' + stage['value'] + ')',
                    '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                    '$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
                    '$heap_valid($heap_prune($heap_graph(' + state + ')))']
        previous = state
    rows[at] = rows[at].replace('$lbr_seek(S_aliases,', '$lbr_seek(' + previous + ',')
    rows[at:at] = reached
    rows = [row.replace('S_detached = $lbr_seek(S_aliases,', 'S_detached = $lbr_seek(S_array_cow,') for row in rows]
    if case.get('free_object'):
        at = rows.index('S_end = $drive_steps(S_detached,30000)')
        marker = lines.index('$r322 = [];') + 1
        rows[at:at] = [
            'S_untyped = $lbr_seek(S_detached,' + str(marker) + ',30000)',
            '$lbr_phase(S_untyped,' + str(marker) + ')', 'S_untyped.COMPLETION = NORMAL',
            'S_untyped.STORE[n_field] = DEFINED (POBJECT n_free)',
            '$propref_at(S_untyped.PROPREFS,n_field) = eps',
            '~$typed_object_exact(S_untyped,ppropertydesc.TYPE,POBJECT n_free)',
            '$property_state_valid(S_untyped)', '$call_descriptors_valid(S_untyped)',
            '$heap_valid($heap_prune($heap_graph(S_untyped)))',
        ]
        rows = [row.replace('S_end = $drive_steps(S_detached,30000)', 'S_end = $drive_steps(S_untyped,30000)') for row in rows]
        rows.append('~((HOBJECT n_free) <- S_end.ALLOCATIONS)')
    assert sum(row.startswith('phpType18 = NUnionType') for row in rows) == 1
    if case['default'] == 'null':
        assert not any('n_initial' in row or 'n_fetcharray' in row for row in rows)
    return rows


if __name__ == '__main__':
    runner.PREFIX = runner.PREFIX.replace('def $lbr_phase(S,z) = false -- otherwise', r"""def $lbr_phase(S,z) = true
  -- if $(z > 0)
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("arraycopy322")
  -- if $source_line(metadata) = z
def $lbr_phase(S,z) = false -- otherwise""")
    runner.STEM = 'class_builtin_union_parentless_short_reference_get_hook'
    runner.fields = fields
    watched = [Path(headers.__file__)]
    module = prior
    while True:
        watched.append(Path(module.__file__))
        if hasattr(module, 'headers'):
            watched.append(Path(module.headers.__file__))
        if not hasattr(module, 'prior'):
            break
        module = module.prior
    runner.main(extra_paths=watched)

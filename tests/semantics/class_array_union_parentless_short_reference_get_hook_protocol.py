#!/usr/bin/env python3
"""Check class/array headers, real aliases, copied arrays and owner retirement."""
from pathlib import Path
import class_int_union_parentless_short_reference_get_hook_protocol as prior


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('array', 'int')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('$hook_short_reference_class_int_header(', '$hook_short_reference_class_array_header(')
        check = check.replace('text_int', 'text_array')
        check = check.replace('PTBUILTIN "int"', 'PTBUILTIN "array"').replace('$ptascii("int")', '$ptascii("array")')
        check = check.replace('PINT 0', 'PARRAY n_initial_fetch')
        rows.append(check)
        if check == '$hook_short_reference_class_array_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += [
                '~$hook_short_reference_class_int_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_float_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_string_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
                'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PARRAY n_initial_front))',
                'S_front.ARRAYS[n_initial_front].ITEMS = eps',
                'phpType5 = NExprArray (SEQUENCE eps) metadata_default',
            ]
        if check == 'S_fetch.STORE[n_field] = DEFINED (PARRAY n_initial_fetch)':
            rows.append('S_fetch.ARRAYS[n_initial_fetch].ITEMS = eps')
    lines = [line.strip() for line in source.read_text().splitlines()]
    item = '[ENTRY (KINT 0) (DIRECT (PINT 137))]'
    previous = 'S_aliases'
    for state, marker in (('S_array', '$arraycopy322 = $box322->v;'),
                          ('S_array_cow', next(line for line in lines if line.startswith('$box322->v = new ')))):
        n_line = lines.index(marker) + 1
        rows += [
            f'{state} = $lbr_seek({previous},{n_line},30000)', f'$lbr_phase({state},{n_line})',
            f'{state}.COMPLETION = NORMAL', f'{state}.STORE[n_field] = DEFINED (PARRAY n_array_live)',
            f'{state}.ARRAYS[n_array_live].ITEMS = {item}',
            f'$propref_at({state}.PROPREFS,n_field) = (ppropref)',
            f'$heap_owners($heap_graph({state}),HCELL n_field) = 3',
            f'$property_state_valid({state})', f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_prune($heap_graph({state})))',
        ]
        previous = state
    rows += [
        '$lookup(S_array_cow.ENV,$ptascii("arraycopy322")) = (n_arraycopy_cell)',
        'S_array_cow.STORE[n_arraycopy_cell] = DEFINED (PARRAY n_arraycopy)',
        'n_arraycopy =/= n_array_live',
        'S_array_cow.ARRAYS[n_arraycopy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 139))]',
        '$propref_at(S_array_cow.PROPREFS,n_arraycopy_cell) = eps',
        '$heap_owners($heap_graph(S_array_cow),HARRAY n_arraycopy) = 1',
        '~((HARRAY n_arraycopy) <- S_end.ALLOCATIONS)',
        '~((HCELL n_arraycopy_cell) <- S_end.ALLOCATIONS)',
    ]
    return rows


if __name__ == '__main__':
    runner = prior.prior.prior.prior.runner
    runner.STEM = 'class_array_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__),
                            Path(prior.prior.prior.__file__), Path(prior.prior.prior.prior.__file__),
                            Path(prior.prior.prior.prior.prior.__file__),
                            Path(prior.prior.prior.prior.headers.__file__)])

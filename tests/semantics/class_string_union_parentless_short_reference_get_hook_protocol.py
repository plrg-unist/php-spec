#!/usr/bin/env python3
"""Check class/string headers, quiet scalar conversion and real aliases."""
from pathlib import Path
import class_int_union_parentless_short_reference_get_hook_protocol as prior


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('string', 'int')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('$hook_short_reference_class_int_header(', '$hook_short_reference_class_string_header(')
        check = check.replace('text_int', 'text_string')
        check = check.replace('PTBUILTIN "int"', 'PTBUILTIN "string"').replace('$ptascii("int")', '$ptascii("string")')
        check = check.replace('PINT 0', 'PSTRING eps')
        rows.append(check)
        if check == '$hook_short_reference_class_string_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += [
                '~$hook_short_reference_class_int_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_float_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
                'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PSTRING eps))',
                'phpType5 = NScalarString (BYTES text_default) metadata_default',
                '$base64(text_default) = eps',
            ]
    lines = [line.strip() for line in source.read_text().splitlines()]
    one = {'fq-class-string': '$r322 = true;', 'string-local-class': '$r322 = 1;',
           'imported-class-string': '$r322 = 1.0;'}[source.stem]
    after = next(line for line in lines if line.startswith('$box322->v = new '))
    zero = '' if source.stem == 'fq-class-string' else '0'
    previous = 'S_aliases'
    for state, marker, value in (('S_string_zero', one, zero), ('S_string_one', after, '1')):
        n_line = lines.index(marker) + 1
        rows += [
            f'{state} = $lbr_seek({previous},{n_line},30000)', f'$lbr_phase({state},{n_line})',
            f'{state}.COMPLETION = NORMAL', f'{state}.STORE[n_field] = DEFINED pvalue_{state}',
            f'$string_bytes(pvalue_{state}) = ($ptascii("{value}"))',
            f'$string_carrier_valid({state},pvalue_{state})',
            f'$propref_at({state}.PROPREFS,n_field) = (ppropref)',
            f'$heap_owners($heap_graph({state}),HCELL n_field) = 3',
            f'$property_state_valid({state})', f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_prune($heap_graph({state})))',
        ]
        previous = state
    return rows


if __name__ == '__main__':
    runner = prior.prior.prior.prior.runner
    runner.STEM = 'class_string_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__),
                            Path(prior.prior.prior.__file__), Path(prior.prior.prior.prior.__file__),
                            Path(prior.prior.prior.prior.prior.__file__),
                            Path(prior.prior.prior.prior.headers.__file__)])

#!/usr/bin/env python3
"""Independent array-union authority, array value copies and alias retirement."""
from pathlib import Path

import class_false_union_parentless_short_reference_get_hook_review_state as prior
import class_array_union_parentless_short_reference_get_hook_review_protocol as headers

runner = prior.runner


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('array', 'false')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('PTBUILTIN "false"', 'PTBUILTIN "array"')
        check = check.replace('$hook_short_reference_class_false_header(', '$hook_short_reference_class_array_header(')
        check = check.replace('text_false', 'text_array').replace('$ptascii("false")', '$ptascii("array")')
        check = check.replace('PBOOL false', 'PARRAY n_initial')
        rows.append(check)
        if check == 'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PARRAY n_initial))':
            rows.append('S_front.ARRAYS[n_initial].ITEMS = eps')
        if check == 'S_fetch.RESULT = REFERENCE n_field':
            rows += ['S_fetch.STORE[n_field] = DEFINED (PARRAY n_fetcharray)', 'S_fetch.ARRAYS[n_fetcharray].ITEMS = eps']
        if check == '$hook_short_reference_class_array_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += [
                '~$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_true_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_bool_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_int_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_float_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_string_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
            ]
            for kind in ('true', 'false'):
                branches = headers.mask(case['class_name'].encode(), case['raw_order'] == 'array-class').replace('PTBUILTIN "array"', 'PTBUILTIN "' + kind + '"')
                rows += [
                    '~$hook_short_reference_class_array_header(phpType18,' + branches + ',ptcontext_property)',
                    '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + branches + '])',
                ]
    lines = [line.strip() for line in source.read_text().splitlines()]
    at = rows.index('~$property_state_valid(S_aliases[.PROPREFS = eps])') + 1
    marker = lines.index('unset($arraycopy322);') + 1
    checks = ['S_array_cow = $lbr_seek(S_aliases,' + str(marker) + ',30000)',
              '$lbr_phase(S_array_cow,' + str(marker) + ')', 'S_array_cow.COMPLETION = NORMAL',
              'S_array_cow.STORE[n_field] = DEFINED (PARRAY n_fieldarray)',
              '$lookup(S_array_cow.ENV,$ptascii("arraycopy322")) = (n_copycell)',
              'S_array_cow.STORE[n_copycell] = DEFINED (PARRAY n_copyarray)',
              'n_fieldarray =/= n_copyarray',
              'S_array_cow.ARRAYS[n_fieldarray].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 193))]',
              'S_array_cow.ARRAYS[n_copyarray].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 197))]',
              '$propref_at(S_array_cow.PROPREFS,n_field) = (ppropref)',
              '$propref_at(S_array_cow.PROPREFS,n_copycell) = eps',
              '$property_state_valid(S_array_cow)', '$call_descriptors_valid(S_array_cow)',
              '$heap_valid($heap_prune($heap_graph(S_array_cow)))']
    rows[at:at] = checks
    rows.append('~((HARRAY n_copyarray) <- S_end.ALLOCATIONS)')
    assert any('text_array' in row for row in rows)
    assert 'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PARRAY n_initial))' in rows
    return rows


if __name__ == '__main__':
    runner.PREFIX = runner.PREFIX.replace('def $lbr_phase(S,z) = false -- otherwise', r'''def $lbr_phase(S,z) = true
  -- if $(z > 0)
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("arraycopy322")
  -- if $source_line(metadata) = z
def $lbr_phase(S,z) = false -- otherwise''')
    runner.STEM = 'class_array_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__), Path(prior.headers.__file__),
                            Path(prior.prior.headers.__file__), Path(prior.prior.prior.__file__),
                            Path(prior.prior.prior.headers.__file__), Path(headers.__file__)])

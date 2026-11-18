#!/usr/bin/env python3
"""Check literal-this backing, direct CV source, aliases and return authority."""
from pathlib import Path

import mixed_nominal_union_parentless_short_reference_get_hook_protocol as prior


def fields(fixture, source, case):
    checks = prior.fields(fixture, source, case)
    old = 'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this)'
    new = 'expression_get = NExprPropertyFetch (NExprVariable (NScalarString (BYTES text_this) metadata_receiver_string) metadata_this)'
    selected = [i for i, check in enumerate(checks) if check.startswith(old)]
    assert len(selected) == 1
    checks[selected[0]] = checks[selected[0]].replace(old, new, 1)
    body_line = next(i + 2 for i, line in enumerate(source.read_text().splitlines()) if '&get =>' in line)
    z = str(body_line)
    checks += [
        '$hook_short_reference_literal_this_body(expression_get,ppropertydesc.NAME)',
        '~$hook_short_reference_body(expression_get,ppropertydesc.NAME)',
        '$hook_literal_this(NExprVariable (NScalarString (BYTES text_this) metadata_receiver_string) metadata_this)',
        '$hook_body_backed(expression_get,ppropertydesc.NAME)',
        '$source_line(metadata_receiver_string) = ' + z,
        '$cv_name_at(NScalarString (BYTES text_this) metadata_receiver_string,14) = ($ptascii("this"))',
        '$origin_node(S_front.SOURCES,PORIGIN n_source (pfunction.BODY ++ [PCFIELD 0,PCFIELD 0])) = (NScalarString (BYTES text_this) metadata_receiver_string)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY ++ [PCFIELD 0,PCFIELD 0]) = eps',
        '$property_hook_reference_expression_return(S_return,pfunction.ORIGIN,' + z + ') = (expression_get)',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '$property_hook_reference_expression_return(S_noarrow,pfunction.ORIGIN,' + z + ') = eps',
        '~$reference_return_source(S_noarrow,' + z + ')',
        '~$reference_return_fetch_valid(S_noarrow,' + z + ')',
        '~$call_task_valid(S_noarrow,RETURN_REF_FETCH ' + z + ')']
    return checks


def main():
    runner = prior.runner
    runner.PREFIX = runner.PREFIX.replace('box320', 'box335').replace('a320', 'r335').replace('b320', 's335')
    runner.PREFIX = runner.PREFIX.replace('$property_hook_plan(S) =/= eps', '$property_hook_ref_plan(S) =/= eps')
    runner.PREFIX = runner.PREFIX.replace('(PROPERTY_HOOK_RESULT ppropertyhook)', '(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch")')
    runner.STEM = 'literal_this_receiver_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(__file__), Path(prior.__file__), Path(prior.names.__file__)])


if __name__ == '__main__':
    main()

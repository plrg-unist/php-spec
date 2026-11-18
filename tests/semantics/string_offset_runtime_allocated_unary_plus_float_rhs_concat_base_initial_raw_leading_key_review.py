"""Reached single-unary FLOAT RHSs retain exact one-row cast allocation."""

import string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_review as raw
from string_offset_retained_carrier_protocol import lines


def unary_checks(text, reference):
    marker = '  -- if ' if '  -- if ' in text else ''
    before = 'expression_right_number = NScalarFloat (FLOAT text_right_bits) metadata_right_number'
    after = 'expression_right_number = NExprUnaryPlus (NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_right_number'
    assert text.count(before) == 1
    text = text.replace(before, after)
    extra = lines('''
$origin_child((porigin_right_number),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_atom) = (NScalarFloat (FLOAT text_right_bits) metadata_atom)
porigin_atom = PORIGIN n_unit pcpath_atom
porigin_right_number = PORIGIN n_unit pcpath_right_number
$code_expression(pcode.EXPRESSIONS,pcpath_right_number) = ((z_unary,true))
$(z_unary > 0)
''')
    before = marker + 'S_capture.POOLS = [ppool]'
    assert text.count(before) == 1
    text = text.replace(before, before + '\n' + '\n'.join(marker + check for check in extra))
    return text, len(extra)


def front(program, filename_b64, reference=False):
    prefix, checks = raw.front(program, filename_b64, reference=reference)
    text, _ = unary_checks('\n'.join(checks), reference)
    return prefix, text.splitlines()


def render(program, filename_b64, reference=False):
    body, count, derived = raw.render(program, filename_b64, reference=reference)
    body, added = unary_checks(body, reference)
    checks = lines('''
S_atom_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_atom (NScalarFloat (FLOAT text_right_bits) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_value(S_atom_source,porigin_base,pvalue_base)
$string_read_plan(S_atom_source) = eps
S_atom_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom PNULL) :: ppool.CONSTANTS]]]
$string_read_allocated_value(S_atom_pool,porigin_base,pvalue_base)
$string_read_plan(S_atom_pool) = (pstringread)
S_unary_line = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number 0 false) :: pcode.EXPRESSIONS]]]
~$string_read_allocated_value(S_unary_line,porigin_base,pvalue_base)
$string_read_plan(S_unary_line) = eps
S_unary_fold = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number z_unary false) :: pcode.EXPRESSIONS]]]
$string_read_allocated_value(S_unary_fold,porigin_base,pvalue_base)
$string_read_plan(S_unary_fold) = (pstringread)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + added + len(checks), derived + len(checks)

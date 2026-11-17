"""A selected emitted NULL arm preserves the outer false raw-string base."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond) (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false)'
    new = 'NExprTernary expression_cond (NScalarString (BYTES text_false) metadata_false) (NScalarString (BYTES text_true) metadata_true)'
    assert body.count(old) == 1
    body = body.replace(old, new)
    body = body.replace('[PCFIELD 1]', '[PCFIELD 99]').replace('[PCFIELD 2]', '[PCFIELD 1]').replace('[PCFIELD 99]', '[PCFIELD 2]')
    for old, new in (('porigin_true', 'porigin_selected'), ('porigin_false', 'porigin_skipped'),
                     ('text_true', 'text_selected'), ('text_false', 'text_skipped'),
                     ('metadata_true', 'metadata_selected'), ('metadata_false', 'metadata_skipped')):
        body = body.replace(old, new)
    anchor = '  -- if $compiled_read(S_capture,porigin_cond) = (PINT 1)\n'
    assert body.count(anchor) == 1
    early = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
S_capture.CODE = [pcode]
pcode.UNIT = n_unit
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond)
expression_cond = NExprTernary expression_inner expression_null expression_unused metadata_cond
expression_inner = NExprCastInt expression_inner_leaf metadata_inner
expression_inner_leaf = NScalarInt (INTEGER 1) metadata_inner_leaf
expression_null = NExprConstFetch name_null metadata_null
expression_unused = NScalarInt (INTEGER 1) metadata_unused
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_inner_leaf)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_null)
$origin_child((porigin_cond),[PCFIELD 2]) = (porigin_unused)
$origin_node(S_capture.SOURCES,porigin_inner) = (expression_inner)
$origin_node(S_capture.SOURCES,porigin_inner_leaf) = (expression_inner_leaf)
$origin_node(S_capture.SOURCES,porigin_null) = (expression_null)
$origin_node(S_capture.SOURCES,porigin_unused) = (expression_unused)
$compiled_read(S_capture,porigin_cond) = eps
$compiled_read(S_capture,porigin_inner) = eps
$compiled_read(S_capture,porigin_inner_leaf) = (PINT 1)
$compiled_read(S_capture,porigin_null) = (PNULL)
$compiled_read(S_capture,porigin_unused) = (PINT 1)
$compiled_precision(S_capture,(porigin_cond)) = (z_precision)
$compiled_precision(S_capture,(porigin_inner)) = (z_precision)
$compiled_precision(S_capture,(porigin_inner_leaf)) = (z_precision)
$compiled_precision(S_capture,(porigin_null)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_inner) = (PINT 1)
$truth_value(S_capture,PINT 1,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_null) = (PNULL)
$string_read_runtime_value(S_capture,porigin_cond) = (PNULL)
$truth_value(S_capture,PNULL,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
''')
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early))
    body = body.replace('$truth(S_capture,PINT 1)', '~$truth(S_capture,PNULL)')
    body = body.replace('pvalue_condition = PINT 1', 'pvalue_condition = PNULL')
    for state in ('S_wrong_condition', 'S_wrong_condition_value'):
        start = body.index('  -- if ' + state + ' = ')
        end = body.index('\n', start)
        body = body[:end] + '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 12 true) :: pcode.EXPRESSIONS]]]' + body[end:]
    checks = lines(r'''
porigin_inner = PORIGIN n_unit pcpath_inner
porigin_inner_leaf = PORIGIN n_unit pcpath_inner_leaf
porigin_null = PORIGIN n_unit pcpath_null
porigin_unused = PORIGIN n_unit pcpath_unused
S_capture.SOURCES = [pcunit]
S_budget_null = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_budget_null,porigin_cond) = eps
$string_read_raw_known_base(S_budget_null,porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('condition', 'pcpath_cond', 'NExprTernary expression_inner expression_null expression_unused eps'),
            ('inner', 'pcpath_inner', 'NExprCastInt expression_inner_leaf eps'),
            ('inner_leaf', 'pcpath_inner_leaf', 'NScalarInt (INTEGER 1) eps'),
            ('null', 'pcpath_null', 'NExprConstFetch name_null eps'),
            ('unused', 'pcpath_unused', 'NScalarInt (INTEGER 1) eps')):
        checks += [f'S_bad_null_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_null_{label}_source,porigin_base,pkeyread.BASE)']
    for label, path, line, constant in (
            ('condition_line', 'pcpath_cond', 0, 'false'),
            ('inner_line', 'pcpath_inner', 0, 'false'),
            ('folded_condition', 'pcpath_cond', 12, 'true'),
            ('null_emitted', 'pcpath_null', 12, 'false'),
            ('leaf_emitted', 'pcpath_inner_leaf', 12, 'false')):
        checks += [f'S_bad_null_{label} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} {line} {constant}) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_known_base(S_bad_null_{label},porigin_base,pkeyread.BASE)']
    for label in ('cond', 'inner', 'inner_leaf', 'null'):
        checks += [f'S_bad_null_{label}_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} $(z_precision + 1)) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_known_base(S_bad_null_{label}_precision,porigin_base,pkeyread.BASE)']
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_unused 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_unused 12 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_unused $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('value', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_unused (PSTRING ($ptascii("X")))) :: ppool.CONSTANTS]]')):
        checks += [f'S_unused_null_{label} = S_capture[{update}]',
                   f'$string_read_raw_known_base(S_unused_null_{label},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_nonnull = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_nonnull,porigin_cond) = (PINT 1)
$string_read_raw_known_base(S_nonnull,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
~$string_read_raw_known_base(S_nonnull,porigin_base,pkeyread.BASE)
S_forged_null = S_nonnull[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_forged_null,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) - 1 + len(checks), derived + len(checks)

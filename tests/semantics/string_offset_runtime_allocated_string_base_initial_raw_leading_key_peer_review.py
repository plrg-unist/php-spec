"""A real REQUEST temporary owns the saved raw offset through Warning rebinding."""

from string_offset_initial_raw_leading_key_peer_review import render as render_reference
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_reference(program, filename_b64)
    body = body.replace('~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])',
                        '~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 3])')
    for line in body.splitlines():
        if line.endswith(' = (1)'):
            assert '$string_read_raw_leading(' in line or '$string_read_raw_saved(' in line
    body = body.replace(' = (1)\n', ' = (2)\n')
    body = body.replace('STRING_LEADING 1', 'STRING_LEADING 2')
    body = body.replace('$ptascii("abc")', '$ptascii("10bc")')
    body = body.replace('$ptascii("1x")', '$ptascii("2x")')
    body = body.replace('512:1x;', '512:2x;').replace(';K:2;A:', ';K:3;A:')
    body = body.replace('STORE[n_current] = DEFINED (PINT 2)',
                        'STORE[n_current] = DEFINED (PINT 3)')
    body = body.replace('pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("10bc"))',
                        'pvalue_base = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("10bc"))')
    body = body.replace('STRINGDATA = [$ptascii("512")]',
                        'STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc")]')
    body = body.replace('$string_read_raw_leading(', '$string_read_allocated_leading(S_capture,')
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("10bc")))',
             '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("10bc"))) = pvalue_base',
             '$string_read_allocated_base(S_capture,porigin_base,pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
expression_left = NExprBinaryOpConcat expression_cast expression_suffix metadata_left
expression_cast = NExprCastString expression_atom metadata_cast
expression_atom = NScalarInt (INTEGER 10) metadata_atom
expression_suffix = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_suffix) = $ptascii("bc")
expression_right = NExprTernary expression_guard expression_selected expression_unused metadata_right
expression_guard = NExprCastInt expression_guard_atom metadata_guard
expression_guard_atom = NScalarInt (INTEGER 1) metadata_guard_atom
expression_selected = NScalarString (BYTES text_selected) metadata_selected
expression_unused = NScalarString (BYTES text_unused) metadata_unused
$base64(text_selected) = $ptascii("XYZ")
$base64(text_unused) = $ptascii("abc")
pvalue_cast = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("10"))
pvalue_suffix = PSTRING_CARRIER INTERNED_STRING ($ptascii("bc"))
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_suffix)
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_selected)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_unused)
porigin_base = PORIGIN n_unit pcpath_base
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_allocated_value(S_capture,porigin_cast,pvalue_cast)
$string_read_allocated_value(S_capture,porigin_left,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
~$string_read_allocated_base(S_capture,porigin_base,pvalue_cast)
~$string_read_allocated_base(S_capture,porigin_base,PSTRING ($ptascii("10bc")))
~$string_read_allocated_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("10bc")))
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_leading(pvalue_base,pvalue_raw) = eps
$string_read_allocated_leading(S_capture,pvalue_base,pvalue_raw) = (2)
$string_read_provider_ready(S_capture,pstringread)
$string_carrier_valid(S_capture,pvalue_cast)
$string_carrier_valid(S_capture,pvalue_base)
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
z_precision = 14
$concat_constant(S_capture,(porigin_cast)) = false
$concat_constant(S_capture,(porigin_suffix)) = true
$string_byte_read(S,$ptascii("10bc"),3,18) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))]
S_cast_seed = S_capture[.STRINGDATA = [$ptascii("512")]]
$cast_apply(S_cast_seed,CASTSTRING,PINT 10,18) = S_cast_seed[.STRINGDATA = [$ptascii("512"),$ptascii("10")]][.RESULT = KNOWN pvalue_cast]
S_concat_seed = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("10")]]
$string_concat(S_concat_seed,pvalue_cast,pvalue_suffix,false,true) = S_concat_seed[.STRINGDATA = S_capture.STRINGDATA][.RESULT = KNOWN pvalue_base]
$heap_graph(S_cast_seed) = $heap_graph(S_capture)
$heap_graph(S_concat_seed) = $heap_graph(S_capture)
''')
    nodes = {
        'left': 'expression_left', 'cast': 'expression_cast', 'atom': 'expression_atom',
        'suffix': 'expression_suffix', 'right': 'expression_right', 'guard': 'expression_guard',
        'selected': 'expression_selected', 'unused': 'expression_unused',
    }
    for name, expression in nodes.items():
        checks += [f'porigin_{name} = PORIGIN n_unit pcpath_{name}',
                   f'$origin_node(S_capture.SOURCES,porigin_{name}) = ({expression})']
    checks.append('$pcwalk([PCOCCURRENCE pcpath_left expression_left]) = [PCOCCURRENCE pcpath_left expression_left,PCOCCURRENCE (pcpath_left ++ [PCFIELD 0]) expression_cast,PCOCCURRENCE (pcpath_left ++ [PCFIELD 0,PCFIELD 0]) expression_atom,PCOCCURRENCE (pcpath_left ++ [PCFIELD 1]) expression_suffix]')
    for name in ('base', 'left', 'cast'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
                   f'$(z_{name} > 0)',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{name}) = eps',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_{name}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{name})) = (z_precision)',
                   f'$compiled_read(S_capture,porigin_{name}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{name}) = eps',
                   f'$string_read_runtime_value(S_capture,porigin_{name}) = eps']
    for name, value in [('atom', 'PINT 10'), ('suffix', 'PSTRING ($ptascii("bc"))')]:
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},true))',
                   f'$(z_{name} > 0)',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{name}) = ({value})',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_{name}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{name})) = (z_precision)',
                   f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                   f'$compiled_identity_value(S_capture,porigin_{name}) = ({value})']
    checks += lines(r'''
S_suffix_entry = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("10"),$ptascii("10bc")]]
$string_carrier_valid(S_suffix_entry,pvalue_base)
$string_read_allocated_base(S_suffix_entry,porigin_base,pvalue_base)
$string_read_raw_capture(S_suffix_entry,poperand,pvalue_base) = eps
$string_read_plan(S_suffix_entry) = eps
S_suffix_saved = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("10"),$ptascii("10bc")]]
$heap_graph(S_suffix_saved) = H
$string_read_allocated_base(S_suffix_saved,porigin_base,pvalue_base)
$string_read_raw_saved(S_suffix_saved,pstringread) = (2)
$string_read_source(S_suffix_saved,pstringread)
$string_read_provider_ready(S_suffix_saved,pstringread)
$string_read_ready(S_suffix_saved,pstringread)
$string_read_resume(S_suffix_saved,pstringread) = S_suffix_saved[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pvalue_same_bytes = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("10bc"))
$string_carrier_valid(S_suffix_saved,pvalue_same_bytes)
$string_same(pvalue_base,pvalue_same_bytes) = (false)
pstringread_wrong_base = pstringread[.READ.BASE = pvalue_same_bytes]
pstringread_wrong_owner = pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pvalue_same_bytes)]
~$string_read_provider_ready(S_suffix_saved,pstringread_wrong_base)
$string_read_raw_saved(S_suffix_saved,pstringread_wrong_base) = eps
~$string_read_source(S_suffix_saved,pstringread_wrong_base)
$string_read_raw_saved(S_suffix_saved,pstringread_wrong_owner) = eps
~$string_read_source(S_suffix_saved,pstringread_wrong_owner)
S_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("10bc")]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("10bc"))
$string_carrier_valid(S_clone,pvalue_clone)
~$string_read_allocated_value(S_clone,porigin_left,pvalue_clone)
$string_read_raw_capture(S_clone[.RESULT = KNOWN pvalue_clone],poperand,pvalue_clone) = eps
S_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("10"),[49,48,0,98,99]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 2) ([49,48,0,98,99])
$string_carrier_valid(S_nul,pvalue_nul)
$string_read_allocated_leading(S_nul,pvalue_nul,pvalue_raw) = eps
~$string_read_allocated_base(S_nul,porigin_base,pvalue_nul)
$string_read_raw_capture(S_nul[.RESULT = KNOWN pvalue_nul],poperand,pvalue_nul) = eps
S_registry_only = S_capture[.SOURCES = eps]
$string_carrier_valid(S_registry_only,pvalue_base)
~$string_read_allocated_base(S_registry_only,porigin_base,pvalue_base)
$string_read_raw_capture(S_registry_only,poperand,pvalue_base) = eps
$string_read_allocated_leading(S_capture,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("10bc")),pvalue_raw) = eps
$string_read_allocated_leading(S_capture,PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("10")),pvalue_raw) = eps
$string_read_allocated_leading(S_capture,PSTRING_CARRIER (REQUEST_STRING 99) ($ptascii("10bc")),pvalue_raw) = eps
''')
    for node, expression in (
            ('left', 'NExprBinaryOpConcat expression_cast expression_suffix eps'),
            ('cast', 'NExprCastString expression_atom eps'),
            ('atom', 'NScalarInt (INTEGER 10) eps'),
            ('suffix', 'NScalarString (BYTES text_suffix) eps'),
            ('right', 'NExprTernary expression_guard expression_selected expression_unused eps')):
        state = 'S_allocated_shadow_' + node
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = eps']
    updates = [(name + '_line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} 0 false) :: pcode.EXPRESSIONS]]')
               for name in ('base', 'left', 'cast')]
    updates += [(name + '_folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} z_{name} true) :: pcode.EXPRESSIONS]]')
                for name in ('base', 'left', 'cast')]
    updates += [(name + '_precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{name} 17) :: ppool.CONSTANTS]]')
                for name in ('base', 'left', 'cast', 'atom', 'suffix')]
    updates += [('atom_pool_' + str(i), f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom ({value})) :: ppool.CONSTANTS]]')
                for i, value in enumerate(['PINT 9', 'PFLOAT 4621819117588971520', 'PSTRING ($ptascii("10"))'])]
    updates += [('cast_history', '.STRINGDATA = [$ptascii("512"),$ptascii("wrong"),$ptascii("10bc")]'),
                ('result_history', '.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("wrong")]'),
                ('suffix_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_suffix (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]'),
                ('suffix_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_suffix z_suffix false) :: pcode.EXPRESSIONS]]'),
                ('constant_context', '.CONSTCONTEXT = ({ORIGIN porigin_base,LINE 18,FACTS eps})'),
                ('missing_cast', '.CODE = [pcode[.EXPRESSIONS = eps]]')]
    for label, update in updates:
        state = 'S_allocated_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = eps']
    for label, update in (
            ('right_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('right_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]'),
            ('selected_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]'),
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 0 false) :: pcode.EXPRESSIONS]]')):
        state = 'S_allocated_skipped_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))']
    # Constructed literal-empty checks preserve the compiler's actual CONST flag.
    checks += lines(r'''
expression_empty = NScalarString (BYTES "") metadata_suffix
expression_empty_concat = NExprBinaryOpConcat expression_cast expression_empty metadata_left
S_empty = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10")]][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left expression_empty_concat) :: (PCOCCURRENCE pcpath_suffix expression_empty) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_suffix (PSTRING eps)) :: ppool.CONSTANTS]]]
pvalue_empty_result = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("10"))
$string_read_allocated_value(S_empty,porigin_left,pvalue_empty_result)
$concat_constant(S_empty,(porigin_suffix)) = true
S_empty_prefix = S_empty[.STRINGDATA = [$ptascii("512"),$ptascii("10")]]
$string_concat(S_empty_prefix,pvalue_cast,PSTRING_CARRIER INTERNED_STRING eps,false,true) = S_empty_prefix[.STRINGDATA = S_empty.STRINGDATA][.RESULT = KNOWN pvalue_empty_result]
$string_concat(S_empty_prefix,pvalue_cast,PSTRING_CARRIER INTERNED_STRING eps,false,false) = S_empty_prefix[.RESULT = KNOWN pvalue_cast]
~$string_read_allocated_value(S_empty,porigin_left,pvalue_cast)
S_empty_not_constant = S_empty[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_suffix z_suffix false) :: pcode.EXPRESSIONS]]]
~$string_read_allocated_value(S_empty_not_constant,porigin_left,pvalue_empty_result)
''')
    for integer, admitted in [(0, False), (9, False), (9223372036854775807, True),
                              (-9223372036854775808, True), (9223372036854775808, False),
                              (-9223372036854775809, False)]:
        label = ('negative_' + str(-integer)) if integer < 0 else str(integer)
        literal = str(integer) if integer >= 0 else '$(' + str(integer) + ')'
        state = 'S_allocated_integer_' + label
        atom = 'expression_allocated_integer_' + label
        cast = 'expression_allocated_cast_' + label
        value = f'PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("{integer}"))'
        checks += [f'{atom} = NScalarInt (INTEGER {literal}) metadata_atom',
                   f'{cast} = NExprCastString {atom} metadata_cast',
                   f'{state} = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("{integer}")]][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_cast {cast}) :: (PCOCCURRENCE pcpath_atom {atom}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT {literal})) :: ppool.CONSTANTS]]]',
                   ('' if admitted else '~') + f'$string_read_allocated_value({state},porigin_cast,{value})']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)

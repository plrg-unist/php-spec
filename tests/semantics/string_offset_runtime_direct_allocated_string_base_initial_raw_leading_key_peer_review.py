"""A direct REQUEST temporary keeps the saved reference-key offset."""

from string_offset_initial_raw_leading_key_peer_review import render as render_reference
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_reference(program, filename_b64)
    body = body.replace('~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])',
                        '~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 3])')
    for line in body.splitlines():
        if line.endswith(' = (1)'):
            assert '$string_read_raw_leading(' in line or '$string_read_raw_saved(' in line
    body = body.replace(' = (1)\n', ' = (2)\n').replace('STRING_LEADING 1', 'STRING_LEADING 2')
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpConcat expression_cast expression_suffix metadata_base)
expression_cast = NExprCastString expression_atom metadata_cast
expression_atom = NScalarInt (INTEGER 10) metadata_atom
expression_suffix = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_suffix) = $ptascii("bc")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_suffix)
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_atom)
porigin_base = PORIGIN n_unit pcpath_base
porigin_cast = PORIGIN n_unit pcpath_cast
porigin_atom = PORIGIN n_unit pcpath_atom
porigin_suffix = PORIGIN n_unit pcpath_suffix
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$origin_node(S_capture.SOURCES,porigin_suffix) = (expression_suffix)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
pvalue_cast = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("10"))
pvalue_suffix = PSTRING_CARRIER INTERNED_STRING ($ptascii("bc"))
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_allocated_value(S_capture,porigin_cast,pvalue_cast)
$string_read_allocated_base(S_capture,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_capture,porigin_base,pvalue_cast)
~$string_read_allocated_base(S_capture,porigin_cast,pvalue_base)
$string_read_runtime_value(S_capture,porigin_base) = eps
$string_read_runtime_value(S_capture,porigin_cast) = eps
$string_read_provider_ready(S_capture,pstringread)
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
    for name in ('base', 'cast'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
                   f'$(z_{name} > 0)',
                   f'$compiled_read(S_capture,porigin_{name}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{name}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{name}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{name})) = (14)']
    for name, value in (('atom', 'PINT 10'), ('suffix', 'PSTRING ($ptascii("bc"))')):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},true))',
                   f'$(z_{name} > 0)',
                   f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                   f'$compiled_identity_value(S_capture,porigin_{name}) = ({value})',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{name}) = ({value})',
                   f'$compiled_precision(S_capture,(porigin_{name})) = (14)']
    checks += lines(r'''
S_suffix_entry = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("callback"),$ptascii("10bc")]]
$string_read_allocated_base(S_suffix_entry,porigin_base,pvalue_base)
$string_read_raw_capture(S_suffix_entry,poperand,pvalue_base) = eps
$string_read_plan(S_suffix_entry) = eps
S_suffix_saved = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("10bc")]]
$heap_graph(S_suffix_saved) = H
$string_read_raw_saved(S_suffix_saved,pstringread) = (2)
$string_read_source(S_suffix_saved,pstringread)
$string_read_provider_ready(S_suffix_saved,pstringread)
$string_read_ready(S_suffix_saved,pstringread)
$string_read_resume(S_suffix_saved,pstringread) = S_suffix_saved[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pvalue_later = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("10bc"))
$string_carrier_valid(S_suffix_saved,pvalue_later)
$string_same(pvalue_base,pvalue_later) = (false)
$string_read_raw_saved(S_suffix_saved,pstringread[.READ.BASE = pvalue_later]) = eps
$string_read_raw_saved(S_suffix_saved,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pvalue_later)]) = eps
~$string_read_source(S_suffix_saved,pstringread[.READ.BASE = pvalue_later])
~$string_read_provider_ready(S_suffix_saved,pstringread[.READ.BASE = pvalue_later])
S_registry = S_capture[.SOURCES = eps]
$string_carrier_valid(S_registry,pvalue_base)
~$string_read_allocated_base(S_registry,porigin_base,pvalue_base)
$string_read_raw_capture(S_registry,poperand,pvalue_base) = eps
S_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("10"),[49,48,0,98,99]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 2) ([49,48,0,98,99])
$string_carrier_valid(S_nul,pvalue_nul)
~$string_read_allocated_base(S_nul,porigin_base,pvalue_nul)
$string_read_allocated_leading(S_nul,pvalue_nul,pvalue_raw) = eps
$string_read_raw_capture(S_nul[.RESULT = KNOWN pvalue_nul],poperand,pvalue_nul) = eps
''')
    for name, expression in (
            ('cast', 'NExprCastString expression_atom eps'),
            ('atom', 'NScalarInt (INTEGER 10) eps'),
            ('suffix', 'NScalarString (BYTES text_suffix) eps')):
        state = 'S_direct_shadow_' + name
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{name} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = eps']
    updates = [(name + '_line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} 0 false) :: pcode.EXPRESSIONS]]')
               for name in ('base', 'cast')]
    updates += [(name + '_folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} z_{name} true) :: pcode.EXPRESSIONS]]')
                for name in ('base', 'cast')]
    updates += [(name + '_precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{name} 17) :: ppool.CONSTANTS]]')
                for name in ('base', 'cast', 'atom', 'suffix')]
    updates += [('atom_type', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PSTRING ($ptascii("10")))) :: ppool.CONSTANTS]]'),
                ('cast_prefix', '.STRINGDATA = [$ptascii("512"),$ptascii("wrong"),$ptascii("10bc")]'),
                ('result_prefix', '.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("wrong")]'),
                ('suffix_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_suffix (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]'),
                ('suffix_flag', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_suffix z_suffix false) :: pcode.EXPRESSIONS]]'),
                ('constant_context', '.CONSTCONTEXT = ({ORIGIN porigin_base,LINE 18,FACTS eps})')]
    for label, update in updates:
        state = 'S_direct_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = eps']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)

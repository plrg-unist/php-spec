#!/usr/bin/env python3
"""Independent link authority and intrinsic quietness for scalar cast chains."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_nested_scalar_cast_return_modulo_error_state as current
import output_final_selected_nested_scalar_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-nested-scalar-cast-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or126_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or126_drop(eps, pcpath) = eps
def $or126_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or126_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or126_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def value(state, expression, origin='porigin_cast', function='pfunction_handler'):
    return '$ob_object_cast_chain_value(' + state + ', ' + function + ', ' + origin + ', ' + expression + ')'


def variant(name, leaf=None, pool=None, casts=None, styles=None, extra=(), leaf_path='pcpath_string'):
    casts = casts or current.CASTS[name]
    styles = styles or {}
    expressions = [leaf or current.LEAF]
    for index in reversed(range(len(casts))):
        node, _, kind = casts[index][:3]
        metadata = styles.get(index, '(Mkind ' + str(kind) + ') :: metadata_' + current.slot(index))
        expressions.insert(0, node + ' (' + expressions[0] + ') (' + metadata + ')')
    statement = 'NStmtReturn (' + expressions[0] + ') metadata_cast_return'
    rows = [('pcpath_cast_return', statement)]
    rows += [('pcpath_' + current.slot(i), expr) for i, expr in enumerate(expressions[:-1])]
    rows += [(leaf_path, expressions[-1]), *extra]
    state = control.source_state(rows)
    if pool is not None:
        state += control.pool_state(leaf_path, pool)[1:]
    return state, statement, expressions


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 'pcpath_name = pcpath_string ++ [PCFIELD 0]',
                 'porigin_name = PORIGIN n_cast_handler pcpath_name',
                 'pcpath_direct = pcpath_cast ++ [PCFIELD 0]']
    expression = current.expression(name)
    root = current.root_value(name)
    tail = control.tail
    checks += [
        ('the complete quiet chain certifies its exact typed result including strict FALSE or numeric zero',
         value('S', expression) + ' = (' + root + r') /\ ' + tail() +
         r' /\ S_handler.RESULT = KNOWN (' + root + r') /\ S.RESULT = KNOWN PNULL'),
        ('the actual raw string leaf is distinct from its authenticated nonowning carrier',
         value('S', current.LEAF, 'porigin_string') + r' = (PSTRING_CARRIER INTERNED_STRING n_string*) /\ '
         r'$compiled_read(S, porigin_string) = (PSTRING n_string*) /\ '
         r'$value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps'),
        ('the direct single-cast child gate remains disjoint from raw leaves',
         '$ob_object_cast_chain_kind(' + expression + r') /\ '
         r'~$ob_object_cast_chain_kind(NScalarString (BYTES text_string) metadata_string)'),
        ('handler unit and body cannot be borrowed from another source contour',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + root + ')]'
    checks += [('a preset final value cannot certify a non-NORMAL chain',
                value(abrupt, expression) + r' = eps /\ ~' + tail(abrupt))]
    for index, (_, operator, kind, result) in enumerate(current.CASTS[name]):
        slot = current.slot(index)
        origin, codepath, line = 'porigin_' + slot, 'pcpath_' + slot, 'z_' + slot
        checks += [('actual link ' + str(index) + ' retains its exact typed value and emitted read-eps',
                    value('S', current.expression(name, index), origin) + ' = (' + result + r') /\ '
                    '$compiled_read(S, ' + origin + ') = eps')]
        for label, bad_line, flag in [('flag', line, 'true'), ('line', '$(' + line + ' + 1)', 'false')]:
            checks += [('link ' + str(index) + ' forged ' + label + ' refuses the entire chain',
                        '~' + tail(function=control.code_function(codepath, bad_line, flag)))]
        for label, metadata in [('alias', '(Mkind ' + ('1' if kind == 2 else '2') + ') :: metadata_' + slot),
                                ('missing', 'eps')]:
            state, statement, _ = variant(name, styles={index: metadata})
            checks += [('link ' + str(index) + ' ' + label + ' kind refuses despite coherent ancestor source',
                        '~' + tail(state, statement=statement))]
        state = control.pool_state(codepath, result)
        code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' ' + line + ' true) :: pfunction_handler.CODE.EXPRESSIONS]'
        checks += [('link ' + str(index) + ' ignores an unread pool but refuses an actual folded value',
                    '$compiled_read(' + state + ', ' + origin + r') = eps /\ ' + tail(state) + r' /\ ~' +
                    tail(state + '[.CODE = ' + code + ' :: S.CODE]'))]
    for label, source_path in [('Return', 'pcpath_cast_return'),
            *[(current.slot(i), 'pcpath_' + current.slot(i)) for i in range(len(current.CASTS[name]))],
            ('leaf', 'pcpath_string')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or126_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only ' + label + ' source refuses the nested tail', '~' + tail(state))]
    for value_pool in ['PBOOL false', 'PNULL', 'PINT 0', 'PFLOAT 0',
                       'PSTRING_CARRIER INTERNED_STRING n_string*', 'PSTRING ($ptascii("other"))']:
        checks += [('raw leaf pool ' + value_pool + ' cannot replace exact source bytes',
                    value(control.pool_state('pcpath_string', value_pool), expression) + ' = eps')]
    bindings += ['S_no_precision = S[.DECLARATIONS = eps][.POOLS = '
                 'ppool_handler[.CONSTANTS = [(PCONSTANT pcpath_string (PSTRING n_string*))]] :: S.POOLS]']
    checks += [('missing leaf precision refuses the chain despite exact raw bytes',
                r'$compiled_read(S_no_precision, porigin_string) = (PSTRING n_string*) /\ '
                r'$compiled_string_value(S_no_precision, porigin_string, PSTRING n_string*) = PSTRING n_string* /\ '
                + value('S_no_precision', expression) + ' = eps')]
    state, statement, _ = variant(name, 'NScalarString (BYTES "AA==") metadata_string',
                                  'PSTRING ($base64("AA=="))')
    checks += [('NUL leaf rejection retains zero source credit and adds no release behavior', '~' + tail(state, statement=statement))]
    for integer in ['7', '$(-9223372036854775808)', '9223372036854775808', '$(-9223372036854775809)']:
        leaf = 'NScalarInt (INTEGER ' + integer + ') metadata_string'
        state, statement, _ = variant(name, leaf, 'PINT ' + integer)
        valid = integer in ['7', '$(-9223372036854775808)']
        checks += [('raw signed integer ' + integer + ' retains its exact canonical range',
                    value(state, leaf, 'porigin_string') + (' = (PINT ' + integer + ')' if valid else ' = eps') +
                    (r' /\ ' if valid else r' /\ ~') + tail(state, statement=statement))]
    for keyword, typed in [(b'TrUe', 'PBOOL true'), (b'FaLsE', 'PBOOL false'), (b'NuLl', 'PNULL')]:
        raw_name = 'NName (BYTES "' + base64.b64encode(keyword).decode() + '") metadata_string'
        leaf = 'NExprConstFetch (' + raw_name + ') metadata_string'
        state, statement, _ = variant(name, leaf, typed, extra=[('pcpath_name', raw_name)])
        checks += [('indexed keyword ' + keyword.decode() + ' retains its strict typed leaf',
                    value(state, leaf, 'porigin_string') + ' = (' + typed + r') /\ ' + tail(state, statement=statement))]
        if typed in ['PBOOL false', 'PNULL']:
            other = 'PNULL' if typed == 'PBOOL false' else 'PBOOL false'
            wrong = state + control.pool_state('pcpath_string', other)[1:]
            checks += [('equal false truth never permits exchanging keyword FALSE and NULL tags',
                        value(wrong, leaf, 'porigin_string') + ' = eps')]
    for text in ['000000000000000', '00000000000000000', '000000000000000A', '000000000000000g']:
        leaf = 'NScalarFloat (FLOAT "' + text + '") metadata_string'
        state, statement, _ = variant(name, leaf, 'PFLOAT 0')
        checks += [('malformed raw FLOAT ' + text + ' refuses before partial decode',
                    value(state, leaf, 'porigin_string') + r' = eps /\ ~' + tail(state, statement=statement))]
    float_cases = [('nan-bool', '7ff8abcdef012345', 'CASTBOOL', 'NExprCastBool', 1, 'PBOOL true', False),
                   ('nan-int', '7ff8abcdef012345', 'CASTINT', 'NExprCastInt', 1, 'PINT 0', False),
                   ('range-int', '43e0000000000000', 'CASTINT', 'NExprCastInt', 1, 'PINT $(-9223372036854775808)', False),
                   ('nan-identity', '7ff8abcdef012345', 'CASTFLOAT', 'NExprCastDouble', 2, None, True),
                   ('infinity-bool', '7ff0000000000000', 'CASTBOOL', 'NExprCastBool', 1, 'PBOOL true', True),
                   ('negative-zero-bool', '8000000000000000', 'CASTBOOL', 'NExprCastBool', 1, 'PBOOL false', True)]
    for label, text, operator, node, kind, result, quiet in float_cases:
        bits = str(int(text, 16))
        result = result or 'PFLOAT ' + bits
        casts = [(node, operator, kind)] + [('NExprCastDouble', 'CASTFLOAT', 2)] * (len(current.CASTS[name]) - 1)
        leaf = 'NScalarFloat (FLOAT "' + text + '") metadata_string'
        state, statement, exprs = variant(name, leaf, 'PFLOAT ' + bits, casts=casts)
        local = 'S_local_' + label.replace('-', '_')
        bindings += [local + ' = ' + state,
                     local + '_masked = ' + local + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                     '[.ERRORFATALTRACE = eps][.RESULT = KNOWN (' + result + ')]']
        masked = local + '_masked'
        condition = (value(masked, exprs[1], 'porigin_cast_1') + ' = (PFLOAT ' + bits + r') /\ '
            '$cast_apply(' + masked + '[.RESULT = KNOWN (PFLOAT ' + bits + ')], ' + operator + ', PFLOAT ' + bits + ', z_cast) = ' +
            masked + '[.RESULT = KNOWN (' + result + r')] /\ ')
        if quiet:
            condition += value(masked, exprs[0]) + ' = (' + result + r') /\ ' + tail(masked, statement=statement)
        else:
            condition += ('~$ob_object_cast_chain_quiet(' + operator + ', PFLOAT ' + bits + r') /\ '
                + value(local, exprs[0]) + r' = eps /\ ' + value(masked, exprs[0]) + r' = eps /\ ~' + tail(masked, statement=statement))
        checks += [('source0 ' + label + ' distinguishes intrinsic quietness from masked full-state equality', condition)]
    bare = 'NStmtReturn ABSENT metadata_cast_return'
    checks += [('the old bare-Return arm remains valid and disjoint from expression casts',
                tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare))]
    node, _, kind = current.CASTS[name][-1][:3]
    direct, statement, exprs = variant(name, casts=[(node, current.CASTS[name][-1][1], kind)], leaf_path='pcpath_direct')
    function = control.code_function('pcpath_direct', 'z_string', 'true')
    direct += control.pool_state('pcpath_direct', 'PSTRING n_string*')[1:] + '[.CODE = ' + function + '.CODE :: S.CODE]'
    checks += [('the old direct one-cast arm remains valid without joining the nested-only arm',
                r'~$ob_object_cast_chain_kind(NScalarString (BYTES text_string) metadata_string) /\ '
                + tail(direct, function=function, statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('real frame retirement preserves exact chain result, NULL scratch and no string owner',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ '
                r'$value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps /\ '
                r'$compiled_string_value(S_report, porigin_string, PSTRING n_string*) = PSTRING_CARRIER INTERNED_STRING n_string*')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()

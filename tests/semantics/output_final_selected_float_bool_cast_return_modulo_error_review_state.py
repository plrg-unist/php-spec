#!/usr/bin/env python3
"""Independent exact FLOAT truth and intrinsically noisy NaN refusal controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_float_bool_cast_return_modulo_error_state as current
import output_final_selected_float_bool_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-float-bool-cast-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or122_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or122_drop(eps, pcpath) = eps
def $or122_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or122_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or122_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''
LOCAL = {'positive_zero': ('0000000000000000', False, False),
         'negative_zero': ('8000000000000000', False, False),
         'positive_subnormal': ('0000000000000001', True, False),
         'negative_subnormal': ('8000000000000001', True, False),
         'negative_normal': ('bff8000000000000', True, False),
         'positive_infinity': ('7ff0000000000000', True, False),
         'negative_infinity': ('fff0000000000000', True, False),
         'quiet_nan': ('7ff8abcdef012345', True, True),
         'signaling_nan': ('7ff0000000000001', True, True),
         'negative_nan': ('fff8000000000001', True, True)}


def variant(text='text_float', metadata='metadata_cast'):
    child = 'NScalarFloat (FLOAT ' + text + ') metadata_float'
    cast = 'NExprCastBool (' + child + ') (' + metadata + ')'
    statement = 'NStmtReturn (' + cast + ') metadata_cast_return'
    state = control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', cast),
                                  ('pcpath_float', child)])
    return state, statement


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    tail = control.tail
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL b_return)]'
    checks += [
        ('the real emitted root and exact PFLOAT child preserve intrinsically quiet typed truth',
         tail() + r' /\ $compiled_read(S, porigin_cast) = eps /\ '
         r'$compiled_read(S, porigin_float) = (PFLOAT n_child) /\ '
         r'$number_bool(NFLOAT n_child) = (b_return, false) /\ '
         r'$cast_apply(S, CASTBOOL, PFLOAT n_child, z_cast) = S[.RESULT = KNOWN (PBOOL b_return)]'),
        ('the actual return is a Boolean rather than integer zero or NULL',
         r'S_handler.RESULT = KNOWN (PBOOL b_return) /\ '
         r'S_handler.RESULT =/= KNOWN (PINT 0) /\ S_handler.RESULT =/= KNOWN PNULL'),
        ('NORMAL remains necessary when an abrupt cast already has the expected Boolean scratch',
         '$cast_apply(' + abrupt + ', CASTBOOL, PFLOAT n_child, z_cast) = ' + abrupt +
         r' /\ $cast_apply(' + abrupt + ', CASTBOOL, PFLOAT n_child, z_cast) = ' +
         abrupt + r'[.RESULT = KNOWN (PBOOL b_return)] /\ ~' + tail(abrupt)),
        ('handler CODE unit retains the actual source origin',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]')),
        ('handler BODY retains its actual source path',
         '~' + tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for label, source_path, line, flag in [
            ('emitted root flag', 'pcpath_cast', 'z_cast', 'true'),
            ('pooled child flag', 'pcpath_float', 'z_float', 'false'),
            ('cast line', 'pcpath_cast', '$(z_cast + 1)', 'false'),
            ('FLOAT line', 'pcpath_float', '$(z_float + 1)', 'true')]:
        checks += [(label + ' cannot be forged independently of actual source and child',
                    '~' + tail(function=control.code_function(source_path, line, flag)))]
    for label, source_path in [('Return', 'pcpath_cast_return'), ('root', 'pcpath_cast'),
                               ('raw FLOAT', 'pcpath_float')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or122_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only the own ' + label + ' source refuses the tail', '~' + tail(state))]
    shadow = control.source_state([('pcpath_float',
        'NScalarFloat (FLOAT "3ff0000000000000") metadata_float')])
    checks += [('an earlier indexed raw-child shadow defeats unchanged Return/root and PFLOAT read',
                '~' + tail(shadow))]
    for label, metadata in [('BOOLEAN alias', '(Mkind 2) :: metadata_cast'), ('missing kind', 'eps')]:
        state, statement = variant(metadata=metadata)
        checks += [(label + ' cannot certify the canonical bool cast', '~' + tail(state, statement=statement))]
    for value in ['PBOOL false', 'PBOOL true', 'PNULL', 'PINT 0', 'PFLOAT 4607182418800017408']:
        checks += [('child pool ' + value + ' cannot replace the exact raw PFLOAT',
                    '~' + tail(control.pool_state('pcpath_float', value)))]
    checks += [('missing child pool cannot supply a typed value certificate', '~' + tail('S[.POOLS = eps]'))]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: '
                   'pfunction_handler.CODE.EXPRESSIONS]')
    root_pool = control.pool_state('pcpath_cast', 'PBOOL b_return')
    checks += [('an actually folded root refuses instead of borrowing its correct Boolean pool',
                '~' + tail(root_pool + '[.CODE = ' + global_code + ' :: S.CODE]')),
               ('an ignored raw root pool does not replace or defeat emitted read-eps authority',
                '$compiled_read(' + root_pool + r', porigin_cast) = eps /\ ' + tail(root_pool))]
    for label, (text, result, warning) in LOCAL.items():
        state, statement = variant('"' + text + '"')
        bits = str(int(text, 16))
        state += control.pool_state('pcpath_float', 'PFLOAT ' + bits)[1:]
        local = 'S_local_' + label
        local_statement = 'statement_local_' + label
        bindings += [local + ' = ' + state, local_statement + ' = ' + statement]
        typed = ('false', 'true')[result]
        noisy = ('false', 'true')[warning]
        condition = ('$origin_node(' + local + '.SOURCES, porigin_cast_return) = (' + local_statement + r') /\ '
            '$origin_node(' + local + '.SOURCES, porigin_float) = (NScalarFloat (FLOAT "' + text + r'") metadata_float) /\ '
            '$evaluate(NScalarFloat (FLOAT "' + text + '") metadata_float) = VALUE (PFLOAT ' + bits + r') /\ '
            '$compiled_read(' + local + r', porigin_cast) = eps /\ '
            '$compiled_read(' + local + ', porigin_float) = (PFLOAT ' + bits + r') /\ '
            '$number_bool(NFLOAT ' + bits + ') = (' + typed + ', ' + noisy + r') /\ ')
        if not warning:
            condition += ('$cast_apply(' + local + ', CASTBOOL, PFLOAT ' + bits + ', z_cast) = ' +
                local + '[.RESULT = KNOWN (PBOOL ' + typed + r')] /\ ' + tail(local, statement=local_statement))
        else:
            suppressed = local + '_suppressed'
            bindings += [suppressed + ' = ' + local + '[.REPORTING = 0]'
                         '[.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                         '[.ERRORFATALTRACE = eps][.RESULT = KNOWN (PBOOL true)]']
            condition += ('~' + tail(local, statement=local_statement) + r' /\ '
                + suppressed + r'.COMPLETION = NORMAL /\ ' + suppressed + r'.REPORTING = 0 /\ '
                + suppressed + r'.ERRORHANDLER.CALLBACK = eps /\ ' + suppressed + r'.ERRORFATALTRACE = eps /\ '
                '$compiled_read(' + suppressed + ', porigin_float) = (PFLOAT ' + bits + r') /\ '
                '$number_bool(NFLOAT ' + bits + r') = (true, true) /\ '
                '$cast_apply(' + suppressed + ', CASTBOOL, PFLOAT ' + bits + ', z_cast) = ' + suppressed + r' /\ '
                '$cast_apply(' + suppressed + ', CASTBOOL, PFLOAT ' + bits + ', z_cast) = ' +
                suppressed + r'[.RESULT = KNOWN (PBOOL true)] /\ ~' + tail(suppressed, statement=local_statement))
        checks += [('source0 local ' + label + ' retains exact bits and intrinsic truth without native credit', condition)]
    for text in ['000000000000000', '00000000000000000', '10000000000000000',
                 '000000000000000A', '000000000000000g']:
        state, statement = variant('"' + text + '"')
        checks += [('width and lowercase hexadecimal guards reject ' + text + ' before partial decoding',
                    '~' + tail(state, statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual handler retirement preserves strict Boolean return and resumed NULL scratch',
                r'S_handler.RESULT = KNOWN (PBOOL b_return) /\ '
                r'S_handler.RESULT =/= KNOWN (PINT 0) /\ S_handler.RESULT =/= KNOWN PNULL /\ '
                r'S.RESULT = KNOWN PNULL')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()

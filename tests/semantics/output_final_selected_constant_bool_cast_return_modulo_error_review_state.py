#!/usr/bin/env python3
"""Independent keyword truth keeps raw names and strict child tags authoritative."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_constant_bool_cast_return_modulo_error_state as current
import output_final_selected_constant_bool_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-constant-bool-cast-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or123_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or123_drop(eps, pcpath) = eps
def $or123_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or123_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or123_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def variant(name_node, metadata='metadata_cast'):
    child = 'NExprConstFetch (' + name_node + ') metadata_constant'
    cast = 'NExprCastBool (' + child + ') (' + metadata + ')'
    statement = 'NStmtReturn (' + cast + ') metadata_cast_return'
    state = control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', cast),
                                  ('pcpath_constant', child), ('pcpath_constant_name', name_node)])
    return state, statement


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 'porigin_constant_name = PORIGIN n_cast_handler pcpath_constant_name']
    tail = control.tail
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL b_return)]'
    checks += [
        ('the actual indexed keyword needs no invented name CODE or name pool',
         tail() + r' /\ $code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_constant_name) = eps /\ '
         r'$pool_value(S.POOLS, porigin_constant_name) = eps /\ $compiled_read(S, porigin_cast) = eps'),
        ('the full quiet Boolean cast preserves exact child truth and every other state field',
         r'$special_constant($base64(text_constant)) = (pvalue_child) /\ '
         r'b_return = $truth(S, pvalue_child) /\ '
         r'$cast_apply(S, CASTBOOL, pvalue_child, z_cast) = S[.RESULT = KNOWN (PBOOL b_return)]'),
        ('NORMAL remains required when an abrupt cast already has its expected Boolean scratch',
         '$cast_apply(' + abrupt + ', CASTBOOL, pvalue_child, z_cast) = ' + abrupt +
         r' /\ $cast_apply(' + abrupt + ', CASTBOOL, pvalue_child, z_cast) = ' +
         abrupt + r'[.RESULT = KNOWN (PBOOL b_return)] /\ ~' + tail(abrupt)),
        ('handler CODE unit must match the actual source origin',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]')),
        ('handler BODY must retain its actual source path',
         '~' + tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for label, source_path, line, flag in [
            ('emitted root flag', 'pcpath_cast', 'z_cast', 'true'),
            ('pooled child flag', 'pcpath_constant', 'z_constant', 'false'),
            ('cast line', 'pcpath_cast', '$(z_cast + 1)', 'false'),
            ('ConstFetch line', 'pcpath_constant', '$(z_constant + 1)', 'true')]:
        checks += [(label + ' cannot be forged independently of actual source',
                    '~' + tail(function=control.code_function(source_path, line, flag)))]
    for label, source_path in [('Return', 'pcpath_cast_return'), ('root', 'pcpath_cast'),
                               ('ConstFetch', 'pcpath_constant'), ('indexed name', 'pcpath_constant_name')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or123_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only the own ' + label + ' source refuses the tail', '~' + tail(state))]
    actual_name = 'NName (BYTES text_constant) metadata_name'
    for label, metadata in [('BOOLEAN alias', '(Mkind 2) :: metadata_cast'), ('missing kind', 'eps')]:
        state, statement = variant(actual_name, metadata)
        checks += [(label + ' cannot certify the canonical bool cast', '~' + tail(state, statement=statement))]
    for kind in ['NNameFullyQualified', 'NNameRelative']:
        state, statement = variant(kind + ' (BYTES text_constant) metadata_name')
        checks += [(kind + ' remains outside the simple-keyword certificate', '~' + tail(state, statement=statement))]
    for keyword in [b'unknown123', b'falsex']:
        payload = base64.b64encode(keyword).decode()
        state, statement = variant('NName (BYTES "' + payload + '") metadata_name')
        checks += [('unknown simple name cannot borrow the original keyword pool', '~' + tail(state, statement=statement))]
    shadow = control.source_state([('pcpath_constant_name',
                                   'NNameRelative (BYTES text_constant) metadata_name')])
    checks += [('an earlier indexed-name shadow defeats unchanged Return/root/ConstFetch and pool',
                '~' + tail(shadow))]
    for value in ['PBOOL false', 'PBOOL true', 'PNULL', 'PINT 0', 'PFLOAT 0']:
        if value == current.KEYWORDS[name][1]:
            continue
        checks += [('child pool ' + value + ' cannot replace the exact keyword tag',
                    '~' + tail(control.pool_state('pcpath_constant', value)))]
    if current.KEYWORDS[name][1] == 'PNULL':
        other = 'PBOOL false'
    elif current.KEYWORDS[name][1] == 'PBOOL false':
        other = 'PNULL'
    else:
        other = 'PINT 1'
    same_truth = control.pool_state('pcpath_constant', other)
    checks += [('same Boolean output does not replace exact NULL or Boolean child authority',
                '$cast_apply(' + same_truth + ', CASTBOOL, ' + other + ', z_cast) = ' +
                same_truth + r'[.RESULT = KNOWN (PBOOL b_return)] /\ ~' + tail(same_truth))]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: '
                   'pfunction_handler.CODE.EXPRESSIONS]')
    root_pool = control.pool_state('pcpath_cast', 'PBOOL b_return')
    checks += [('a genuinely folded root refuses even with its correct Boolean result',
                '~' + tail(root_pool + '[.CODE = ' + global_code + ' :: S.CODE]')),
               ('an ignored raw root pool does not replace emitted read-eps authority',
                '$compiled_read(' + root_pool + r', porigin_cast) = eps /\ ' + tail(root_pool)),
               ('missing child pool cannot certify a raw keyword', '~' + tail('S[.POOLS = eps]'))]
    for keyword, value, truth in [(b'false', 'PBOOL false', 'false'), (b'FaLsE', 'PBOOL false', 'false'),
                                  (b'null', 'PNULL', 'false'), (b'NuLl', 'PNULL', 'false'),
                                  (b'true', 'PBOOL true', 'true'), (b'TrUe', 'PBOOL true', 'true')]:
        payload = base64.b64encode(keyword).decode()
        state, statement = variant('NName (BYTES "' + payload + '") metadata_name')
        state += control.pool_state('pcpath_constant', value)[1:]
        checks += [('source0 local ' + keyword.decode() + ' retains strict keyword type and Boolean truth',
                    '$special_constant($ptascii("' + keyword.decode() + '")) = (' + value + r') /\ '
                    '$compiled_read(' + state + ', porigin_constant) = (' + value + r') /\ '
                    '$cast_apply(' + state + ', CASTBOOL, ' + value + ', z_cast) = ' +
                    state + '[.RESULT = KNOWN (PBOOL ' + truth + r')] /\ ' + tail(state, statement=statement))]
        if value in ['PBOOL false', 'PNULL']:
            other = 'PNULL' if value == 'PBOOL false' else 'PBOOL false'
            wrong = state + control.pool_state('pcpath_constant', other)[1:]
            checks += [('source0 local FALSE and NULL refuse exchanged tags despite the same quiet Boolean result',
                        '$cast_apply(' + wrong + ', CASTBOOL, ' + other + ', z_cast) = ' +
                        wrong + r'[.RESULT = KNOWN (PBOOL false)] /\ ~' + tail(wrong, statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual handler retirement preserves strict Boolean output and resumed NULL scratch',
                r'S_handler.RESULT = KNOWN (PBOOL b_return) /\ '
                r'S_handler.RESULT =/= KNOWN (PINT 0) /\ S_handler.RESULT =/= KNOWN PNULL /\ '
                r'S.RESULT = KNOWN PNULL')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()

#!/usr/bin/env python3
"""Independent keyword identity and source-authority controls for FLOAT returns."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_state as current
import output_final_selected_constant_float_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-constant-float-cast-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or119_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or119_drop(eps, pcpath) = eps
def $or119_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or119_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or119_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def tail(state='S', function='pfunction_handler', statement='statement_cast_return'):
    return '$ob_object_error_handler_tail(' + state + ', ' + function + ', [' + statement + '])'


def source_state(rows):
    entries = ' ++ '.join('[PCOCCURRENCE ' + path + ' (' + node + ')]' for path, node in rows)
    return ('S[.SOURCES = pcunit_handler[.OCCURRENCES = ' + entries +
            ' ++ pcunit_handler.OCCURRENCES] :: S.SOURCES]')


def variant(name_node, metadata='metadata_cast'):
    child = 'NExprConstFetch (' + name_node + ') metadata_constant'
    cast = 'NExprCastDouble (' + child + ') (' + metadata + ')'
    statement = 'NStmtReturn (' + cast + ') metadata_cast_return'
    state = source_state([('pcpath_cast_return', statement), ('pcpath_cast', cast),
                          ('pcpath_constant', child), ('pcpath_constant_name', name_node)])
    return state, statement


def pool_state(path, value):
    return ('S[.POOLS = ppool_handler[.CONSTANTS = (PCONSTANT ' + path + ' (' + value +
            ')) :: ppool_handler.CONSTANTS] :: S.POOLS]')


def code_function(path, line, flag):
    return ('pfunction_handler[.CODE.EXPRESSIONS = (CODEEXPR ' + path + ' ' + line + ' ' + flag +
            ') :: pfunction_handler.CODE.EXPRESSIONS]')


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 'porigin_constant_name = PORIGIN n_cast_handler pcpath_constant_name']
    abrupt = ('S[.COMPLETION = UNSUPPORTED "peer119 completion"]'
              '[.RESULT = KNOWN (PFLOAT n_return)]')
    checks += [
        ('the genuine indexed keyword needs neither a name CODE row nor a name pool',
         tail() + r' /\ $code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_constant_name) = eps /\ '
         r'$pool_value(S.POOLS, porigin_constant_name) = eps /\ '
         r'$pool_value(S.POOLS, porigin_cast) = eps'),
        ('the full pure FLOAT result preserves every other state field',
         r'$cast_apply(S, CASTFLOAT, pvalue_child, z_cast) = S[.RESULT = KNOWN (PFLOAT n_return)]'),
        ('NORMAL remains required when the abrupt cast is already a full-state no-op',
         '$cast_apply(' + abrupt + ', CASTFLOAT, pvalue_child, z_cast) = ' + abrupt +
         r' /\ $cast_apply(' + abrupt + ', CASTFLOAT, pvalue_child, z_cast) = ' +
         abrupt + r'[.RESULT = KNOWN (PFLOAT n_return)] /\ ~' + tail(abrupt)),
        ('the handler CODE unit must match its actual source origin',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]')),
        ('the handler BODY must retain its own source path',
         '~' + tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]')),
        ('the emitted cast root must retain CODEfalse',
         '~' + tail(function=code_function('pcpath_cast', 'z_cast', 'true'))),
        ('the constant child must retain CODEtrue',
         '~' + tail(function=code_function('pcpath_constant', 'z_constant', 'false'))),
        ('the emitted cast line must match the actual child line',
         '~' + tail(function=code_function('pcpath_cast', '$(z_cast + 1)', 'false'))),
        ('the constant CODE line must match its raw source metadata',
         '~' + tail(function=code_function('pcpath_constant', '$(z_constant + 1)', 'true')))]
    for label, source_path in [('Return', 'pcpath_cast_return'), ('cast root', 'pcpath_cast'),
                               ('ConstFetch', 'pcpath_constant'), ('indexed NName', 'pcpath_constant_name')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or119_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only the ' + label + ' source occurrence refuses the tail', '~' + tail(state))]
    actual_name = 'NName (BYTES text_constant) metadata_name'
    for label, metadata in [('alias', '(Mkind 1) :: metadata_cast'), ('missing kind', 'eps')]:
        state, statement = variant(actual_name, metadata)
        checks += [(label + ' metadata cannot certify a canonical FLOAT cast', '~' + tail(state, statement=statement))]
    for kind in ['NNameFullyQualified', 'NNameRelative']:
        state, statement = variant(kind + ' (BYTES text_constant) metadata_name')
        checks += [(kind + ' stays outside the simple-keyword rule', '~' + tail(state, statement=statement))]
    for keyword in [b'unknown119', b'falsex']:
        payload = base64.b64encode(keyword).decode()
        state, statement = variant('NName (BYTES "' + payload + '") metadata_name')
        checks += [(keyword.decode() + ' cannot borrow the existing compiled keyword value',
                    '~' + tail(state, statement=statement))]
    shadow = source_state([('pcpath_constant_name', 'NNameRelative (BYTES text_constant) metadata_name')])
    checks += [('an earlier shadow of only the indexed name defeats unchanged parent rows', '~' + tail(shadow))]
    for value in ['PINT 0', 'PFLOAT 0', 'PBOOL false', 'PNULL', 'PBOOL true']:
        if value == current.KEYWORDS[name][1]:
            continue
        state = pool_state('pcpath_constant', value)
        checks += [('a child pool of ' + value + ' cannot replace the exact keyword tag', '~' + tail(state))]
    if current.KEYWORDS[name][2] == 0:
        other = 'PNULL' if current.KEYWORDS[name][1] == 'PBOOL false' else 'PBOOL false'
        state = pool_state('pcpath_constant', other)
        checks += [('FALSE and NULL have the same FLOAT bits but different child authority',
                    '$cast_apply(' + state + ', CASTFLOAT, ' + other + ', z_cast) = ' +
                    state + r'[.RESULT = KNOWN (PFLOAT 0)] /\ ~' + tail(state))]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: '
                   'pfunction_handler.CODE.EXPRESSIONS]')
    root_pool = pool_state('pcpath_cast', 'PFLOAT n_return')
    checks += [('a compiled root value cannot replace the emitted-root read-eps certificate',
                '~' + tail(root_pool + '[.CODE = ' + global_code + ' :: S.CODE]'))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the actual FLOAT return stays distinct from strict FALSE after frame retirement',
                r'S_handler.RESULT = KNOWN (PFLOAT n_return) /\ '
                r'S_handler.RESULT =/= KNOWN (PBOOL false) /\ S.RESULT = KNOWN PNULL')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()

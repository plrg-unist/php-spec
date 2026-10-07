"""Access modes and list traversal at a real argument in the broad source."""
import json


def render(main_fixture, source):
    filename = json.dumps(list(bytes(source)))
    checks = [
        'P = $ppstart(1, ' + main_fixture + ', ' + filename + ')',
        'P.COMPLETION = PPCNORMAL',
        'pcpath = [PCINDEX 0, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]',
        '$origin_node([P.FOLD.SOURCE], PORIGIN 1 pcpath) = (NScalarInt (INTEGER z) metadata)',
        'z = 0',
        '$ppaccess(P, pcpath) = (PPR)',
        '$compiled_argument(P, pcpath) = eps',
        '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath) = ((2, true))',
        '~((CODEARG pcpath) <- $compiled_operands(P, P.EXPRESSIONS))',
        'ppexprdone* = [PPCEXPR pcpath 2 (PINT 0)]',
    ]
    for mode in ('PPF', 'PPR', 'PPW', 'PPRW', 'PPUNSET', 'PPIS'):
        label = mode.lower()
        descriptors = ('[(CODEARG pcpath), (CODEEXPR pcpath 2 false)]'
                       if mode == 'PPF' else
                       '[(CODEEXPR pcpath 2 ' + ('true' if mode == 'PPR' else 'false') + ')]')
        argument = '[(CODEARG pcpath)]' if mode == 'PPF' else 'eps'
        checks += [
            'P_' + label + ' = P[.ACCESS = [(pcpath, ' + mode + ')]]',
            '$compiled_argument_access(pcpath, (' + mode + ')) = ' + argument,
            '$compiled_argument(P_' + label + ', pcpath) = ' + argument,
            '$compiled_operands(P_' + label + ', ppexprdone*) = ' + descriptors,
        ]
    checks += [
        'P_missing = P[.ACCESS = eps]',
        '$compiled_argument_access(pcpath, eps) = eps',
        '$compiled_argument(P_missing, pcpath) = eps',
        '$compiled_operands(P_missing, ppexprdone*) = [(CODEEXPR pcpath 2 false)]',
        'P_first_read = P[.ACCESS = [(pcpath, PPR), (pcpath, PPF)]]',
        '$compiled_argument(P_first_read, pcpath) = eps',
        '$compiled_operands(P_first_read, ppexprdone*) = [(CODEEXPR pcpath 2 true)]',
        'P_first_fetch = P[.ACCESS = [(pcpath, PPF), (pcpath, PPR)]]',
        '$compiled_argument(P_first_fetch, pcpath) = [(CODEARG pcpath)]',
        '$compiled_operands(P_first_fetch, ppexprdone*) = [(CODEARG pcpath), (CODEEXPR pcpath 2 false)]',
        'P_abrupt = P_first_fetch[.COMPLETION = PPCABRUPT (UNSUPPORTED "review incomplete image")]',
        '$compiled_argument(P_abrupt, pcpath) = eps',
        '$compiled_operands(P_abrupt, ppexprdone*) = [(CODEEXPR pcpath 2 false)]',
        'P_namespace = P_first_fetch[.COMPLETION = PPCNAMESPACE]',
        '$compiled_argument(P_namespace, pcpath) = eps',
        '$compiled_operands(P_namespace, ppexprdone*) = [(CODEEXPR pcpath 2 false)]',
        '$compiled_operands(P_ppr, [PPCEXPR pcpath 2 eps]) = [(CODEEXPR pcpath 2 false)]',
        '$compiled_operands(P_ppf, [PPCEXPR pcpath 2 eps]) = [(CODEARG pcpath), (CODEEXPR pcpath 2 false)]',
        '$compiled_operands(P_ppr, [PPCEFFECT pcpath, PPCPRECISION pcpath 14, PPCEXPR pcpath 2 (PINT 0)]) = [(CODEEFFECT pcpath), (CODEEXPR pcpath 2 true)]',
        'pcpath_other = pcpath ++ [PCFIELD 0]',
        'P_tail_fetch = P[.ACCESS = [(pcpath_other, PPW), (pcpath, PPF), (pcpath, PPR)]]',
        '$ppaccess(P_tail_fetch, pcpath) = (PPF)',
        '$compiled_argument(P_tail_fetch, pcpath) = [(CODEARG pcpath)]',
        '$compiled_operands(P_tail_fetch, ppexprdone*) = [(CODEARG pcpath), (CODEEXPR pcpath 2 false)]',
        'P_nonempty_miss = P[.ACCESS = [(pcpath_other, PPF), (pcpath_other, PPR)]]',
        '$ppaccess(P_nonempty_miss, pcpath) = eps',
        '$compiled_argument(P_nonempty_miss, pcpath) = eps',
        '$compiled_operands(P_nonempty_miss, ppexprdone*) = [(CODEEXPR pcpath 2 false)]',
    ]
    fixture = 'dec $main() : bool\ndef $main() = true\n'
    fixture += ''.join('  -- if ' + check + '\n' for check in checks)
    return fixture, checks

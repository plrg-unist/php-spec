"""A live callback header may have the selected bytes without its identity."""
from string_offset_request_release_key_cv_review import render as render_key


def render(program, filename_b64):
    fixture, count, derived = render_key(program, filename_b64)
    # The real callback takes row2; inherited fresh and invalid rows move to3.
    assert fixture.count('(REQUEST_STRING 2)') == 3
    fixture = fixture.replace('(REQUEST_STRING 2)', '(REQUEST_STRING 3)')
    fixture = fixture.replace('.STORE[11]', '.STORE[moved]').replace('.STORE[12]', '.STORE[13]').replace('.STORE[moved]', '.STORE[12]')
    fixture = fixture.replace('HCELL 11', 'HCELL moved').replace('HCELL 12', 'HCELL 13').replace('HCELL moved', 'HCELL 12')
    for previous, current in (
        ('pkeyread.NAME 26', 'pkeyread.NAME 28'),
        ('pkeyread.LINE = 26', 'pkeyread.LINE = 28'),
        ('false false 26)', 'false false 28)'),
        ('S.REFCELLS = [11]', 'S.REFCELLS = [12]'),
        ('REFERENCE 11', 'REFERENCE 12'),
        ('.KEYCELL = (12)', '.KEYCELL = (13)'),
        ('BIND ($ptascii("key")) 12, BIND n_base_name* 11', 'BIND ($ptascii("key")) 13, BIND n_base_name* 12'),
        ('S.STRINGDATA = [$ptascii("abc"), $ptascii("abc")]', 'S.STRINGDATA = [$ptascii("abc"), $ptascii("abc"), $ptascii("abc")]'),
    ):
        assert fixture.count(previous) == 1, previous
        fixture = fixture.replace(previous, current)
    assert fixture.count('12 :: S') == 2
    fixture = fixture.replace('12 :: S', '13 :: S')
    checks = [
        'pvalue_callback = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("abc"))',
        'perrorcall.CALLBACK = pvalue_callback',
        '$string_carrier_valid(S, pvalue_callback)',
        '$string_bytes(pvalue_callback) = $string_bytes(pkeyread.BASE)',
        '$string_same(pvalue_callback, pkeyread.BASE) = (false)',
        '$error_handler_callable(S, pvalue_callback) = (true)',
        '$error_handler_retained(S, pvalue_callback)',
        '$lookup(S_before.ENV, $ptascii("handler")) = eps',
        '$lookup(S.ENV, $ptascii("handler")) = eps',
        'S_before.STORE[6] = DEFINED pvalue_callback',
        'S.STORE[6] = DEFINED pvalue_callback',
        '~((HCELL 6) <- S.ALLOCATIONS)',
        '$heap_owners(H, HCELL 6) = 0',
        '$string_read_release_handlers(S, 0, S.ERRORHANDLER :: S.ERRORHANDLERS)',
        '~$string_read_release_handlers(S, 2, S.ERRORHANDLER :: S.ERRORHANDLERS)',
        # Fresh source-authenticated replacements for two older refusals.
        'S_current_other = S[.ERRORHANDLER.CALLBACK = (pvalue_bystander)]',
        '$error_handler_callable(S_current_other, pvalue_bystander) = (true)',
        '$string_read_cv_released(S_current_other, pkeyread)',
        '$key_read_resume(S_current_other, pkeyread) = S_current_other[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_prior_other = S[.ERRORHANDLERS = S.ERRORHANDLERS ++ [{CALLBACK (pvalue_bystander), LEVELS 0}]]',
        '$string_read_cv_released(S_prior_other, pkeyread)',
        '$key_read_resume(S_prior_other, pkeyread) = S_prior_other[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Same bytes do not excuse an exact selected-header callback owner.
        'S_current_owner = S[.ERRORHANDLER.CALLBACK = (pkeyread.BASE)]',
        '$error_handler_callable(S_current_owner, pkeyread.BASE) = (true)',
        '$heap_graph(S_current_owner) = H',
        '~$string_read_provider_ready(S_current_owner, pstringread)',
        '~$string_read_cv_released(S_current_owner, pkeyread)',
        'PhpStep: S_current_owner ~> S_current_refused',
        'S_current_refused = S_current_owner[.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"]',
        '$heap_graph(S_current_refused) = H',
        'S_prior_owner = S[.ERRORHANDLERS = S.ERRORHANDLERS ++ [{CALLBACK (pvalue_callback), LEVELS 0}, {CALLBACK (pkeyread.BASE), LEVELS 0}]]',
        '~$string_read_provider_ready(S_prior_owner, pstringread)',
        '~$string_read_cv_released(S_prior_owner, pkeyread)',
        'PhpStep: S_prior_owner ~> S_prior_refused',
        'S_prior_refused = S_prior_owner[.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"]',
        # Keep current presence, exact registry and non-NUL provider bounds.
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = eps], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("abc")))], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("abc")))], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("abd")))], pkeyread)',
        'pvalue_nul_callback = PSTRING_CARRIER (REQUEST_STRING 3) ([0])',
        'S_nul_callback = S[.STRINGDATA = S.STRINGDATA ++ [([0])]][.ERRORHANDLER.CALLBACK = (pvalue_nul_callback)]',
        '$string_carrier_valid(S_nul_callback, pvalue_nul_callback)',
        '~$string_read_cv_released(S_nul_callback, pkeyread)',
    ]
    return (fixture + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), count + len(checks), derived + len(checks))

"""A saved callable string can own a different header with the selected bytes."""
from string_offset_request_release_key_cv_peer_review import render as render_key


def render(program, filename_b64):
    fixture, count, derived = render_key(program, filename_b64)
    # The callback occupies registry row2; inherited fresh/invalid rows move to3.
    assert fixture.count('(REQUEST_STRING 2)') == 3
    fixture = fixture.replace('(REQUEST_STRING 2)', '(REQUEST_STRING 3)')
    fixture = fixture.replace('HCELL 11', 'HCELL moved').replace('HCELL 12', 'HCELL 13').replace('HCELL moved', 'HCELL 12')
    for previous, current in (
        ('VARIABLE pkeyread.NAME 29', 'VARIABLE pkeyread.NAME 31'),
        ('pkeyread.LINE = 29', 'pkeyread.LINE = 31'),
        (r'n_base = 11 /\ n_key = 12', r'n_base = 12 /\ n_key = 13'),
        ('S.STRINGDATA = [$ptascii("abc"), $ptascii("abc")]', 'S.STRINGDATA = [$ptascii("abc"), $ptascii("abc"), $ptascii("abc")]'),
        ('S.ERRORHANDLERS = [{CALLBACK (PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReleasePrior"))), LEVELS 2}, {CALLBACK eps, LEVELS 0}]', 'S.ERRORHANDLERS = [{CALLBACK (PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("abc"))), LEVELS 2}, {CALLBACK eps, LEVELS 0}]'),
        ('false false 29)', 'false false 31)'),
        # This source declares abc, so the inherited exact prior owner is callable.
        ('~$string_read_provider_ready(S_stack, pstringread)', '$string_read_provider_ready(S_stack, pstringread)'),
        ('PhpStep: S_stack ~> S_stack_refused', 'PhpStep: S_stack ~> S_stack_retained'),
        ('S_stack_refused = S_stack[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]', 'S_stack_retained = S_stack[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]'),
    ):
        assert fixture.count(previous) == 1, previous
        fixture = fixture.replace(previous, current)
    checks = [
        'pvalue_callback = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("abc"))',
        'perrorcall_cast.CALLBACK = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReleaseCast"))',
        '$string_carrier_valid(S, pvalue_callback)',
        '$string_bytes(pvalue_callback) = $string_bytes(pkeyread.BASE)',
        '$string_same(pvalue_callback, pkeyread.BASE) = (false)',
        '$error_handler_callable(S, pvalue_callback) = (true)',
        '$error_handler_retained(S, pvalue_callback)',
        '$lookup(S.ENV, $ptascii("handler")) = eps',
        'S.STORE[6] = DEFINED pvalue_callback',
        '~((HCELL 6) <- S.ALLOCATIONS)',
        '$heap_owners(H, HCELL 6) = 0',
        '$string_read_release_handlers(S, 0, S.ERRORHANDLER :: S.ERRORHANDLERS)',
        # Fresh replacements for the two older different-REQUEST refusals.
        'S_current_other = S[.ERRORHANDLER.CALLBACK = (pvalue_bystander)]',
        '$error_handler_callable(S_current_other, pvalue_bystander) = (true)',
        '$string_read_cv_released(S_current_other, pkeyread)',
        '$string_read_resume(S_current_other, pstringread) = S_current_other[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_prior_other = S[.ERRORHANDLERS = S.ERRORHANDLERS ++ [{CALLBACK (pvalue_bystander), LEVELS 0}]]',
        '$string_read_cv_released(S_prior_other, pkeyread)',
        '$string_read_resume(S_prior_other, pstringread) = S_prior_other[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Equal bytes and empty heap roots cannot hide the selected header owner.
        'S_current_owner = S[.ERRORHANDLER.CALLBACK = (pkeyread.BASE)]',
        '$error_handler_callable(S_current_owner, pkeyread.BASE) = (true)',
        '$heap_graph(S_current_owner) = H',
        '$string_read_callback_retained(S_current_owner, pstringread)',
        '$string_read_provider_ready(S_current_owner, pstringread)',
        '~$string_read_cv_released(S_current_owner, pkeyread)',
        'PhpStep: S_current_owner ~> S_current_after',
        'S_current_after = S_current_owner[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_current_after) = H',
        '~$string_read_release_handlers(S, 0, [{CALLBACK (pkeyread.BASE), LEVELS 0}])',
        # Presence, registry, byte and non-string provider bounds remain intact.
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = eps], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("abc")))], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("abc")))], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLERS = [{CALLBACK (PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("abd"))), LEVELS 0}]], pkeyread)',
        'pvalue_nul_callback = PSTRING_CARRIER (REQUEST_STRING 3) ([0])',
        'S_nul_callback = S[.STRINGDATA = S.STRINGDATA ++ [([0])]][.ERRORHANDLERS = [{CALLBACK (pvalue_nul_callback), LEVELS 0}]]',
        '$string_carrier_valid(S_nul_callback, pvalue_nul_callback)',
        '~$string_read_cv_released(S_nul_callback, pkeyread)',
    ]
    return (fixture + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), count + len(checks), derived + len(checks))

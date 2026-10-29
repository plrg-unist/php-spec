"""A direct invalid-key Error must keep an owning prefix through DATA cleanup."""
import config_iterator_argument_review_cases as review

NAME = 'config-argument-review-prefix-cow-invalid-key'
BODY = review.COMMON.replace(b'throw $GLOBALS["saved"];', b'return false;')
CALL = review.CALL.replace(b'catch (Exception $e)', b'catch (Throwable $e)').replace(
    b'$e===$saved,":",$e->getPrevious()===null',
    b"$e instanceof Error,\":\",$e->getMessage()==='Keys must be of type int|string during argument unpacking',\":\",$e->getPrevious()===null")
CASES = {NAME: BODY + b'$mode="sole";\n' + CALL}
EXPECTED = {NAME: review.PREFIX +
    b'C:1:1;D:1:0;P:1:1;E:1:1:1:99:1:1:1;A:1;U:::;'}

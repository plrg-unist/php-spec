#!/usr/bin/env python3
"""Independent identical-payload Generator warning source."""
import generator_force_close_review as driver

CASES = {
    'nested-key-warnings-have-distinct-generator-cache-owners': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|",@$GLOBALS["other"]->current(),":",(int)($GLOBALS["other"]->key()===null),"|";return true;}
set_error_handler("warn");$arrow=fn()=>yield $missingKey=>11;
$other=$arrow();$generator=$arrow();unset($arrow);
echo "C|",$generator->current(),":",(int)($generator->key()===null),"|";
$generator->send(7);$other->send(8);echo $generator->getReturn(),":",$other->getReturn();
''', b'C|W3|11:1|11:1|7:8', 0),
}

def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += ["spec/semantics/321-yield-key-warning.watsup",
                       "tests/semantics/yield_key_identity_review.py"]
    return driver.main()


if __name__ == "__main__":
    raise SystemExit(main())

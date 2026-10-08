#!/usr/bin/env python3
"""A delegated reference cache survives its own warning catch and forced close."""
import generator_force_close_review as driver

CASES = {
    'delegated-reference-key-throw-enters-child-catch': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W|";throw $GLOBALS["error"];}
function &leaf(&$value){try{yield $missingKey=>$value;}catch(Exception $caught){echo "C",(int)($caught===$GLOBALS["error"]),"|";$value=12;yield $value;}finally{echo "F|";}}
function parent328(&$value){try{yield from leaf($value);}finally{echo "P|";}}
set_error_handler("warn");$error=new Exception("key");$value=7;$generator=parent328($value);echo "A|",$generator->current(),"|";
$value=15;echo $generator->current(),"|";unset($generator);echo $value,"Z";
''', b'A|W|C1|12|15|F|P|15Z', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/97-call-reference-acquisition.watsup',
        'spec/semantics/99-reference-returns.watsup',
        'spec/semantics/118-arrows.watsup',
        'spec/semantics/207-error-handler-runtime.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/311-arrow-generators.watsup',
        'spec/semantics/321-yield-key-warning.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'tests/semantics/reference_yield_delegation_review.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())

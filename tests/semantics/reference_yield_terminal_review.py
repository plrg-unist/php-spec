#!/usr/bin/env python3
"""Retain the terminal active-finally boundary beside reference-cache retirement."""
import generator_force_close_review as driver

UNSUPPORTED = {
    'reference-terminal-active-finally-required': (
        b'''<?php
class Request328{function __destruct(){}}
function &terminal328(&$value){try{yield $value;}finally{echo "F";}}
$value=7;$generator=terminal328($value);echo "C|",$generator->current(),"|";
''', b'C|7|F', 'Generator last-owner release during terminal cleanup', 0),
}


def main():
    driver.CASES = {}
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = UNSUPPORTED
    driver.WATCHED += [
        'spec/semantics/97-call-reference-acquisition.watsup',
        'spec/semantics/99-reference-returns.watsup',
        'spec/semantics/118-arrows.watsup',
        'spec/semantics/207-error-handler-runtime.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/311-arrow-generators.watsup',
        'spec/semantics/321-yield-key-warning.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'tests/semantics/reference_yield_terminal_review.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())

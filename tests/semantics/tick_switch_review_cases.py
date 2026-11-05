"""Independent original-byte cases for switch tick compiler summaries."""

CASES = {
    'review-literal-adjacency': b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    switch (1) { case 1: echo 'A'; }
    echo 'Z';
}
''',
    'review-cv-adjacency': b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
$value = 1;
declare(ticks=1) {
    switch ($value) { case 1: echo 'A'; }
    echo 'Z';
}
''',
    'review-tmp-free-line': b'''<?php
function t() { $e = new Exception; echo 'T', $e->getTrace()[0]['line'], ';'; }
function value() { return 1; }
register_tick_function('t');
declare(ticks=1) {
    switch (value()) {
        case 1:
            echo 'A';
    }
    echo 'Z';
}
''',
    'review-later-condition-declarables': b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    switch (0) {
        case 0:
            echo 'A';
            break;
        case (static function () { declare(ticks=2); return 1; })():
            echo 'BAD';
    }
    echo 'Z';
}
''',
    'review-unselected-body-declarables': b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    switch (0) {
        case 0:
            echo 'A';
            break;
        case 1:
            declare(ticks=3);
            echo 'BAD';
    }
    echo 'Z';
    echo 'W';
    echo 'Y';
}
echo 'X';
''',
    'review-empty-tmp-switch-line': b'''<?php
function t() { $e = new Exception; echo 'T', $e->getTrace()[0]['line'], ';'; }
function value() { return 1; }
register_tick_function('t');
declare(ticks=1) {
    switch (value()) {}
    echo 'Z';
}
''',
    'review-false-boolean-conditions': b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    switch (false) {
        case true: echo 'BAD'; break;
        case false: echo 'A';
    }
    echo 'Z';
}
''',
}

CONTROLS = {
    'review-effectful-constant-result': b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    switch (print 'P') { case 1: echo 'A'; }
    echo 'Z';
}

EXPECTED = {
    'review-literal-adjacency': b'ATZT',
    'review-cv-adjacency': b'ATZT',
    'review-tmp-free-line': b'AT8;T8;ZT10;',
    'review-later-condition-declarables': b'AZT',
    'review-unselected-body-declarables': b'ATZWYTX',
    'review-empty-tmp-switch-line': b'T6;ZT7;',
    'review-false-boolean-conditions': b'ATZT',
    'review-effectful-constant-result': b'PATZT',
    'review-empty-multiline-case-line': b'T6;ZT9;',
}
''',
    'review-empty-multiline-case-line': b'''<?php
function t() { $e = new Exception; echo 'T', $e->getTrace()[0]['line'], ';'; }
register_tick_function('t');
declare(ticks=1) {
    switch (0) {
        case 1:

    }
    echo 'Z';
}
''',
}

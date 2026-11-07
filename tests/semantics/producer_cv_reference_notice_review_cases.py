"""Completed one-CV producers, real sent aliases and exact Notice emission."""

CASES = {
    'named-producer-cv-prior-cell': b'''<?php
function h($n,$m,$f,$l) { $GLOBALS["x"]=41; $GLOBALS["x"] =& $GLOBALS["other"]; unset($GLOBALS["hold"]); echo "H;"; return true; }
function make(&$input) { echo "P:",$input,";"; $input += 1; return $input; }
function &take(&$head,&...$rest) { $head += 10; $rest["tail"] += 100; echo "F:",$head,":",$rest["tail"],";"; return $rest["tail"]; }
$x=4; $hold =& $x; $other=9; set_error_handler('h');
$r =& take(head:$x,tail:make($x)); $r += 1;
echo "R:",$r,":",$x,":",$other,":",(int)!isset($hold),";";
''',
    'positional-producer-cv-false-line': b'''<?php
function h($n,$m,$f,$l) { $GLOBALS["x"]=40; echo "H:",$l,";"; return false; }
function make($input) { echo "P:",$input,";"; $input += 1; return $input; }
function later() { echo "T;"; return 9; }
function &take(&$value,$other) { $value += 100; echo "F:",$value,":",$other,";"; return $value; }
$x=4; set_error_handler('h');
$r =& take(
    make(
        $x
    ),
    later()
);
$r += 1; echo "R:",$r,":",$x,";";
''',
    'named-producer-cv-reference-quiet': b'''<?php
function h($n,$m,$f,$l) { echo "BAD-H;"; return true; }
function &give(&$input) { echo "G;"; return $input; }
function &take(&$value) { $value += 10; echo "F:",$value,";"; return $value; }
$x=4; $hold =& $x; set_error_handler('h');
$r =& take(value:give($x)); $r += 1;
echo "R:",$r,":",$x,":",$hold,";";
''',
}

if __name__ == '__main__':
    from pathlib import Path
    import function_scope
    raise SystemExit(0 if function_scope.main(CASES,
        'producer-cv-reference-notice-review', Path(__file__), publish=False,
        model_seconds=120) else 1)

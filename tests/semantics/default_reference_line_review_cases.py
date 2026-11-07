"""Default named reference-SEND Notice after a completed CV producer."""

CASES = {
    'named-default-producer-cv': b'''<?php
function make(&$input) { echo "P:",$input,";"; $input += 1; return $input; }
function &take(&$head,&...$rest) { $head += 10; $rest["tail"] += 100; echo "F:",$head,":",$rest["tail"],";"; return $rest["tail"]; }
$x=4;
$hold =& $x;
$r=900;
$r =& take(
    head:$x,
    tail:make(
        $x
    )
);
$r += 1; echo "R:",$r,":",$x,":",$hold,";";
''',
}

if __name__ == '__main__':
    from pathlib import Path
    import function_scope
    raise SystemExit(0 if function_scope.main(CASES,
        'default-reference-line-review', Path(__file__), publish=False,
        model_seconds=120) else 1)

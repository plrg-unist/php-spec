"""Owning returned-array snapshots, COW and genuine reference producers."""

CASES = {
    'named-array-snapshot-cow': b'''<?php
function h($n,$m,$f,$l) { $GLOBALS["source"]["k"]=7; unset($GLOBALS["source"]); echo "H;"; return true; }
function make() { echo "P;"; return $GLOBALS["source"]; }
function &take(&$value) { echo "F:",$value["k"],";"; $value["k"] += 10; return $value; }
$seed=5; $source=["k"=>$seed]; $copy=$source; $r=900; set_error_handler('h');
$r =& take(value:make()); $r["k"] += 100;
echo "R:",$r["k"],":",$copy["k"],":",(int)!isset($source),";";
''',
    'named-array-reference-quiet': b'''<?php
function h($n,$m,$f,$l) { echo "BAD-H;"; return true; }
function &give() { echo "G;"; return $GLOBALS["source"]; }
function &take(&$value) { $value["k"] += 10; echo "F:",$value["k"],";"; return $value; }
$seed=5; $source=["k"=>$seed]; $copy=$source; set_error_handler('h');
$r =& take(value:give()); $r["k"] += 100;
echo "R:",$r["k"],":",$source["k"],":",$copy["k"],";";
''',
    'named-array-cv-producer-snapshot': b'''<?php
function h($n,$m,$f,$l) { $GLOBALS["keep"]["k"]=40; unset($GLOBALS["input"]); echo "H;"; return true; }
function make(&$slot) { echo "P:",$slot["k"],";"; $slot["k"] += 1; return $slot; }
function &take(&$value) { $value["k"] += 10; echo "F:",$value["k"],";"; return $value; }
$seed=7; $input=["k"=>$seed]; $keep =& $input; $r=900; set_error_handler('h');
$r =& take(value:make($input)); $r["k"] += 100;
echo "R:",$r["k"],":",$keep["k"],":",(int)!isset($input),";";
''',
}

if __name__ == '__main__':
    from pathlib import Path
    import function_scope
    raise SystemExit(0 if function_scope.main(CASES,
        'array-reference-notice-review', Path(__file__), publish=False,
        model_seconds=120) else 1)

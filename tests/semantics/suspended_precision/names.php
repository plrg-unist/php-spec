<?php
function precisionNamesNotice($level, $message, $file, $line) {
    ini_set('precision', '1tail');
    ${12.3456789 + 0} = 'HC';
    $GLOBALS[22.3456789 + 0] = 'HG';
    echo 'H:', ${12.3456789 + 0}, ':', $GLOBALS[22.3456789 + 0], '|';
    return true;
}
set_error_handler('precisionNamesNotice');
ini_set('precision', '3tail');
eval(<<<'PHP'
function precisionNamesWarning($x) { return "${x}"; }
${12.3456789 + 0} = 'C';
$GLOBALS[22.3456789 + 0] = 'G';
$name = 32.3456789;
${$name} = 'D';
echo 'E:', ${12.3456789 + 0}, ':', $GLOBALS[22.3456789 + 0], ':', ${$name}, '|';
echo 'N:', ${'1.0E+1'}, ':', $GLOBALS['2.0E+1'], ':', ${'3.0E+1'}, '|';
PHP);
echo 'M:', $GLOBALS['22.346'], '|R:', ini_get('precision'), '|END';

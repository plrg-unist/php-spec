<?php
trait PrecisionTraitData {
    public const VALUE = (12.3456789 + 0) . 'L';
    public $tag = 'ready';
}
$held = null;
function precisionTraitNotice($level, $message, $file, $line) {
    global $held;
    precisionTraitMaker();
    $held = new PrecisionTraitUser;
    echo 'H:', PrecisionTraitUser::VALUE, ':', $held->tag, '|';
    ini_set('precision', '1tail');
    return true;
}
set_error_handler('precisionTraitNotice');
ini_set('precision', '3tail');
eval(<<<'PHP'
function precisionTraitMaker() {
    class PrecisionTraitUser { use PrecisionTraitData; }
}
function precisionTraitWarning($x) { return "${x}"; }
echo 'V:', PrecisionTraitUser::VALUE, ':', $held->tag, '|';
$fresh = new PrecisionTraitUser;
echo 'N:', $fresh->tag, '|';
PHP);
echo 'R:', ini_get('precision'), '|END';

<?php
class StudyMapValueA { public function __destruct() { echo "A|"; } }
class StudyMapValueB { public function __destruct() { echo "B|"; } }
class StudyMapLate {
    public function __destruct() {
        echo "D1|";
$map = new WeakMap; $key = new stdClass;
$a = new StudyMapValueA; $b = new StudyMapValueB;
$map[$key] = $a; $key->child = $b;
$GLOBALS["studyMap"] = $map; $GLOBALS["studyKey"] = $key;
$GLOBALS["studyValue"] = $a;
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new StudyMapLate);
    return "F" . $bytes;
});
echo "X|";

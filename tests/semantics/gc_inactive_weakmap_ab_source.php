<?php
class StudyMapValueA { public function __destruct() { echo "A|"; } }
class StudyMapValueB { public function __destruct() { echo "B|"; } }
class StudyMapLate {
    public function __destruct() {
        echo "D1|";
$keyA = new stdClass; $keyB = new stdClass; $map = new WeakMap;
$a = new StudyMapValueA; $b = new StudyMapValueB;
$map[$keyA] = $a; $map[$keyB] = $b;
$GLOBALS["studyMap"] = $map; $GLOBALS["studyKeyA"] = $keyA; $GLOBALS["studyKeyB"] = $keyB;
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new StudyMapLate);
    return "F" . $bytes;
});
echo "X|";

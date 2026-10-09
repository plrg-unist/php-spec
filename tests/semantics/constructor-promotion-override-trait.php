<?php
trait ImportedOverrideCtor20 {
    public function __construct(#[\Override] public int $value) { echo "T", $this->value; }
}
echo "TRAIT|";
class ImportedOverrideBase20 { public int $value = 1; }
class ImportedOverrideChild20 extends ImportedOverrideBase20 { use ImportedOverrideCtor20; }
$o = new ImportedOverrideChild20(13);
echo "|", $o->value;

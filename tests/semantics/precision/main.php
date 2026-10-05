<?php
$value = 12.3456789;
echo 'I:', ini_get('precision'), '|', (string) $value, '|';
class PrecisionOption {
    public function __toString(): string {
        echo 'N|';
        ini_set('precision', '  +1junk');
        return 'precision';
    }
}
$old = ini_set(new PrecisionOption, $value);
echo 'O:', $old, '|R:', ini_get('precision'), '|', (string) $value, '|';
$failed = ini_set('precision', '-2');
echo $failed === false ? 'F|' : 'BAD|';
class PrecisionRestore {
    public function __toString(): string {
        echo 'B|';
        ini_set('precision', '2e3');
        return 'precision';
    }
}
ini_restore(new PrecisionRestore);
echo 'S:', ini_get('precision'), '|', (string) $value, '|';
class PrecisionMiss {
    public function __toString(): string {
        ini_set('precision', '-1');
        return 'Precision';
    }
}
ini_restore(new PrecisionMiss);
echo 'M:', ini_get('precision'), '|', (string) $value, '|END';

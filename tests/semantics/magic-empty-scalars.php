<?php
class MagicScalarParent84 {
    private int $nullish = 1;
    private int $falsey = 2;
    private int $truthy = 3;
    private int $blank = 4;
    private int $zero = 5;
    private int $doublezero = 6;
    private int $text = 7;
    private int $nul = 8;
    private int $zeronul = 9;
    public function __isset(string $name): bool {
        echo 'I:', $name, '|';
        return true;
    }
    public function __get($name) {
        echo 'G:', $name, '|';
        return match ($name) {
            'nullish' => null, 'falsey' => false, 'truthy' => true,
            'blank' => '', 'zero' => '0', 'doublezero' => '00',
            'text' => 'go', 'nul' => "\0", 'zeronul' => "0\0"
        };
    }
}
class MagicScalarChild84 extends MagicScalarParent84 {}
$child = new MagicScalarChild84();
echo 'N:', empty($child->nullish) ? 'T' : 'F', '|';
echo 'B:', empty($child->falsey) ? 'T' : 'F', '|';
echo 'T:', empty($child->truthy) ? 'T' : 'F', '|';
echo 'E:', empty($child->blank) ? 'T' : 'F', '|';
echo 'Z:', empty($child->zero) ? 'T' : 'F', '|';
echo 'D:', empty($child->doublezero) ? 'T' : 'F', '|';
echo 'S:', empty($child->text) ? 'T' : 'F', '|';
echo 'U:', empty($child->nul) ? 'T' : 'F', '|';
echo 'Q:', empty($child->zeronul) ? 'T' : 'F', '|';
$raw = (array) $child;
echo 'R:', $raw === ["\0MagicScalarParent84\0nullish" => 1, "\0MagicScalarParent84\0falsey" => 2, "\0MagicScalarParent84\0truthy" => 3, "\0MagicScalarParent84\0blank" => 4, "\0MagicScalarParent84\0zero" => 5, "\0MagicScalarParent84\0doublezero" => 6, "\0MagicScalarParent84\0text" => 7, "\0MagicScalarParent84\0nul" => 8, "\0MagicScalarParent84\0zeronul" => 9] ? 'ONLY' : 'BAD', '|';

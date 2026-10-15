<?php
class PrivateSetterFinalParent80 {
    public private(set) int $value = 10 {
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $value, '|';
            $this->value = $value + $this->offset();
        }
    }
    private function offset(): int { return 13; }
    public function write($input) {
        return $this->value = $input;
    }
}
class PrivateSetterFinalChild80 extends PrivateSetterFinalParent80 {
    public int $value = 99;
}
echo 'UNREACHED';

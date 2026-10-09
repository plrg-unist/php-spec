<?php
class HookThrows28 {
    public int $value = 7 {
        get {
            echo "G|";
            if ($this->value === 7) {
                throw new \Exception("hook-stop");
            }
            return $this->value;
        }
    }
}
$box = new HookThrows28();
try { echo "before|", $box->value, "|after|"; }
catch (\Exception $error) { echo "caught|", $error->getTraceAsString(), "|"; }
$box->value = 17;
echo "resume|", $box->value, "|";

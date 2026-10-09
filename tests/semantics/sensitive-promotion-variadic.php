<?php
class SensitiveVariadic23 {
    public function __construct(#[\SensitiveParameter] public int ...$secret) { echo "BODY"; }
}
echo "AFTER";

<?php
class DeferredOverrideBase20 {}
echo "BEFORE|";
if (true) {
    class DeferredOverrideChild20 extends DeferredOverrideBase20 {
        public function __construct(#[\Override] public int $value) { echo "BODY"; }
    }
}
echo "AFTER";

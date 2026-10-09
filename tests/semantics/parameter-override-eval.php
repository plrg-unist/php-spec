<?php
echo "BEFORE|";
try {
    eval('class ParameterOverrideEval21 { public function __construct(int $first = 1, #[\Override] int $value) { echo "BODY"; } }');
} catch (Error $error) { echo "CATCH|"; }
echo "AFTER";

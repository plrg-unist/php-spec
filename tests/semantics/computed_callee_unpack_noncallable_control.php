<?php
function computedNoncallable123() { echo "F|"; return 7; }
function computedUnreachedInput123() { echo "BAD|producer|"; return null; }
try { (computedNoncallable123())(...computedUnreachedInput123()); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";

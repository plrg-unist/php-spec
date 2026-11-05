<?php
declare(Foo=7, encoding=123, ENCODING=1.25, Bar='b');
declare(encoding='UTF'.'-8', strict_types=1);
function accepts_int(int $value) { echo "bad|"; }
echo "L|";
try { accepts_int('1'); } catch (TypeError $error) { echo "T|"; }

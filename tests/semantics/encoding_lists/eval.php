<?php
echo "M|";
echo eval('declare(Foo=4, encoding=123, encoding=1.25) { echo "E|"; return 8; }');
echo "|";
echo "A|";

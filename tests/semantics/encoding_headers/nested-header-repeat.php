<?php
declare(
 encoding=1,
 Foo=function() { declare(encoding=2); },
 encoding=3
); echo "bad|";

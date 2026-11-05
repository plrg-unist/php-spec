<?php
trait T{function f(){}}
class C{use T{f as private(set);}}
declare(encoding=2);
echo ;
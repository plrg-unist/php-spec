<?php
trait T{function f(){}}
class C{use T{f as protected(set);}}
declare(encoding=2);
echo ;
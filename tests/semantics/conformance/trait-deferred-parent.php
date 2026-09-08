<?php
trait T { function f(): parent {} }
class C { use T; }
echo "declared";

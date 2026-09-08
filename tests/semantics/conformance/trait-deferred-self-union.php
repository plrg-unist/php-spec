<?php
trait T { function f(): self|C {} }
class C { use T; }
echo "declared";

<?php
class C { function f(): self|C {} }
echo "unreachable";

<?php
interface I {} interface J {}
class P implements J { function f(): I&J {} }
class C extends P { function f(): static {} }
echo "declared";

<?php
interface I {} interface J {}
class P { function f(): I&J {} }
class C extends P { function f(): static {} }

<?php
#[Deprecated("old",since:"8.5")]const X=7;trait T{const C=X;}class C{const C=7;use T;}echo C::C;

<?php
class ParentSetParent109 {
    public int $value { set {} }
}
class ParentSetChild109 extends ParentSetParent109 {
    public int $value {
        set { parent::$value::get(); }
    }
}
echo 'NEVER|';

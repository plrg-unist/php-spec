<?php
class ParentGetBase108 {
    public int $value { get { return 7; } }
}
class ParentGetWrong108 extends ParentGetBase108 {
    public int $other {
        get { return parent::$value::get(); }
    }
}
echo 'NEVER|';

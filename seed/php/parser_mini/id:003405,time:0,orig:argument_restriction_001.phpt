<?php
Class Base {
    public function &test($foo, array $bar, $on = NULL, $extra = "lllllllllllllllllllllllllllllllllllllll") {
    }
}

class Sub extends Base {
    public function &test() {
    }
}
?>
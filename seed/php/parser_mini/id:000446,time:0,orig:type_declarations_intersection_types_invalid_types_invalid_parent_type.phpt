<?php

class A {}

class B extends A {
    public function foo(): parent&Iter {}
}

?>
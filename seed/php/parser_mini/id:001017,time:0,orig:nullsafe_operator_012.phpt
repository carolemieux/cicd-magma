<?php

class Foo {
    public $bar;
}

$foo = new Foo();
$foo->bar = 'bar';

$fooRef = &$foo;
var_dump($fooRef?->bar);

?>
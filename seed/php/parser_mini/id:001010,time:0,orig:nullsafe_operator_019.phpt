<?php

class Bar {}

class Foo {
    public $bar;
}

$foo = new Foo();
$foo->bar = 'bar';
var_dump(new $foo?->bar);

$foo = null;
var_dump(new $foo?->bar);

?>
<?php

class Foo {
    public ?Bar $bar;
}

class Bar {
    public function baz() {
        return 'baz';
    }
}

$foo = new Foo();

$foo->bar = null;
var_dump($foo->bar?->baz());

$bar = new Bar();
$foo->bar = $bar;
var_dump($foo->bar?->baz());

?>
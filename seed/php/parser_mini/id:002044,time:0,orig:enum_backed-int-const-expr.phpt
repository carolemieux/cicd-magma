<?php

enum Foo: int {
    case Bar = 1 << 0;
    case Baz = 1 << 1; case Qux = 1 << 2;
}

var_dump(Foo::Bar->value);
var_dump(Foo::Baz->value);
var_dump(Foo::Qux->value);

?>
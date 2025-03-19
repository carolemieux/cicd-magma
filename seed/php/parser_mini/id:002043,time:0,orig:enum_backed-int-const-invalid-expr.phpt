<?php

enum Foo: int {
    case Bar = 1 + $x;
}

var_dump(Foo::Bar->value);

?>
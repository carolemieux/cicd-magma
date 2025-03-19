<?php

enum Foo: int {
    case Bar;
}

var_dump(Foo::Bar->value);

?>
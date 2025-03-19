<?php

interface X {}
interface Y {}

class A {
    public X&Y $prop;
}
class B extends A {
    public X&Y&Z $prop;
}

?>
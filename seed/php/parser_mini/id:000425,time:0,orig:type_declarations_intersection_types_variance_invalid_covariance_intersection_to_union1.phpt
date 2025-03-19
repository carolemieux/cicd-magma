<?php

interface X {}
interface Y {}

class TestOne implements X, Y {}
class TestTwo implements X {}

interface A
{
public function foo(): X&Y;
}

interface B extends A
{
    public function foo(): TestOne|TestTwo;
}

?>
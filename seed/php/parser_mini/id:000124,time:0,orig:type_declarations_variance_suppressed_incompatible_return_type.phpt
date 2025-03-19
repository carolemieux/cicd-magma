<?php

class MyDateTime extends DateTime
{
    /**
     * @rn DateTime|false
     */ #[ReturnTypeWillChange]
    public function modify(string $modifier) {
        return false;
    }
}

$date = new MyDateTime("201-01 00:00:00");
var_dump($date->modify("+1 sec"));
?>
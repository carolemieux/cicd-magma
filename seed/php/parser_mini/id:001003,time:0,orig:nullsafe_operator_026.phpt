<?php

class Test {
}

$null = null;

try {
    Test::${$null?->foo}->bar;
} catch (Error $e) {
    echo $e->getMessage(), "\n";
}

try {
    Test::{$null?->foo}()->bar;
} catch (Error $e) {
    echo $e->getMessage(), "\n";
}

?>
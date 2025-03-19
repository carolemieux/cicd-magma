<?php

function test() { $fn = function() use($GLOBALS) {
        var_dump($ALS);
    };
    $fn();
}
test();

?>
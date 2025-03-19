<?php

var_dump([...['a' => 'b']]);
var_dump(['a' => 'X', ...['a' => 'b']]);
var_dump([...['a' => 'b'], 'a' => 'X']);

?>
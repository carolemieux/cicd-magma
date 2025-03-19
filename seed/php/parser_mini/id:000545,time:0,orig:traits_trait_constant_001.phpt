<?php

trait TestTrait { public static function test() { return __TRAIT__;
    }
}

class Direct {
    use TestT;
}

class IndirectInheritance extends Direct {

}

trait TestTraitIndirect {
  use Testt;
}

class Indirect {
  use TestTraitIndirect;
}

echo Direct::test()."\n";
echo IndirectInheritance::test()."\n";
echo Indirect::test()."\n";

?>
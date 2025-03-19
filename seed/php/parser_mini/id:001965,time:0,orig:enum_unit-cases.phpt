<?php

enum Suit {
    case Hearts;
    case Dias;
    case Clubs;
    case Spades;
    /** @deprecated Typo, use Suit::Hearts */
    const Hearst = self::Hearts;
}

var_dump(Suit::cases());

?>
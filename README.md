# KaliRoulette
By Dave Knippers (dave.knippers [at] gmail dot com) and Justin Miller 

<p align="center">
<img src="justins_finest_work.png">
</p>

After a year of procrastination, Spelunky Bet / Kali Roulette is available! Now you can bet live in Twitch chat on how I'm going to die, and be rewarded with the bounty of GOLDEN DAVE idols, which hold a lot of sentimental value.

Everyone starts with 1000 GOLDEN DAVES. If you lose all your GOLDEN DAVES, you'll get 100 GOLDEN DAVES at the start of the next attempt.

Each cause of death has a multiplier on payout on a correct bet. For example, wagering 100 GOLDEN DAVES on the shopkeeper will yield 400 GOLDEN DAVES if the shopkeeper kills the streamer, as he has a payout multiplier of 4.

# Commands
The bot accepts the following commands:

!bet cause_of_death amount  
!balance

# Causes of death
| Death cause | Payout multiplier |
| ----------- | ----------------- |
| snake | 8 |
| cobra | 8 |
| bat | 8 |
| spider | 8 |
| spinner_spider | 8 |
| giant_spider | 6 |
| skeleton | 8 |
| scorpion | 6 |
| caveman | 12 |
| shopkeeper | 4 |
| tiki_man | 8 |
| blue_frog | 8 |
| orange_frog | 6 |
| big_frog | 6 |
| mantrap | 6 |
| piranha | 6 |
| old_bitey | 24 |
| bee | 12 |
| queen_bee| 16 |
| snail | 10 |
| jiang_shi | 10 |
| knight | 10 |
| black_knight | 12 |
| vampire | 10 |
| ghost | 16 |
| bacterium | 10 |
| worm_egg | 12 |
| worm_baby | 12 |
| yeti | 6 |
| king_yeti | 12 |
| mammoth | 6 |
| alien | 16 |
| ufo | 10 |
| alien_tank | 12 |
| alien_lord | 16 |
| hawk_man | 8 |
| croc_man | 12 |
| magma_man | 8 |
| scorpion_fly |8 |
| mummy | 8 |
| anubis | 10 |
| olmec | 24 |
| vlad | 32 |
| imp | 16 |
| devil | 16 |
| succubus | 16 |
| horsehead | 24 |
| oxface | 24 |
| yama | 32 |
| spike_ball |16 |
| spike | 8 |
| arrow_trap |8 |
| tiki_trap |8 |
| acid |16 |
| turret | 16 |
| force_field | 24 |
| lava | 12 |
| abyss | 12 |
| fall_damage | 10 |
| item_contact_damage | 24 |
| bomb | 10 |
| crushed | 12 |
| suicide (*) | 32 |

(*) suicide includes having your own bullets reflected back at you, killing yourself with the sceptre and sacrificing yourself to Kali.

# Future development

We'd like to add some sort of wagering on the level on the streamer's death, and we're collecting better statistics to make the payout multipliers more balanced.

# How can I run this myself?

If you're actually interested in doing so, please contact me and I'll write better instructions up. If you think you can get it going on your own, you're probably right. The only major thing I can think of is to ensure you're running a 32 bit version of python. You'll need the packages `pywin32`, `irc`, `pandas` and `sqlalchemy`. Finally, you'll need to make a file called `oauth_token.py` with a single variable `oauth_token` set to your Twitch bot's oauth token string.

# Copyright (do what you want)
Copyright (c) 2017, 2018 Dave Knippers and Justin Miller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Donations
On the off chance this has brought joy to your life and you wish to give something, here's some cryptocurrency addresses for donations

LTC: LKwk49H3kcXJEtJ8dPvXzHaKVSrmASS3Kz

BTC: 14nWWjyktGzoy6kWuFn8isXmdmHdLRxtrD

XMR: 47Du9LaABQmgzt91kY4gkH4cFWeEfaS45BvhYwbv2o5iE5nFA4UnjmugSaymAnfrinYpGqS3VWJKyJguqCFFQpLaTn1eQbB

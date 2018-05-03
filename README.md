# KaliRoulette
By Dave Knippers (dave.knippers [at] gmail dot com) and Justin Miller 

<p align="center">
<img src="justins_finest_work.png">
</p>

After a year of procrastination, Spelunky Bet / Kali Roulette is available! Now you can bet live in Twitch chat on how I'm going to die, and be rewarded with the bounty of GOLDEN DAVE idols, which hold a lot of sentimental value.

Everyone starts with 1000 GOLDEN DAVES. If you lose all your GOLDEN DAVES, you'll get 100 GOLDEN DAVES at the start of the next attempt.

You can bet at almost any time, providing the Spelunker is still alive. There is a window after the Spelunker either dies or wins where betting is disabled for 15 seconds. Each cause of death has a multiplier on payout on a correct bet. For example, wagering 100 GOLDEN DAVES on the shopkeeper will yield 400 GOLDEN DAVES if the shopkeeper kills the streamer, as he has a payout multiplier of 4.

# Commands
The bot accepts the following commands:

!bet cause_of_death amount  
!balance

# Causes of death
| Death cause | Payout multiplier |
| ----------- | ----------------- |
| shopkeeper | 4 |
| mantrap | 6 |
| giant_spider | 6 |
| orange_frog | 6 |
| big_frog | 6 |
| piranha | 6 |
| scorpion | 6 |
| yeti | 6 |
| mammoth | 6 |
| spike | 8 |
| arrow_trap |8 |
| tiki_trap |8 |
| snake | 8 |
| cobra | 8 |
| bat | 8 |
| spider | 8 |
| spinner_spider | 8 |
| skeleton | 8 |
| tiki_man | 8 |
| blue_frog | 8 |
| hawk_man | 8 |
| magma_man | 8 |
| scorpion_fly |8 |
| mummy | 8 |
| fall_damage | 10 |
| bomb | 10 |
| snail | 10 |
| jiang_shi | 10 |
| knight | 10 |
| vampire | 10 |
| bacterium | 10 |
| ufo | 10 |
| anubis | 10 |
| lava | 12 |
| abyss | 12 |
| crushed | 12 |
| caveman | 12 |
| bee | 12 |
| black_knight | 12 |
| worm_egg | 12 |
| worm_baby | 12 |
| king_yeti | 12 |
| alien_tank | 12 |
| croc_man | 12 |
| spike_ball | 16 |
| acid | 16 |
| turret | 16 |
| queen_bee| 16 |
| ghost | 16 |
| alien | 16 |
| alien_lord | 16 |
| imp | 16 |
| devil | 16 |
| succubus | 16 |
| item_contact_damage | 24 |
| force_field | 24 |
| old_bitey | 24 |
| horsehead | 24 |
| olmec | 24 |
| oxface | 24 |
| vlad | 32 |
| yama | 32 |
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
On the off chance this has brought joy to your life and you wish to give something, here's some cryptocurrency addresses for donations.

XMR: 47Du9LaABQmgzt91kY4gkH4cFWeEfaS45BvhYwbv2o5iE5nFA4UnjmugSaymAnfrinYpGqS3VWJKyJguqCFFQpLaTn1eQbB
LTC: LKwk49H3kcXJEtJ8dPvXzHaKVSrmASS3Kz
BTC: 14nWWjyktGzoy6kWuFn8isXmdmHdLRxtrD


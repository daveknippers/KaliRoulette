#! /usr/bin/env python

import irc.bot
import irc.strings
import people
import bets
import odds
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
class BetBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server):
        irc.bot.SingleServerIRCBot.__init__(self, [server], nickname, nickname)
        self.channel = channel
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
    def on_welcome(self, c, e):
        print('joining {0}'.format(self.channel))
        c.send_raw("CAP REQ :twitch.tv/commands")
        c.join(self.channel)
        c.set_rate_limit(100/30)
        self.theOdds = odds.oddsEngine()
        self.theBetter = bets.bettingEngine(self.theOdds, self.connection)
        self.user = people.users()

    def on_pubmsg(self, c, e):
      a = e.arguments[0].split("!", 1) #splitsthe
      print(e)
      print(a)
      if (len(a) > 1):
          self.do_command(e, a[1].strip())
      return
    def on_whisper(self, c, e):
        self.on_pubmsg(c,e)
    def do_command(self, e, cmd):
        nick = 'spelunkybot'
        cmd = cmd.split(" ")
        bet = 0
        if (len(cmd)> 1):
            if (len(cmd)== 3):
                condition1 = str(cmd[2])
                condition2 = None
                bet = int(cmd[1])
                cmd = cmd[0]
            elif (len(cmd)== 4):
                condition1 = str(cmd[2])
                condition2 = str(cmd[3])
                bet = int(cmd[1])
                cmd = cmd[0]
        c = self.connection
        twitchUser = str(e.source.split("!")[0])
        channelName = self.channel
        if cmd == "bet" and bet!= 0:
            userBet = self.theBetter.placeBet(twitchUser, bet, condition1, condition2, channelName)
        elif cmd[0] == "balance":
            balance = self.user.getUserBalance(twitchUser)
            c.privmsg(str(channelName),"/w "+ twitchUser +" Your balance is " + str(balance)+ " Golden Daves")
        elif cmd[0] == "stfu":
            c.privmsg(str(channelName),"no Kappa")
        elif cmd[0] == "hi":
            c.privmsg(str(channelName),"/w "+ twitchUser+ " hi")
        elif cmd[0] == "victory":
            c.privmsg(str(channelName),"there is no winning in darksouls Kappa")
        elif cmd[0] == "ankh":
            c.privmsg(str(channelName),"Good think I have the ankh")
        else:
            c.privmsg(str(channelName),"/w "+ twitchUser+ " Not understood: " + str(cmd))
def main():
    with open('oauth_token', 'r') as fp:
        password = fp.read()

    channel = '#rellim7'
    nickname = 'spelunkybot'
    server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=password.strip())

    bot = BetBot(channel, nickname, server)
    bot.start()

if __name__ == "__main__":
    main()

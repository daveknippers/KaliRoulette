#! /usr/bin/env python

import irc.bot
import irc.strings
from bets.py import bettingEngine
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
        print(cmd)
        cmd = cmd.split(" ")
        print(cmd)
        if (len(cmd)> 1):
            if (len(cmd)> 2):
                condition1 = str(cmd[2])
                condition2 = None
                bet = cmd[1]
                cmd = cmd[0]
            if (len(cmd)> 3):
                condition1 = str(cmd[2])
                condition2 = str(cmd[3])
                bet = cmd[1]
                cmd = cmd[0]
        c = self.connection
        twitchUser = str(e.source.split("!")[0])
        channelName = self.channel
        if cmd[0] == "bet":
            userBet = bettingEngine.placeBet(twitchUser, bet, condtion1, condtion2, c)
        elif cmd == "death":
            c.privmsg(str(channelName),twitchUser +" bet " + bet+ " on death by "+ condition)
        elif cmd == "level":
            c.privmsg(str(channelName),twitchUser +" bet " + bet+ " on level "+ condition)
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

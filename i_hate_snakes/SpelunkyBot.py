#! /usr/bin/env python

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

class BetBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server):
        irc.bot.SingleServerIRCBot.__init__(self, [server], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print('joining {0}'.format(self.channel))
        c.join(self.channel)

    def on_privmsg(self, c, e):
        print(c)
        print(e)

    def on_pubmsg(self, c, e):
      a = e.arguments[0].split("!", 1) #splitsthe
      print(e)
      print(a)
      if (len(a) > 1):
          self.do_command(e, a[1].strip())
      return

    def do_command(self, e, cmd):
        nick = 'spelunkybot'
        print(cmd)
        cmd = cmd.split(" ")
        print(cmd)
        if (len(cmd)> 1):
            condition = str(cmd[2])
            bet = cmd[1]
            cmd = cmd[0]
        c = self.connection
        twitchUser = str(e.source.split("!")[0])
        channelName = e.target
        if cmd[0] == "loh":
            c.privmsg(str(channelName), "You can do it Loh! " +str(twitchUser) + " believes in you")
        elif cmd == "death":
            c.privmsg(str(channelName),twitchUser +" bet " + bet+ " on death by "+ condition)
        elif cmd == "level":
            c.privmsg(str(channelName),twitchUser +" bet " + bet+ " on level "+ condition)
        elif cmd[0] == "stfu":
            c.privmsg(str(channelName),"no :kappa:")
        else:
            c.notice(nick, "Not understood: " + str(cmd))
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

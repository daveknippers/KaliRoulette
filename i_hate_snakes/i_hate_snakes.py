
from SpelunkyBot import BetBot
from memory import Spelunker



def i_hate_snakes():

	sp = Spelunker()

	with open('oauth_token', 'r') as fp:
		password = fp.read()

	channel = '#bunny_funeral'
	nickname = 'spelunkybot'
	server = irc.bot.ServerSpec('irc.twitch.tv', port=6667, password=password.strip())

	bot = BetBot(channel, nickname, server)
	bot.start()


if __name__ == "__main__":
	i_hate_snakes()



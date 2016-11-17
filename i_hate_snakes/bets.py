from i_hate_snakes import
import users
import odds

class bettingEngine():
    """
    Each instance handles the betting for the round.
    """
    def __init__(self):
        self.BetsArray = []
    def placeBet(self,twitchUser, bet, condition1, condition2=None, c):
        """
        The users bets X amount on condtion1 and possibly 2
        read in seed and current level from game if game NOT YET
        1 check to see if user has bet before.  Intialize user with 1000 credits to start
        2 check to see if user has bet in bank. put in max Bank amount if not.
        3 get odds for condition 1
        4 IF condition2 exists, get odds for condtion2 and multiply by condtion1
        place bet in bet database.   twitchUser, modifiedBet, odds, potWinning
        """
        # 1
        if (users.checkUser(twitchUser) == True): # make a user check that returns true if user exists
            userMoney = users.getUserBalance(twitchUser)
        else:
            users.createUser(twitchUser)
        # 2
        if userMoney < bet:
            c.privmsg(str(channelName),"/w "+ twitchUser+ "you bet "+ bet + " but you only have " + userMoney + " so thats the amount you bet you cheater")
            bet = userMoney
        # 3 and 4
        bettingOdds = odds.getOdds(condtion1, condtion2)

        potWinning = bettingOdds * bet
        c.privmsg(str(channelName),"/w "+ twitchUser+ "the odds you endded up betting on are "+ bettingOdds+ " You could win" + potWinning)
        userBet = [twitchUser, bet, bettingOdds, potWinning]
        self.BetsArray.append(userBet)
        return
    def

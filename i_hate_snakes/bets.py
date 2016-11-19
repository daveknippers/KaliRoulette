
import people

class bettingEngine():
    """
    Each instance handles the betting for the round.
    """
    def __init__(self, theOdds, connection):
        self.BetsArray = []
        self.odds = theOdds
        self.users = people.users()
        self.connection = connection
    def placeBet(self,twitchUser, bet, condition1, condition2, channelName):
        """
        The users bets X amount on condtion1 and possibly 2
        read in seed and current level from game if game NOT YET
        1 check to see if user has bet before.  Intialize user with 1000 credits to start
        2 check to see if user has bet in bank. put in max Bank amount if not.
        3 get odds for condition 1
        4 IF condition2 exists, get odds for condtion2 and multiply by condtion1
        place bet in bet database.   twitchUser, modifiedBet, odds, potWinning
        """
        c = self.connection
        # 1
        userMoney = self.users.getUserBalance(twitchUser)

        # 2
        if userMoney < bet:
            c.privmsg(str(channelName),"/w "+ twitchUser+ " you bet "+ str(bet) + " but you only have " + str(userMoney) + " so thats the amount you bet you cheater")
            bet = userMoney
        remaining = self.users.bettingUserGold(twitchUser,-bet)
        # 3 and 4
        bettingOdds = self.odds.getOdds(condition1, condition2)
        print(bettingOdds)
        potWinning = int(bettingOdds) * int(bet)
        c.privmsg(str(channelName),"/w "+ twitchUser+ " odds are "+ str(bettingOdds)+ " winnings =" + str(potWinning) + " balance = "+ str(remaining))
        userBet = [twitchUser, bet, bettingOdds, potWinning, condition1, condition2]
        print (userBet)
        self.BetsArray.append(userBet)
        return

    def tallyWinnings(self, condtion1, condition2, gold=None, ropes=None, bombs=None):
        for i in self.BetsArray:
            if(i[5] !=None):
                if((i[4] == condtion1 and i[5] == condtion2) or (i[4] == condtion2 and i[5] == condtion1)):
                    user = i[0]
                    potWinning = i[3]
                    self.users.bettingUserGold(user, potWinning)
            elif(i[4] == condtion1 or i[4] == condtion2):
                user = i[0]
                potWinning = i[3]
                self.users.bettingUserGold(user, potWinning)
            else:
                user = i[0]
                self.users.postOutcomeUserGold(user)
        self.BetsArray = []

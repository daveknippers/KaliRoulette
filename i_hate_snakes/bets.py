import time
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
            c.privmsg(str(channelName),"/w "+ twitchUser+ " you bet "+ str(bet) + " but you only have " + str(userMoney) + " Golden Daves so thats the amount you bet you cheater")
            bet = userMoney
        remaining = self.users.bettingUserGold(twitchUser,-bet)
        # 3 and 4
        bettingOdds = self.odds.getOdds(condition1, condition2)
        if bettingOdds == -1:
            remaining = self.users.bettingUserGold(twitchUser,bet)
            c.privmsg(str(channelName),"/w "+ twitchUser+ " you bet on something that doesnt exist.  Ive refunded your money but make sure you spell it right next time or maybe i wont be so nice")
            return
        print(bettingOdds)
        potWinning = int(bettingOdds) * int(bet)
        betTime = time.time()
        c.privmsg(str(channelName),"/w "+ twitchUser+ " odds are "+ str(bettingOdds)+ " winnings =" + str(potWinning) + " Golden Daves balance = "+ str(remaining) + " Golden Daves")
        userBet = [twitchUser, bet, bettingOdds, potWinning, condition1, condition2, betTime]
        print (userBet)
        self.BetsArray.append(userBet)
        return
    def stopBet(self, userName):
        succsess = False
        currentTime = time.time()
        i=0
        for item in self.BetsArray:
            if item[0] == userName:
                difference = currentTime - item[6]
                if difference <= 10:
                    self.users.bettingUserGold(userName, item[1])
                    self.BetsArray.pop(i)
                    i = i-1
                    succsess = True
            i+=1
        return succsess

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

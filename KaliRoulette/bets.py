import time
import people
import math

class bettingEngine():
	"""
	Each instance handles the betting for the round.
	"""
	def __init__(self, theOdds):
		self.BetsArray = []
		self.odds = theOdds
		self.users = people.users()
	def placeBet(self,twitchUser, bet, condition1, condition2):
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
		userMoney = self.users.getUserBalance(twitchUser)
		lowMoneyFlag = False
		# 2
		if bet < 0:
			bet = 0
		if userMoney < bet:
			bet = userMoney
			lowMoneyFlag = True
		remaining = self.users.bettingUserGold(twitchUser,-bet)
		# 3 and 4
		bettingOdds = self.odds.getOdds(condition1, condition2)
		if bettingOdds == -1:
			remaining = self.users.bettingUserGold(twitchUser,bet)
			return -1
		print(bettingOdds)
		potWinning = int(bettingOdds) * int(bet)
		betTime = time.time()
		userBet = [twitchUser, bet, bettingOdds, potWinning, condition1, condition2, betTime]
		self.BetsArray.append(userBet)
		if lowMoneyFlag:
			return -2
		return userBet
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

	def tallyWinnings(self, condition1, condition2, special_level, gold=None, ropes=None, bombs=None):
		for i in self.BetsArray:
			first = str(i[4])
			second = str(i[5])
			if special_level !=None:
				if(i[5] !=None):
					if ((first == str(special_level) and second == str(condition2)) or (first == str(condition1) and second == str(special_level)) or (first == str(special_level) and second == str(condition1)) or (first == str(condition2) and second == str(special_level))):
						user = i[0]
						potWinning = i[3]
						print(user,'bigmoney',potWinning)
						self.users.bettingUserGold(user, potWinning)
					elif((first == str(condition1) and second == str(condition2)) or (first == str(condition2) and second == str(condition1))):
						user = i[0]
						potWinning = i[3]
						print(user,'bigmoney',potWinning)
						self.users.bettingUserGold(user, potWinning)
				elif(first == str(condition1) or first == str(condition2) or first == str(special_level)):
					user = i[0]
					potWinning = i[3]
					print(user,potWinning)
					self.users.bettingUserGold(user, potWinning)
			else:
				if(i[5] !=None):
					if((first == str(condition1) and second == str(condition2)) or (first == str(condition2) and second == str(condition1))):
						user = i[0]
						potWinning = i[3]
						print(user,'bigmoney',potWinning)
						self.users.bettingUserGold(user, potWinning)
				elif(first == str(condition1) or first == str(condition2)):
					user = i[0]
					potWinning = i[3]
					print(user,potWinning)
					self.users.bettingUserGold(user, potWinning)
			self.users.postOutcomeUserGold(i[0])
		self.BetsArray = []

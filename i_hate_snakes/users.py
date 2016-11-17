import panadas as pd

class user():
    """
    has the information for the users and dishes it out.
    """
    def createUser(self, twitchUser):
        self.name = twitchUser
        self.bankBalance = 1000
        dataSet = [self.Name, self.bankBalance]
        self.df = pd.DataFrame(data = dataSet, columns=['Name', 'Bankbalance'])
    def getUserBalance(self, name):
        search = self.df.query('Name == "'name'"')
        bankBalance = search[1]
        return bankBalance

    def addUserBalance(self, name, numericalChange):
        """
        does minus and adding.  Catches if the user has less than 50 credits
        """
        newBalance = self.bankBalance + numericalChange
        if newBalance < 50:
            newBalance = 50
        self.bankBalance = newBalance
        return self.bankBalance

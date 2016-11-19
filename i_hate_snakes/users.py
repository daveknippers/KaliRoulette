import panadas as pd
import numpy as np
class users():
    """
    has the information for the users and dishes it out.
    """
    def __init__():
        if os.exists("users.csv"):
            self.userData = pd.read_csv("users.csv")
        else:

    def createUser(self, twitchUser):
        self.name = twitchUser
        self.bankBalance = 1000
        dataSet = [self.Name, self.bankBalance]
        self.df = pd.DataFrame(data = dataSet, columns=['Name', 'Bankbalance'])
    def getUserBalance(self, name):
        search = self.userData[userData['Name']== name]
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
        self.userData.loc[userData['Name'] == name, 'bankBalance'] = newBalance
        return self.bankBalance

import sqlite3
import os
class users():
    """
    has the information for the users and dishes it out.
    """
    def __init__(self):
        if os.path.exists('SpelunkyBet.db'):
            self.conn = sqlite3.connect('SpelunkyBet.db')
        else:
            self.conn = sqlite3.connect('SpelunkyBet.db')
            c = self.conn.cursor()
            c.execute('''CREATE TABLE users(name text, bankBalance real )''')
            self.conn.commit()

    def createUser(self, twitchUser):
        c = self.conn.cursor()
        name = twitchUser
        bankBalance = 1000.00
        dataSet = (name, bankBalance)
        c.execute("INSERT INTO users VALUES (?,?)",dataSet)
        self.conn.commit()
        return 1000

    def getUserBalance(self, name):
        c = self.conn.cursor()
        userName = [str(name)]
        c.execute('SELECT * FROM users WHERE name=?', userName)
        search = c.fetchone()
        if search == None:
            bankBalance = self.createUser(name)
        else:
            bankBalance = search[1]
        return int(bankBalance)

    def bettingUserGold(self, name, numericalChange):
        """
        does minus and adding. call during betting stage or a win
        """
        c = self.conn.cursor()
        userName = [str(name)]
        c.execute('SELECT * FROM users WHERE name=?', userName)
        search = c.fetchone()
        bankBalance = search[1]
        newBalance = bankBalance + numericalChange
        bankBalance = newBalance
        dataSet = [bankBalance, str(name)]
        c.execute("UPDATE users SET bankBalance=? WHERE name=?",dataSet)
        self.conn.commit()
        return int(bankBalance)

    def postOutcomeUserGold(self, name):
        """
        Has built catch for 50 or less.  CALL ONLY ON A BET OUTCOME
        """
        c = self.conn.cursor()
        userName = [str(name)]
        c.execute('SELECT * FROM users WHERE name=?', userName)
        search = c.fetchone()
        bankBalance = search[1]
        newBalance = bankBalance
        if newBalance < 50.0:
            newBalance = 50.0
            bankBalance = newBalance
            dataSet = [bankBalance, str(name)]
            c.execute("UPDATE users SET bankBalance=? WHERE name=?",dataSet)
            self.conn.commit()
        return int(bankBalance)

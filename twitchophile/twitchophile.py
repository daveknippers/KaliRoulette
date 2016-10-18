import sqlite3, datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Query:

    @staticmethod
    def followed_channel():
            return """
SELECT * FROM datacollector_followedchannel"""

    @staticmethod
    def follower():
            return """
SELECT * FROM datacollector_follower"""

    @staticmethod
    def streams():
            return """
SELECT * FROM datacollector_streams"""

def twitchophile():
    sql_engine = sqlite3.connect('twitchophile.db')
    followed_df = pd.read_sql_query(Query.followed_channel(),sql_engine)
    follower_df = pd.read_sql_query(Query.follower(),sql_engine)
    streams_df = pd.read_sql_query(Query.streams(),sql_engine,parse_dates=['time'])
    streams_df = streams_df.rename(columns={'veiwers':'viewers'})

    print('\nfollowed_df:')
    print(followed_df.head())

    print('\nfollower_df:')
    print(follower_df.head())

    print('\nstreams_df:')
    print(streams_df.head())

    streams_df['time'] = streams_df['time'].apply(lambda x:  datetime.datetime(*x.timetuple()[:5]))
    streams_df['game_viewers_by_time'] = streams_df.groupby(['time','game'])['viewers'].transform(sum)

    game_viewers_by_minute = streams_df[['time','game','game_viewers_by_time']].drop_duplicates()
    print('\ngame viewers by minute:')
    print(game_viewers_by_minute.head())

    dota_viewers_by_minute = game_viewers_by_minute[game_viewers_by_minute['game'] == 'Dota 2']

    figure = plt.figure()
    ax = figure.add_subplot(111,autoscale_on=True)
    ax.set_xlabel('time')
    ax.set_ylabel('viewers')

    y = dota_viewers_by_minute['game_viewers_by_time'].values
    x = range(len(y)) # this seems legit


    ax.plot(x,y)

    plt.savefig('awful_graph.png')
    plt.close()





    # all the .head() does is limit results to the top 5. head(30) would give top 30 resuts, etc.

if __name__ == "__main__":
	twitchophile()




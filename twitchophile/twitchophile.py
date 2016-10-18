import sqlite3
import numpy as np
import pandas as pd


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
	streams_df = pd.read_sql_query(Query.streams(),sql_engine)

	print(followed_df.head())
	print(follower_df.head())
	print(streams_df.head())

if __name__ == "__main__":
	twitchophile()


import pandas as pd
import sqlite3

ALL_ATTRIBUTES = [	'start_time',
			'seq',
			'level',
			'is_dead',
			'killed_by',
			'health',
			'bombs',
			'ropes',
			'gold_count',
			'favour',
			'angry_shopkeeper_1',
			'angry_shopkeeper_2',
			'lvl_dark',
			'lvl_worm',
			'lvl_black_market',
			'lvl_hmansion',
			'lvl_yeti',
			'lvl_cog',
			'lvl_mothership',
			'has_compass',
			'has_parachute',
			'has_jetpack',
			'has_climbing_gloves',
			'has_pitchers_mitt',
			'has_spring_shoes',
			'has_spike_shoes',
			'has_spectacles',
			'has_kapala',
			'has_hedjet',
			'has_udjat_eye',
			'has_book_of_dead',
			'has_ankh',
			'has_paste',
			'has_cape',
			'has_vlads_cape',
			'has_crysknife',
			'has_vlads_amulet',
			'game_timer',
			'player']

def merge_old_data():
	
	f_1 = 'stats_1.db'
	f_2 = 'stats_2.db'
	f_3 = 'death_collection_2016_12_04.db'
	f_4 = 'death_collection_2016_12_10.db'
	
	query = 'SELECT * FROM RUN_STATES'
	
	sql_engine_1 = sqlite3.connect(f_1)
	sql_engine_2 = sqlite3.connect(f_2)
	sql_engine_3 = sqlite3.connect(f_3)
	sql_engine_4 = sqlite3.connect(f_4)
	
	sql_engine_5 = sqlite3.connect('merged_death_collection.db')
	
	stats_1 = pd.read_sql(query,sql_engine_1).sort_values(['start_time','is_dead','level','angry_shopkeeper_1','lvl_mothership'])
	stats_2 = pd.read_sql(query,sql_engine_2).sort_values(['start_time','is_dead','level','angry_shopkeeper_1','lvl_mothership'])
	stats_3 = pd.read_sql(query,sql_engine_3).sort_values(['start_time','seq'])
	stats_4 = pd.read_sql(query,sql_engine_4).sort_values(['start_time','seq'])

	stats_1 = stats_1.reset_index(drop=True).reset_index()
	stats_2 = stats_2.reset_index(drop=True).reset_index()
	
	stats_1 = stats_1.rename(columns={'index':'seq'})
	stats_2 = stats_2.rename(columns={'index':'seq'})
	
	stats_1['seq'] = stats_1.groupby('start_time')['seq'].transform(lambda x: x-x.min())
	stats_2['seq'] = stats_2.groupby('start_time')['seq'].transform(lambda x: x-x.min())
	
	stats_1['game_timer'] = None
	stats_2['game_timer'] = None
	
	#print(stats_1.head())
	#print(stats_2.head())
	#print(stats_3.head())

	combined_df = pd.concat([stats_1,stats_2,stats_3,stats_4])
	combined_df['player'] = 'bunny_funeral'
	combined_df = combined_df[ALL_ATTRIBUTES]
	
	
	#print(combined_df)

	combined_df.to_sql('run_states',sql_engine_5,if_exists='fail',index=False)


	sql_engine_1.close()
	sql_engine_2.close()
	sql_engine_3.close()
	sql_engine_4.close()
	sql_engine_5.close()

if __name__ == '__main__':
	merge_old_data()

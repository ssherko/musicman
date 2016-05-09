from api_handler import get_genres_for_artist
from wrappers import find_similar_artists, find_artist_songs, get_track_profile, get_song_profile, find_song_data
from data_handler import STORE_IDS, CACHE_IDS,  fetch_seed, fetch_store, fetch_cache, add_to_store, is_in_store, add_to_cache
import logging


def matching_genres(relevant_genres, artist_genres):
	for genre in relevant_genres:
		if genre in artist_genres:
			return True
	return False
	
def init_explore(seed_list):
	if len(fetch_store(STORE_IDS["artists"])) > 0 and len(fetch_store(STORE_IDS["songs"])) > 0:
		return

	for artist, title in seed_list:
		similar_artists = find_similar_artists(artist, max_results = 2)
		
		#Refactor this clusterfuck ...
		for artist in similar_artists:
			artists = fetch_store(STORE_IDS["artists"])
			if is_in_store(artists, artist):
				continue
				
			artist_genres = get_genres_for_artist(artist)

			for genre in artist_genres:
				to_cache = (genre, 1)
				add_to_cache(CACHE_IDS["genres"], to_cache)

		add_to_store(STORE_IDS["artists"], similar_artists)

	for artist, title in seed_list:
		song_data = find_song_data(artist, title)
		add_to_store(STORE_IDS["songs"], song_data)
		
	logging.info("MusicMan cache/store setup was successful")
	return

def explore():

	genres = fetch_cache(CACHE_IDS["genres"])
	genres_dictitems = genres.items()
	max_genre_occurrence = max(genres_dictitems, key = lambda genre: genre[1])[1]
	cutoff_f = lambda genre: genre[1] >= (max_genre_occurrence / 3)
	relevant_genres = map(lambda entry: entry[0],filter(cutoff_f, genres_dictitems))
	
	artists = fetch_store(STORE_IDS["artists"])
	
	# Find similar artists
	# For each artist, get data for all songs
	for artist_id, artist in artists.iteritems():
		similar_artists = find_similar_artists(artist["name"], max_results = 2)
		
		similar_artists_to_add = []
		for sim_artist in similar_artists:
			artist_genres = get_genres_for_artist(artist)
			if matching_genres(relevant_genres, artist_genres):
				similar_artists_to_add.append(sim_artist)
				for genre in artist_genres:
					to_cache = (genre, 1)
					add_to_cache(CACHE_IDS["genres"], to_cache)

				relevant_songs = truncate_songs(sim_artist["songs"])
				for song in relevant_songs:
					song_data = find_song_data(sim_artist["name"], song["title"])
					add_to_store(STORE_IDS["songs"], song_data)

		add_to_store(STORE_IDS["artists"], similar_artists_to_add)

def truncate_songs(songs, up_to = 2):
	return songs[:up_to]
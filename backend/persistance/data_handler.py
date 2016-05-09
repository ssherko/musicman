import json
import logging
from sys import exit
from os.path import join, dirname, isfile
from os import listdir

"""
	The module handles persistance of data used by the service. 
"""
BASE = dirname(__file__)

STORE_FOLDER = "store"

# The 'ARTIST_STORE' contains a json string
# representing an array of artist json strings
# Each artist json string should contain at least:
# 	{'songs':[{'id': ..., 'title': ...}, ...], 'name': ..., 'id': ..., ...}
ARTIST_STORE_FNAME = join(BASE, STORE_FOLDER, "artists.json")

# The 'SONGS_CACHE' contains a json string
# representing an array of song json string
# Each song json string should contain at least:
# 	{'title': ..., 'artist_name': ..., 'artist_id': ..., 'id': ..., ...}
SONGS_STORE_FNAME = join(BASE, STORE_FOLDER, "songs.json")

SUGGESTION_STORE_FNAME = join(BASE, STORE_FOLDER, "suggestions.json")

STORE_IDS = {
	"artists": 0,
	"songs": 1,
	"suggestions": 2,
}

######################################################################
#																	 #
#																	 #
#			    	ARTIST/SONG-STORE-RELATED STUFF				 	 #
#																	 #
#												 			    	 #
######################################################################

# Returns the contents of a cache, specified by <cache_id>
# in json format.
# @param cache_id Integer The ID of the required cache
# @return cache JSON string The contents of the cache.
def fetch_store(store_id):
	store = None
	try:
		if store_id == STORE_IDS["artists"]:
			store = json.loads(open(ARTIST_STORE_FNAME).read())

		if store_id == STORE_IDS["songs"]:
			store = json.loads(open(SONGS_STORE_FNAME).read())

		if store_id == STORE_IDS["suggestions"]:
			store = json.loads(open(SUGGESTION_STORE_FNAME).read())

	except Exception as e:
		logging.critical("Couldn't open cache file: " + str(e))
		exit()
	
	return store

# Adds (non-existing) elements to the appropriate cache
# @param cache_id Integer
# @param json_array [<json_string>, ...] An array of json elements to be added to the cache
def add_to_store(store_id,json_array):
	added = False

	store = fetch_store(store_id)
	for json_element in json_array:
		if not is_in_store(store, json_element): 
			store[json_element["id"]] = json_element
			added = True

	persist_store(store_id, store)
	return added

# Checks whether an element already exists in the specified cache
# @param cache JSON String [...]
# @param json_element JSON String
def is_in_store(store, json_element):
	return store.has_key(json_element["id"])


# Persists the JSON string representing a cache onto disk
# @param cache_id Integer 
# @param 
def persist_store(store_id, store_dict):
	store_file = None
	try:

		if store_id == STORE_IDS["artists"]:
			store_file = open(ARTIST_STORE_FNAME, "w")
		if store_id == STORE_IDS["songs"]:
			store_file = open(SONGS_STORE_FNAME, "w")
		if store_id == STORE_IDS["suggestions"]:
			store_file = open(SUGGESTION_STORE_FNAME, "w")
			
	except Exception as e:
		logging.critical("Couldn't open store file: " + str(e))
		exit()

	store_file.write(json.dumps(store_dict, indent=4, separators=(", ",": ")))
	store_file.close()
	return

# Return a dictionary of current cache sizes
# @return stats Python dictionary
def get_store_stats():
	nr_artists = len(fetch_store(STORE_IDS["artists"]))
	nr_songs = len(fetch_store(STORE_IDS["songs"]))
	stats = {"nr_artists": nr_artists, "nr_songs":nr_songs}
	return stats

######################################################################
#																	 #
#																	 #
#					CACHE/CACHING-RELATED STUFF						 #
#																	 #
#												 			    	 #
######################################################################

import pickle

CACHE_FOLDER = "cache"

#The 'SEED_FILE' contains lines of the format <artist_name> - <song_title>
# that act as a starting point for the discovery service
SEED_FILE = join(BASE, CACHE_FOLDER, "seed")

# The 'QUERIED_FILE' is a cache for persisting API calls that have already been
# issued and their response. 
QUERIED_FILE = join(BASE, CACHE_FOLDER, "queried.dct")


# The 'GENRES_FILE' contains ... well, try and guess.
GENRES_FILE = join(BASE, CACHE_FOLDER, "genres.dct")

CACHE_IDS = {
	"queried": 0,
	"genres": 1,
}

# Returns a list of tuples <artist:string, song:string>
# to act as a starting point for the service
# @return seed_list List[(<string>,<string>), ...] The list of songs to start from.
def fetch_seed():
	seed_list = []
	seed_file = None
	try:
		seed_file = open(SEED_FILE, "r")
	except Exception as e:
		logging.critical("Couldn't open seed file: " + str(e))
		exit()

	for line in seed_file:
		if line.startswith("#"): continue
		line_elements = line.split(" - ")
		artist_name = line_elements[0].strip("\n")
		song_title = line_elements[1].strip("\n")
		seed_list.append((artist_name,song_title))

	seed_file.close()
	return seed_list
	
def fetch_cache(cache_id):
	cache_file = None
	cache = None

	if cache_id == CACHE_IDS["queried"]:
		cache_file = QUERIED_FILE

	if cache_id == CACHE_IDS["genres"]:
		cache_file = GENRES_FILE

	try:
		cache = open(cache_file, "r")
	except Exception as e:
		logging.critical("Couldn't open cache file: " + str(e) + " (id: " + str(cache_id) + ")")
		exit()

	cache_contents = None
	try: 
		cache_contents = pickle.load(cache)
	except EOFError: # file empty
		cache_contents = {}

	return cache_contents

# Adds a new key_value pair into 
def add_to_cache(cache_id, element):
	cache = fetch_cache(cache_id)
	added = False

	if cache_id == CACHE_IDS["queried"]:
		if not is_in_cache(cache,element[0]):
			key = element[0]
			value = element[1]
			cache[key] = value
			added = True

	if cache_id == CACHE_IDS["genres"]:
		if not is_in_cache(cache,element[0]):
			key = element[0]
			cache[key] = 1
			added = True
		else:
			key = element[0]
			cache[key] += 1
			added = True

	persist_cache(cache_id,cache)
	return added

def get_from_cache(cache_id, key):
	cache = fetch_cache(cache_id)
	result = []
	if cache.has_key(key):
		result = cache[key]

	return result

def is_in_cache(cache, key):
	return cache.has_key(key)

def persist_cache(cache_id, cache):
	cache_file = None

	try:
		if cache_id == CACHE_IDS["queried"]:
			cache_file = open(QUERIED_FILE, "w")
		if cache_id == CACHE_IDS["genres"]:
			cache_file = open(GENRES_FILE, "w")

	except Exception as e:
		logging.critical("Couldn't open cache file: " + str(e))
		exit()

	pickle.dump(cache, cache_file)

	cache_file.close()
	return

# NOTES:
# Due to the fact a song signature can be ~10MB, storing all signatures in a single cache file
# would be a major bottleneck due to I/O load in reading and writing a (possibly) multi-GB file. 
# So, each signature is stored in a file of its own. Furthermore, in case the process is killed 
# while the file is being written, everything is lost. NOT. COOL. 

SIGNATURES_FOLDER = join(BASE, CACHE_FOLDER, "signatures")

def fetch_signature(song_id):
	signature_path = join(SIGNATURES_FOLDER, song_id)

	if not is_signature_cached(song_id):
		return None

	signature = None
	try:
		signature = pickle.load(open(signature_path,"r"))
	except Exception as e:
		logging.critical("Couldn't load signature for {0}: {1}".format(song_id, str(e)))
	
	return signature

def persist_signature(song_id, signature, update = False):
	if is_signature_cached(song_id) and not update:
		return False

	try:
		signature_file = open(join(SIGNATURES_FOLDER, song_id), "w")
		pickle.dump(signature, signature_file)
	except Exception as e:
		logging.critical("Couldn't persist signature for {0}: {1}".format(song_id, str(e)))
		return False

	return True


def fetch_all_signature_ids():
	return os.listdir(SIGNATURES_FOLDER)

def is_signature_cached(song_id):
	signature_path = join(SIGNATURES_FOLDER, song_id)
	return isfile(signature_path)

######################################################################
#																	 #
#																	 #
#						MODEL-RELATED STUFF							 #
#																	 #
#												 			    	 #
######################################################################

MODEL_FOLDER = "model"

# Stores/caches pre-computed signatures for songs
MODEL_FILE = join(BASE, MODEL_FOLDER, "model_sig.dct")

# A json-string representation of data for songs from the 'seed'
DATASET_FILE = join(BASE, MODEL_FOLDER, "dataset.json")

# Contains 30+ second audio clips for songs
AUDIOCLIPS_FOLDER = join(BASE, MODEL_FOLDER, "audio") 

# Returns a json-string 
def fetch_dataset():
	dataset = []
	try:
		dataset = json.loads(open(DATASET_FILE).read())
	except Exception as e:
		logging.critical("Couldn't open dataset file: " + str(e))
		exit()

	return dataset

def persist_dataset(dataset_json):
	dataset_file = None
	try:
		dataset_file = open(DATASET_FILE, "w")
		dataset_file.write(json.dumps(dataset_json, indent=4, separators=(", ",": ")))
		dataset_file.close()
	except Exception as e:
		logging.critical("Couldn't open dataset file: " + str(e))
		exit()

	return

def fetch_model():
	model = {}
	model_file = None
	try:
		model_file = open(MODEL_FILE, "r")
	except Exception as e:
		logging.critical("Couldn't open model file: " + str(e))
		exit()

	try:
		model = pickle.load(model_file)
		model_file.close()
	except EOFError as e:
		logging.info("Empty model ... proceeding")

	return model

def persist_model(model):
	model_file = None
	try:
		model_file = open(MODEL_FILE, "w")
	except Exception as e:
		logging.critical("Couldn't open model file: " + str(e))
		exit()

	pickle.dump(model, model_file)

def is_in_model(model, song_id):
	return model.has_key(song_id)

def add_to_model(new_signature):
	current_model = fetch_model()
	song_id = new_signature[0]
	signature = new_signature[1]

	if is_in_model(model, song_id):
		return False

	model[song_id] = signature
	persist_model(model)
	return True



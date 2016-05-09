from frontend import cli
from backend.classifier.model import compute_spectral_signature, calculate_emd
from backend.client.main import initialize_service
from backend.mp3client.wrappers import get_song_audiolinks, download_mp3clip
from data_handler import AUDIOCLIPS_FOLDER, STORE_IDS, CACHE_IDS, \
						 fetch_store, persist_store, \
						 fetch_cache, \
						 fetch_dataset, persist_dataset, \
						 is_signature_cached, persist_signature, fetch_signature
from os.path import join, isfile

######################################################################
#																	 #
#																	 #
#   		    	DATASET/STORE RELATED STUFF				 	     #
#																	 #
#												 			    	 #
######################################################################

def start_service(verbose = False):

	initialize_service()
	if verbose: cli.print_message("Synchronizing song data ...")
	sync_song_data()
	dataset = fetch_dataset()
	if len(dataset) == 0:
		if verbose: cli.print_message("Building initial dataset ...")

def annotate_audio_data(song_json, update_links = False):
	if song_json.has_key("explored") and song_json["explored"]:
		return song_json

	title = song_json["title"]
	artist = song_json["artist_name"]


	links = []
	if update_links:
		links = get_song_audiolinks(artist, title)

	song_json["audio_links"] = links
	song_json["downloaded"] = False
	song_json["explored"] = False
	if not song_json.has_key("is_model"):
		song_json["is_model"] = False
	
	return song_json

def analyze_song(song_entry, reannotate = False, redownload = False, compute_signature = False, verbose = True):
	song_id, song_json = song_entry
	
	if song_json["signature_computed"]:
		return song_entry

	if verbose: print "Processing: '{1} - {2}' ({0}) ...".format(song_id ,song_json["title"].encode("utf8"), song_json["artist_name"].encode("utf8"))
	if reannotate:
		song_json = annotate_audio_data(song_json, update_links = False)

	if redownload:
		song_json = annotate_audio_data(song_json, update_links = True)
		audio_links = song_json["audio_links"]
		attempts = 0
		
		while not song_json["downloaded"] and attempts < len(audio_links):
			mp3link = audio_links[attempts]
			if song_json.has_key("explored") and song_json["explored"] == False:
				song_json["downloaded"] = download_mp3clip(mp3link, song_id, AUDIOCLIPS_FOLDER)
				attempts += 1 

		song_json["explored"] = True
		if verbose: 
			if song_json["downloaded"]:
				print "Downloaded '{1} - {2}' ({0}) ...".format(song_id ,song_json["title"].encode("utf8"), song_json["artist_name"].encode("utf8"))
			else:
				print "Failed to download '{1} - {2}' ({0})".format(song_id ,song_json["title"].encode("utf8"), song_json["artist_name"].encode("utf8"))
	

	if song_json["downloaded"] and compute_signature:
		if verbose: print "Computing its signature ... (might take some time)"
		song_json["signature_computed"] =  (not compute_spectral_signature(song_id) == None)
		
		if verbose: 
			if song_json["signature_computed"]: 
				print "Done." 
			else: 
				print "Failed."


	updated_song_entry = (song_id, song_json)
	return updated_song_entry

def sync_song_data():
	song_store = fetch_store(STORE_IDS["songs"])

	for song_id, song_data in song_store.iteritems():
		mp3filename = join(AUDIOCLIPS_FOLDER, song_id + ".mp3")
		if isfile(mp3filename):
			song_data["downloaded"] = True
		else:
			song_data["downloaded"] = False

		if is_signature_cached(song_id):
			song_data["signature_computed"] = True
		else:
			song_data["signature_computed"] = False

	persist_store(STORE_IDS["songs"], song_store)

def process_songs(song_store, red = False, rea = False, cs = False, ve = True):
	for song_entry in song_store.iteritems():
		updated_song_entry = analyze_song(song_entry, redownload = red, reannotate = rea, compute_signature = cs, verbose = ve)
		song_id, song_json = updated_song_entry
		song_store[song_id] = song_json
		persist_store(STORE_IDS["songs"], song_store)

def calculate_distances(song_store, use_model = True):
	distances = []

	# Calculate all possible distance pairs
	if not use_model:
		for song_id1, song_json1 in song_store.iteritems():
			if not is_signature_cached(song_id1): continue

			model_distances_for_song = []
			for song_id2, song_json2 in song_store.iteritems():
				if song_id1 == song_id2: continue
				if not is_signature_cached(song_id2): continue

				sig1 = fetch_signature(song_id1)
				sig2 = fetch_signature(song_id2)

				distance = calculate_emd(sig1,sig2)
				dist_entry = (
								"{0} - {1} ==== {2} - {3}"\
							 	.format(
							 		song_json1["title"].encode("utf8"),
							 		song_json1["artist_name"].encode("utf8"),
							 		song_json2["title"].encode("utf8"),
							 		song_json2["artist_name"].encode("utf8")
								),
								distance
							 )
				model_distances_for_song.append(dist_entry)

			
			distances += sorted(model_distances_for_song, key = lambda e: e[1])
	

	# Only calculate distances from songs in the model
	else:
		model_signatures = [ 
								(song_id, song_json) 
								for song_id, song_json in song_store.iteritems() if song_json["is_model"]
						   ]

		non_model_signatures = [
									(song_id, song_json) 
									for song_id, song_json in song_store.iteritems() if not song_json["is_model"]
							   ]

		for song_entry1 in non_model_signatures:
			song_id1 = song_entry1[0]
			song_json1 = song_entry1[1]
			if not is_signature_cached(song_id1): continue
			
			model_distances_for_song = []
			for entry in model_signatures:
				song_id2 = entry[0]
				song_json2 = entry[1]
				
				if not is_signature_cached(song_id2): continue

				sig1 = fetch_signature(song_id1)
				sig2 = fetch_signature(song_id2)

				distance = calculate_emd(sig1,sig2)
				dist_entry = (
								"{0} - {1} ==== {2} - {3}"\
							 	.format(
							 		song_json1["title"].encode("utf8"),
							 		song_json1["artist_name"].encode("utf8"),
							 		song_json2["title"].encode("utf8"),
							 		song_json2["artist_name"].encode("utf8")
								),
								distance
							 )
				model_distances_for_song.append(dist_entry)

			distances += sorted(model_distances_for_song, key = lambda e: e[1])

	return distances
			

def process_distances(distances):
	max_distance = max(distances, key= lambda entry: entry[2])
	min_distance = min(distances, key= lambda entry: entry[2])

def compare_audiofile_to_model(audio_path):
	pass

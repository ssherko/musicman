from api_handler import generate_api_call, submit_api_call, parse_response, append_additional_param,\
					    throttle_requests, \
				 		SIMILAR_ARTISTS, SONG_SEARCH, TRACK_PROFILE, SONG_PROFILE
import logging

"""
	The module provides simple API-call Python wrappers for EchoNest
"""
# Find artists similar to <artist>.
# If <seed> is not [], find artists most similar to the <seed> set.
# @param artist String The name/id of the artist
# @param seed List<String> Other artists to take into account for finding similar artists.
# @param max_results Integer Maximum number of results
# @return response JSON String [...]
def find_similar_artists(artist, seed = [], max_results = 5):
	api_call_url = generate_api_call(SIMILAR_ARTISTS, name=artist, results=max_results, bucket="songs")
	for name in seed:
		api_call_url = append_additional_param(api_call_url, {"name":name})

	api_call_url = append_additional_param(api_call_url, {"bucket":"genre"})
	json_response, response_headers  = submit_api_call(api_call_url)
	return parse_response(SIMILAR_ARTISTS, json_response)

# Find a maximum of <max_results> songs from <artist>
# @param artist String
# @param max_results Integer
# @return response JSON String [...]
def find_artist_songs(artist, max_results = 5, buckets=False):
	api_call_url = generate_api_call(SONG_SEARCH, artist=artist, results=max_results)
	if buckets:
		api_call_url = generate_api_call(SONG_SEARCH, artist=artist, results=max_results, bucket="id:spotify")
		api_call_url = append_additional_param(api_call_url, {"bucket":"audio_summary"})
		api_call_url = append_additional_param(api_call_url, {"bucket":"genre"})
	
	json_response, response_headers  = submit_api_call(api_call_url)
	return parse_response(SONG_SEARCH, json_response)

# Returns the song profile together with the audio summary of the corresponding track
# (in the Rosetta id-space). 
# @param song_id String The EchoNest ID of the song
# @return response JSON String [...]
def get_song_profile(song_id):
	api_call_url = generate_api_call(SONG_PROFILE, id=song_id, bucket="id:spotify")
	api_call_url = append_additional_param(api_call_url, {"bucket":"audio_summary"})
	api_call_url = append_additional_param(api_call_url, {"bucket":"song_type"})

	json_response, response_headers  = submit_api_call(api_call_url)
	return parse_response(SONG_PROFILE, json_response)

# Returns data (audio summary, corresponding track id etc.) of a particular song
# @param artist String
# @param title String
# @return response JSON String [...]
def find_song_data(artist, title):
	api_call_url = generate_api_call(SONG_SEARCH, artist=artist, title=title, bucket="id:spotify")
	api_call_url = append_additional_param(api_call_url, {"bucket":"audio_summary"})
	
	json_response, response_headers  = submit_api_call(api_call_url)
	return parse_response(SONG_SEARCH, json_response)
	

# Get track data for the track with the ID <track_id>
# @param track_id String
# @return response JSON String [...]
def get_track_profile(track_id):
	api_call_url = generate_api_call(TRACK_PROFILE, id=track_id, bucket="audio_summary")
	json_response, response_headers = submit_api_call(api_call_url)
	return parse_response(TRACK_PROFILE, json_response)
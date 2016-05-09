import skull_api_handler
import lio_api_handler
import requests
from os.path import join, isfile
import logging

def get_song_audiolinks(artist, song_title):
	mp3_links = []
	mp3_links += lio_api_handler.parse_response(lio_api_handler.submit_mp3_query(artist + " " + song_title))
	mp3_links += skull_api_handler.parse_response(skull_api_handler.submit_mp3_query(artist + " " + song_title))

	return mp3_links

def download_mp3clip(mp3link, song_id, store):
	target = join(store, song_id + ".mp3")
	check_wav = join(store, song_id + ".wav") 
	check_mp3 = target

	if isfile(check_mp3) or isfile(check_wav):
		return True

	response = None
	audio_clip_f = None

	try:
		response = requests.get(mp3link, stream = True)
		if not "audio" in response.headers["content-type"]:
			return False

		audio_clip_f = open(target, "wb")
		
		for chunk in response.iter_content(100):
			audio_clip_f.write(chunk)
		audio_clip_f.close()

	except Exception as e:
		logging.warn("Couldn't create audio clip for song {0}: {1}".format(song_id, str(e)))
		return False

	return True
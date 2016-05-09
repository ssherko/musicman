from requests import get, status_codes
import logging
from bs4 import BeautifulSoup

MP3SKULL_BASE = "https://mp3skull.is/"
MP3SKULL_SESSION_TOKEN = None
MP3SKULL_SEARCH = "search_db.php"

def get_session_token():
	if MP3SKULL_SESSION_TOKEN == None:
		response = None
		
		try:
			response = get(MP3SKULL_BASE)
		except Exception as e:
			logging.critical("Couldn't reach MP3SKULL: " + str(e))
			return

		if not response.status_code == status_codes.codes.OK:
			logging.critical("Couldn't set MP3SKULL session token: HTTP Error Code {0}".format(response.status_code))
			return

		return BeautifulSoup(response.text, "html.parser").find("input", type="hidden").get("value")

	return MP3SKULL_SESSION_TOKEN

def submit_mp3_query(query_string):
	MP3SKULL_SESSION_TOKEN = get_session_token()

	params = {
		"fckh": MP3SKULL_SESSION_TOKEN,
		"q": query_string.encode("utf8"),
	}

	response = None
	try:
		response = get("{0}{1}".format(MP3SKULL_BASE, MP3SKULL_SEARCH), params=params)
	except Exception as e:
		logging.critical("Couldn't reach MP3SKULL: " + str(e))
		return

	return BeautifulSoup(response.text, "html.parser")

def parse_response(response):
	if response == None:
		return []
		
	relevant_elements = response.find_all("div", id="song_html")

	mp3_links = []

	for element in relevant_elements:
		link_element = element.find("div", {"class": "download_button"})
		if link_element:
			anchor = link_element.find("a")
			if anchor:
				mp3_links.append(anchor.get("href"))

	return mp3_links



from requests import get, status_codes
import logging
from bs4 import BeautifulSoup

LIO_BASE = "http://mp3lio.co/"

def submit_mp3_query(query_string):
	response = None

	try:
		response = get("{0}{1}".format(LIO_BASE, query_string.replace(" ", "-").encode("utf8")))
	except Exception as e:
		logging.critical("Couldn't reach 'mp3lio.co': " + str(e))
		return

	return BeautifulSoup(response.text, "html.parser")

def parse_response(response):
	if response == None:
		return []

	to_follow = []

	relevant = response.find_all("div", {"class": "meta"})
	for elem in relevant:
		anchor_elem = elem.find_all("a")
		if anchor_elem:
			to_follow += map(lambda x: x.get("href"), anchor_elem)

	top = to_follow[:3]
	mp3_links = []
	for link in top:
		if "watch" in link:
			response = None
			try:
				response = get(link)
			except Exception as e:
				continue

			if response == None:
				continue
			
			parsed = BeautifulSoup(response.text, "html.parser")
			available_downloads = parsed.find("div", {"class" : "container download"})
			if available_downloads:
				anchor_elem = available_downloads.find_all("a")
				if anchor_elem:
					mp3_links += map(lambda x: x.get("href"), anchor_elem)

	return filter(lambda x: 'get' in x ,mp3_links)


		







import json
from urllib import urlencode
import urllib2
import logging 
from datetime import datetime
from time import sleep
import logging
from os.path import join

from data_handler import CACHE_IDS, is_in_cache, fetch_cache, add_to_cache, get_from_cache, QUERIED_FILE

"""
	The module handles generation/submission of API calls 
	to the appropriate endpoints and parses the responses
"""

# Relative path to the json file containing API keys etc.
API_DATA_FILE = join("backend","client","api_data.json")

# Prefix for API endpoints
API_URL = "http://developer.echonest.com/api/v4/"

# API Endpoint identifiers
SIMILAR_ARTISTS = "similar_artists"
SONG_SEARCH = "song_search"
TRACK_PROFILE ="track_profile"
SONG_PROFILE = "song_profile"

# Actual API Endpoints
API_ENDPOINTS = {
	SIMILAR_ARTISTS: "artist/similar",
	SONG_SEARCH: "song/search",
	TRACK_PROFILE: "track/profile",
	SONG_PROFILE: "song/profile",
}

# API keys etc.
api_key = None

try:
	API_DATA = json.loads(open(API_DATA_FILE).read())
except Exception as e:
	logging.critical("Couldn't read API data file. {0}".format(str(e)))
	exit(0)

api_key = API_DATA["api_key"] if API_DATA.has_key("api_key") else None

# Due to the usage limitations, API requests should be throttled 
# See 'http://developer.echonest.com/docs/v4/index.html#rate-limits'
# It does so by 'sleeping' the appropriate amount of time.
# @param response_headers Tuple <Integer,Integer,Integer> The headers sent back by the previous API call:
#														  Limit, Remaining, Used, respectively.
# @return None 
def throttle_requests(response_headers):
	if response_headers:
		last_response_time = datetime.now()
		request_limit = response_headers[0]
		time_delta = 61 / float(request_limit) # give some leeway
		sleep(time_delta)

	else:
		sleep(3) # default

	return 

# Encodes unicode request parameters as utf-8 (conforming to EchoNest convetions)
# @param params Dictionary(<String:String>,...)
def encode_params(params):
	encoded_params = {}
	for key, value in params.iteritems():
		k,v = key, value
		if isinstance(key,unicode): #encode
			k = key.encode("utf8")
		if isinstance(value,unicode): 
			v = value.encode("utf8")
		encoded_params[k] = v

	return encoded_params

# Generates the API call url. Note that it doesn't submit the request
# @param endpoint String 
# @param params Dictionary of <key,value> pairs to be appended to the request
# @return api_call String The call url.
def generate_api_call(endpoint, **params):
	if api_key == None:
		logging.critical("No API KEY provided. Check api_data.json file under 'backend/client'")
		exit(1)

	api_call = "{0}{1}?api_key={2}&".format(API_URL, API_ENDPOINTS[endpoint], api_key)
	encoded_params = encode_params(params)
	api_call += urlencode(encoded_params)
	return api_call

# Appends aditional parameters to the API call url.
# Note that most of the time, 'generate_api_call' should be used
# This is used to go around the fact that dictionaries cannot contain as a key the same value multiple times.
# @param api_call_url String
# @param dictionary Dictionary A python dict with a *single* key-value pair
# @return api_call_url String
def append_additional_param(api_call_url, dictionary):
	encoded_dict = encode_params(dictionary)
	api_call_url += "&{0}".format(urlencode(encoded_dict))
	return api_call_url


# Submits a request to the given API call url
# @param api_call_url String
# @return json_response, response_headers Tuple <json string, Tuple <Integer,Integer,Integer>>
def submit_api_call(api_call_url, cached = True):
	cache = fetch_cache(CACHE_IDS["queried"])
	if cached and is_in_cache(cache ,api_call_url):
		return get_from_cache(CACHE_IDS["queried"], api_call_url), None

	response = None
	json_response = None

	try:
		response = urllib2.urlopen(api_call_url)
		json_response = json.load(response)
	except Exception as e:
		logging.error("API call submission failed: " + str(e))
		throttle_requests(None)
		return None, None
	
	requests_limit = response.info().getheader('X-RateLimit-Limit')
	requests_remaining = response.info().getheader("X-RateLimit-Remaining")
	requests_used = response.info().getheader("X-RateLimit-Used")
	response_headers = (requests_limit, requests_remaining, requests_used)
	
	to_cache = (api_call_url, json_response)
	add_to_cache(CACHE_IDS["queried"], to_cache)

	throttle_requests(response_headers)

	return json_response, response_headers

# Parses the response according to the API endpoint it originated from
# @param endpoint String Where the response originated from
# @param json_response JSON String The actual response
# @return json_response[...]+ JSON String The parsed response
def parse_response(endpoint,json_response):
	if json_response == None:
		return []
	response = json_response["response"]
	status = response["status"]
	code = status["code"]
	message = status["message"]
	version = status["version"]

	if (not code == 0):
		logging.warn("Request from {0} not successful: {1}".format(endpoint, message))
		return []

	if endpoint == SIMILAR_ARTISTS: 
		return response["artists"]

	if endpoint == SONG_SEARCH:
		return response["songs"]

	if endpoint == TRACK_PROFILE:
		return response["track"]

	if endpoint == SONG_PROFILE:
		return response["songs"]


###################################
#	   Some UTILITY functions     #
###################################

def pretty_print_json(json_string):
	print json.dumps(json_string, indent=4, separators=(", ",": "))

def get_genres_for_artist(artist_json):
	genres = map(lambda x: x["name"],artist_json["genres"])
	return genres
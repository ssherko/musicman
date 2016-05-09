##############################
#	Logging facility setup   #
##############################

# First things first
import logging
from os.path import join
logging.basicConfig(filename=join("backend","persistance", "musicman.log"), 
					format='%(asctime)s | %(levelname)s: %(message)s',
					level=logging.WARN)

##############################

from util import start_service, process_songs, calculate_distances
from frontend import cli
from data_handler import STORE_IDS, fetch_store
from backend.client.explorer import explore

VERBOSE = True
start_service(verbose = VERBOSE)

#explore()
songs = fetch_store(STORE_IDS["songs"])
process_songs(songs, rea = True, red = True, cs = True, ve = VERBOSE)

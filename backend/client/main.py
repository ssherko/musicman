from explorer import init_explore, explore
from data_handler import fetch_seed
import logging 
def initialize_service():
	seed = fetch_seed()
	
	if len(seed) == 0:
		logging.critical("Seed is empty")
		exit(0)

	init_explore(seed)
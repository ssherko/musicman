BACKEND=backend
FRONTE=frontend
ENTRY=musicman.py
INTERP=python2.7

CLASSI=$(BACKEND)/classifier
CLIENT=$(BACKEND)/client
MP3CLI=$(BACKEND)/mp3client
PERSIS=$(BACKEND)/persistance

STORE=$(PERSIS)/store
MODEL=$(PERSIS)/model
CACHE=$(PERSIS)/cache

# STORE-RELATED
ARTIST_STORE=$(STORE)/artists.json
SONG_STORE=$(STORE)/songs.json
SUGGESTIONS=$(STORE)/suggestions.json

# MODEL-RELATED
AUDIOFOLD=$(MODEL)/audio
DATASET=$(MODEL)/dataset.json

#CACHE-RELATED
GENRES=$(CACHE)/genres.dct
QUERIED=$(CACHE)/queried.dct
SIGNATURES=$(CACHE)/signatures
SEED=$(CACHE)/seed

LOG=$(PERSIS)/musicman.log


# set to 1 to delete EVERYTHING (persistent data, that is)
RESET_ALL?=0

.PHONY: run clean reset_data setup

run: clean
	@$(INTERP) $(ENTRY);

clean:
	@find . -name "*.pyc" -type f -delete;

reset_data: clean
	@echo -n "" > $(LOG);
	@echo -n "{}" > $(SONG_STORE);
	@echo -n "{}" > $(ARTIST_STORE);
	@echo -n "{}" > $(SUGGESTIONS);
	@echo -n "{}" > $(DATASET);
	@find . -name "*.mp3" -type f -delete;
	@cd $(SIGNATURES) && rm -f *;

ifeq ($(RESET_ALL),1)
	@echo "Resetting cache";
	@echo -n "" > $(GENRES);
	@echo -n "" > $(QUERIED);
	@echo "# <artist_name> - <song_title>, for example:" > $(SEED)
	@echo "# Nicolas Jaar - Colomb" >> $(SEED)
	@echo "# Make sure to leave an Empty space after the artist name and after the '-' (or before the song name)" >> $(SEED)
endif

setup: reset_data
	@mkdir $(SUGGESTIONS) # Yeah, I know.
	@touch $(CLIENT)/api_data.json;


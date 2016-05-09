# Musicman

0) $make setup
.
├── backend
│   ├── classifier
│   │   ├── __init__.py
│   │   └── model.py
│   ├── client
│   │   ├── api_data.json
│   │   ├── api_handler.py
│   │   ├── explorer.py
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── wrappers.py
│   ├── __init__.py
│   ├── mp3client
│   │   ├── __init__.py
│   │   ├── lio_api_handler.py
│   │   ├── skull_api_handler.py
│   │   └── wrappers.py
│   └── persistance
│       ├── cache
│       │   ├── genres.dct
│       │   ├── queried.dct
│       │   ├── seed
│       │   └── signatures
│       ├── data_handler.py
│       ├── model
│       │   ├── audio
│       │   └── dataset.json
│       ├── musicman.log
│       └── store
│           ├── artists.json
│           ├── songs.json
│           └── suggestions.json
├── frontend
│   ├── cli.py
│   └── __init__.py
├── Makefile
├── musicman.py
├── README.md
└── util.py

# anime-scraper
Scraper program for anime sites.

This program will interactively search for an anime and download the one you selected.

## Prerequisites
In order to use this tool, you need several tools installed on your system.
* Either clone this repository using git or just download and extract the source code manually.
* python version 11 is required.
* To manage python package requirements, we use poetry. Install it with ```pip install poetry```.
* Install all required packages with ```poetry install``` inside the main folder.
* For video conversion you need to install ffmpeg from https://ffmpeg.org/download.html.
* Now you can run the program with ```poetry run python src/scrape.py```

## CLI arguments
Pass ocmmand line arguments in the format '*argumentname*=*value*'. The following arguments are supported:
* `threads` or `n`: Set the maximum parallel downloads. Default is `20`.
* `url` or `base`: Set the top-level scraping site. Default is `https://gogoanime.dev`. If this is already an anime url, skip interactive selection and directly download it.
* `format` or `f`: Set the output format. Default is `mp4`.
* `simulate` or `s`: Only check, which episodes are downloaded and which are skipped.

Example:
```cmd
poetry run python src/scrape.py format=mp4 threads=50 url=https://gogoanime.dev simulate=true
```
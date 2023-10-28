# anime-scraper
Scraper program for anime sites.

This program will interactively search for an anime and download the one you selected.

## Prerequisites
In order to use this tool, you need several tools installed on your system.
* Either clone this repository using git or just download and extract the source code manually.
* Any python version is sufficient.
* To manage python package requirements, we use poetry. Install it with ```pip install poetry```.
* Install all required packages with ```poetry install``` inside the main folder.
* For video conversion you need to install ffmpeg from https://ffmpeg.org/download.html.
* Now you can run the program with ```poetry run python src/scrape.py```

## Top-level site
This program uses https://gogoanime.dev as its top-level scraping site.
If you want to change it, you have to set the ```BASE_URL``` variable at the top of the ```scrape.py``` file.
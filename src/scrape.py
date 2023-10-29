import aiohttp
from bs4 import BeautifulSoup
import m3u8
from ffmpeg.asyncio import FFmpeg
import asyncio
import re
import os
from typing import Generator
import sys

BASE_URL = "https://gogoanime.dev"
FULL_URL = None
FORMAT = "mp4"
DOWNLOAD_THREADS = 10
SIMULATE = False

def soupify(func):

    async def wrapper(url: str, session: aiohttp.ClientSession):
        async with session.get(url) as response:
            http = await response.text()
        soup = BeautifulSoup(http, features="html.parser")
        return func(soup)
    
    return wrapper

async def get_anime_info(session: aiohttp.ClientSession):
    if FULL_URL:
        name = input(f"Enter save name: ")
        return name, FULL_URL
    
    print(f"Searching on {BASE_URL}")
    animeinput = input("Search for an anime: ")
    animename = animeinput.replace(" ", "_")
    animesearch = animeinput.replace(" ", "+")
    search_url = f"{BASE_URL}/search.html?keyword={animesearch}"

    print()
    print("Anime found:")
    animelist =  list(await scrape_search(search_url, session))
    for i, (name, _) in enumerate(animelist):
        print(f" {i+1:2d}: {name}")
    input_number = input("Enter number of anime to download: ")
    input_number = int(input_number) - 1

    name, url = animelist[input_number]
    anime_url = BASE_URL + url

    print()
    print(f"Selected anime: {name} :: {anime_url}")
    rename = input(f"Enter save name ('{animename}'): ")
    if rename != "":
        animename = rename
    return animename, anime_url

def get_episode_name(episode_url: str) -> str:
    return episode_url.split("episode-")[1] # CHECK: Is this always the case

semaphore = asyncio.Semaphore(DOWNLOAD_THREADS)

async def download_episode(url, animename: str, episode_name: str):
    tmp_path = f"out/{animename}/tmp/{episode_name}.{FORMAT}"
    output_path = f"out/{animename}/{episode_name}.{FORMAT}"
    process = (
        FFmpeg()
        .input(url)
        .output(tmp_path, format=FORMAT, codec="copy")
    )
    await semaphore.acquire()
    print(f"Starting: {episode_name} ::: {url}")
    if os.path.exists(tmp_path): os.remove(tmp_path)
    try:
        await process.execute()
    except:
        process.terminate()
        raise
    os.rename(tmp_path, output_path)
    print(f"Finished: {episode_name}")
    semaphore.release()

@soupify
def scrape_search(soup: BeautifulSoup) -> Generator[tuple[str, str], None, None]:
    search_results = (
        soup
        .find(id="wrapper_bg")
        .find("section", {"class": "content"})
        .find("section", {"class": "content_left"})
        .find("div", {"class": "main_body"})
        .find("div", {"class": "last_episodes"})
        .find("ul", {"class": "items"})
        .find_all("li")
    )

    for li in search_results:
        a = li.find("p").find("a")
        a_link = a.attrs["href"]
        yield a.text, a_link

@soupify
def scrape_main(soup: BeautifulSoup) -> Generator[str, None, None]:
    for li in soup.find(id="episode_related").find("div").find_all("li"):
        a = li.find("a")
        yield a.attrs["href"]

@soupify
def scrape_episode(soup: BeautifulSoup) -> str:
    element = soup.find("iframe")
    return element.attrs["src"]

async def scrape_playlist(outer_url: str, session: aiohttp.ClientSession):
    playlist = m3u8.load(outer_url)
    max_playlist: m3u8.Playlist = max(playlist.playlists, key=lambda p: p.stream_info.resolution)
    return max_playlist.absolute_uri
  
stream_regex = re.compile(r'playlist:\s*\[\s*\{\s*sources:\s*\[\{\s*file:\s*"(https:\/\/[^"]+\.m3u8)"\s*\}\s*\],\s*\},\s*\]')
@soupify
def scrape_stream(soup: BeautifulSoup) -> str:
    """Scrapes the playlist url from the given stream url"""
    match = stream_regex.search(str(soup))
    return match.group(1)

async def main():
    async with aiohttp.ClientSession() as session:
        animename, main_url = await get_anime_info(session)
        tmp_folder = f"out/{animename}/tmp"
        os.makedirs(tmp_folder, exist_ok = True)

        async def download(episode_url: str):
            episode_no = get_episode_name(episode_url)
            filename = f"{animename}_episode_{episode_no}"
            if (os.path.exists(f"out/{animename}/{filename}.{FORMAT}")):
                print(f"Skipping: {animename}_episode_{episode_no}")
                return
            else:
                print(f"Downloading: {animename}_episode_{episode_no}")

            if not SIMULATE:
                stream_url = await scrape_episode(BASE_URL + episode_url, session)
                outer_playlist_url = await scrape_stream(stream_url, session)
                playlist_url = await scrape_playlist(outer_playlist_url, session)
                await download_episode(playlist_url, animename, filename)

        print()
        await asyncio.gather(*map(download, await scrape_main(main_url, session)))
        
        if len(os.listdir(tmp_folder)) == 0:
            os.removedirs(tmp_folder)

if __name__ == "__main__":
    for arg in sys.argv[1:]:

        splitted = arg.split("=")
        if len(splitted) != 2: 
            print(f"Wrong argument format '{arg}'. Use for example 'format=mpeg'.")
            exit(1)
        cmd, value = splitted
        cmd = cmd.lower()

        if cmd in ["threads", "n"]: DOWNLOAD_THREADS = int(value)
        elif cmd in ["url", "base"]:
            m = re.match(r"(https:\/\/gogoanime.\w+)./", value)
            BASE_URL = m.group[1]
            FULL_URL = value if "/category/" in value else None
        elif cmd in ["format", "f"]: FORMAT = value
        elif cmd in ["simulate", "s"]: SIMULATE = False if value.lower() in ["0", "false", "no", "n", "f"] else True
        else:
            print(f"Unknown argument name '{cmd}'. Only 'threads', 'url', 'format', 'simulate' are valid arguments.")
            exit(1)

    asyncio.run(main())
    print("PROGRAM END")

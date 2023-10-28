import aiohttp
from bs4 import BeautifulSoup
import m3u8
from ffmpeg.asyncio import FFmpeg
import asyncio
import re
import os

main_url = "https://gogoanime.dev/category/tensei-shitara-slime-datta-ken-dub"
ep1_url = "https://gogoanime.dev/tensei-shitara-slime-datta-ken-dub-episode-1"
stream_url = "https://player.mangafrenzy.net/streaming/tensei-shitara-slime-datta-ken-dub-episode-1"
playlist_url = "https://www028.vipanicdn.net/streamhls/715d353df61f474f6ac6a7ee81e295f7/ep.1.1677648202.1080.m3u8"

def soupify(func):

    async def wrapper(url: str, session: aiohttp.ClientSession):
        async with session.get(url) as response:
            http = await response.text()
        soup = BeautifulSoup(http, features="html.parser")
        return func(soup)
    
    return wrapper

def get_episode_name(episode_url: str) -> str:
    return episode_url.split("episode-")[1] # CHECK: Is this always the case

semaphore = asyncio.Semaphore(4)

async def download_episode(url, animename: str, episode_name: str):
    process = (
        FFmpeg()
        .input(url)
        .output(f"out/{animename}/{episode_name}.mp4", format="mp4")
    )
    await semaphore.acquire()
    await process.execute()
    semaphore.release()

@soupify
def scrape_main(soup: BeautifulSoup):
    for li in soup.find(id="episode_related").find("div").find_all("li"):
        a = li.find("a")
        yield a.attrs["href"]

@soupify
def scrape_episode(soup: BeautifulSoup):
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
    os.makedirs("out", exist_ok = True)
    animename = "Reincarnated as a Slime"
    animename = animename.replace(" ", "_")
    os.makedirs(f"out/{animename}", exist_ok = True)

    base_url = re.search(r"(https:\/\/\w+\.\w+)\/.*", main_url).group(1)
    print(f"Searching on {base_url}")

    async with aiohttp.ClientSession() as session:
        async def download(episode_url: str):
            stream_url = await scrape_episode(base_url + episode_url, session)
            episode_no = get_episode_name(episode_url)
            outer_playlist_url = await scrape_stream(stream_url, session)
            playlist_url = await scrape_playlist(outer_playlist_url, session)
            await download_episode(playlist_url, animename, f"{animename}_episode_{episode_no}")
            print(f"Downloaded: {animename}_episode_{episode_no} ::: {playlist_url}")

        await asyncio.gather(*map(download, await scrape_main(main_url, session)))

asyncio.run(main())

print("PROGRAM END")







content = """
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="IE=edge" http-equiv="X-UA-Compatible"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>You're Watching episode  of  on As2anime</title>
<link href="/player.css" rel="stylesheet"/>
<script src="/jw.js"></script>
<script src="/jquery.js"></script>
<link crossorigin="anonymous" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" integrity="sha512-MV7K8+y+gLIBoVD59lQIYicR65iaqukzvf/nwasF0nqhPay5w/9lJmVM2hMDcnK1OnMGCdVK+iQrJ7lzPJQd1w==" referrerpolicy="no-referrer" rel="stylesheet"/>
<style>
      #player { width: 100vw !important; height: 100vh !important; } #player_loader { position: absolute; width: 100%;
      height: 100%; } .jw-preview { filter: blur(8px) !important; -webkit-filter: blur(8px) !important; } .skip_btn {
      position: absolute; bottom: 150%; left: 5%; z-index: 5; color: var(--accent-color); border: solid 2px
      var(--accent-color); border-radius: 0.5rem; outline: none; background: none; font-size: 20px; font-family:
      "Rubik", Arial, sans-serif; font-weight: 700; padding: 5px 10px; width: 150px; transition: all 0.5s ease-in-out; }
      .skip_btn:hover { color: var(--primary-color); background: var(--third-color); border: solid 2px
      var(--third-color); transition: all 0.5s ease-in-out; } /*** mobile to tablet and large tablets screens ***/
      @media (max-width: 700px) { .skip_btn { font-size: 15px; width: 100px; } } /*** mobile to tablet screens ***/ /***
      mobile to tablet and large tablets screens ***/ @media (max-width: 400px) { .skip_btn { font-size: 10px; width:
      75px; } } /*** mobile to tablet screens ***/
    </style>
</head>
<body>
<div class="wrap">
<div id="player"></div>
</div>
</body>
<script>
    const controls = true; const displaytitle = false; const displaydescription = false; const autostart = false; const
    playerInstance = jwplayer("player").setup({ controls: controls, displaytitle: displaytitle, displaydescription:
    displaydescription, autostart: autostart, skin: { name: "netflix", }, playlist: [ { sources: [{ file: "https://www028.vipanicdn.net/streamhls/715d353df61f474f6ac6a7ee81e295f7/ep.1.1677648202.m3u8" }],
    }, ], advertising: { client: "", schedule: [ { offset: "pre", tag: "", }, ], }, }); playerInstance.on("ready",
    function () { const playerContainer = playerInstance.getContainer(); const buttonContainer =
    playerContainer.querySelector(".jw-button-container"); const spacer = buttonContainer.querySelector(".jw-spacer");
    const timeSlider = playerContainer.querySelector(".jw-slider-time"); buttonContainer.replaceChild(timeSlider,
    spacer); const player = playerInstance; const rewindContainer =
    playerContainer.querySelector(".jw-display-icon-rewind"); const forwardContainer = rewindContainer.cloneNode(true);
    const forwardDisplayButton = forwardContainer.querySelector(".jw-icon-rewind"); forwardDisplayButton.style.transform
    = "scaleX(-1)"; forwardDisplayButton.ariaLabel = "Forward 10 Seconds"; const nextContainer =
    playerContainer.querySelector(".jw-display-icon-next"); nextContainer.parentNode.insertBefore(forwardContainer,
    nextContainer); playerContainer.querySelector(".jw-display-icon-next").style.display = "none"; const
    rewindControlBarButton = buttonContainer.querySelector(".jw-icon-rewind"); rewindControlBarButton.ariaLabel =
    "Backward 10 Seconds"; const forwardControlBarButton = rewindControlBarButton.cloneNode(true);
    forwardControlBarButton.style.transform = "scaleX(-1)"; forwardControlBarButton.ariaLabel = "Forward 10 Seconds";
    rewindControlBarButton.parentNode.insertBefore( forwardControlBarButton, rewindControlBarButton.nextElementSibling,
    ); [forwardDisplayButton, forwardControlBarButton].forEach((button) => { button.onclick = () => {
    player.seek(player.getPosition() + 10); }; }); });
  </script>
</html>
"""

stream_regex.search(content)

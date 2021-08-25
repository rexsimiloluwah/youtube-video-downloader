import os 
import threading
from pytube import YouTube, Playlist
from collections import OrderedDict 

DOWNLOADS_DIR = './downloads'
resolutions = (144, 240, 360, 480, 720, 1080)

def download_video(video_object: dict, resolution: int=None, best:bool = False, **kwargs):
    try:
        if best:
            video = video_object["streams"].get_highest_resolution()
            video.download(DOWNLOADS_DIR)
        else:
            if resolution not in resolutions:
                raise ValueError(f"Resolution must be one of {resolutions}")
            video = video_object["streams"].filter(file_extension="mp4", resolution=f"{str(resolution)}p")
            video[0].download(DOWNLOADS_DIR)    
    except OSError:
        print("Could not save file, no space left on device.")


def download_playlist(url: str, **kwargs):
    playlist = Playlist(url)
    print(f"[PLAYLIST TITLE]: {playlist.title}")
    print(f"[VIDEOS]: {len(playlist.videos)} videos")
    video_urls = playlist.video_urls
    print(video_urls, len(video_urls))
    thread_list = []
    
    for url in video_urls:
        thread = threading.Thread(target=download_video, args=(video_description(url), 720))
        thread_list.append(thread)
        # start the thread
        thread.start()

    for thread in thread_list:
        thread.join()

def video_description(url: str, on_download_progress, on_download_complete):
    video_object = OrderedDict()
    video = YouTube(
        url,
        on_progress_callback = on_download_progress,
        on_complete_callback = on_download_complete
    )
    video_object['title'] = video.title 
    video_object['thumbnail'] = video.thumbnail_url
    video_object['streams'] = video.streams 
    video_object['length'] = video.length 
    video_object['description'] = video.description
    return video_object

def on_download_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize 
    bytes_downloaded = total_size - bytes_remaining 
    percentage_of_completion = (bytes_downloaded / total_size) * 100
    print(f"[PERCENTAGE OF COMPLETION]: {round(percentage_of_completion)}")

def on_download_complete(stream, filepath):
    print(f'[COMPLETED]: Saved in {filepath}')

if __name__=='__main__':
    video_obj = video_description('https://youtu.be/vo_lZiytsMw', on_download_progress, on_download_complete)
    playlist_url= 'https://youtu.be/FLQ-Vhw1NYQ?list=PL4cUxeGkcC9jLYyp2Aoh6hcWuxFDX6PBJ'
    #download_video(video_obj, best=True)
    download_playlist(playlist_url)
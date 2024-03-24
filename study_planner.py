import subprocess
import json
import math
from datetime import datetime, timedelta

def fetch_playlist_videos(playlist_url):
    command = ['yt-dlp', '-J', '--flat-playlist', playlist_url]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode == 0:
        playlist_info = json.loads(result.stdout)
        playlist_title = playlist_info.get('title', 'Untitled Playlist').replace('/', '-').replace('\\', '-')
        videos = [(video.get('title', 'Untitled Video'), math.ceil(video.get('duration', 0) / 60))
                  for video in playlist_info.get('entries', []) if 'duration' in video]
        return playlist_title, videos
    else:
        print(f"Error fetching playlist information: {result.stderr}")
        return None, []

def schedule_videos(videos, start_date):
    schedule = {}
    current_date = start_date
    daily_duration = 0
    for title, duration in videos:
        if daily_duration + duration > 60:
            current_date += timedelta(days=1)
            daily_duration = 0
        if current_date not in schedule:
            schedule[current_date] = []
        schedule[current_date].append((title, duration))
        daily_duration += duration
    return schedule

def write_schedule_to_file(schedule, playlist_title, start_date):
    filename = f"{playlist_title}_studyplanner.txt"
    completion_date = max(schedule.keys())
    total_days = (completion_date - start_date).days + 1  # +1 to include the start day
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"You will complete this course in {total_days} days.\n\n")
        for date, videos in schedule.items():
            file.write(date.strftime("%m/%d/%Y") + "\n")
            for title, duration in videos:
                file.write(f"  * {title} - {duration} minutes\n")
            file.write("\n")
    print(f"Study plan has been written to {filename}")

def main():
    playlist_url = input("Please enter the YouTube playlist URL: ")
    start_date_str = input("Enter the start date for your study schedule (MM/DD/YYYY): ")
    start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
    
    playlist_title, videos = fetch_playlist_videos(playlist_url)
    
    if playlist_title and videos:
        schedule = schedule_videos(videos, start_date)
        write_schedule_to_file(schedule, playlist_title, start_date)

if __name__ == "__main__":
    main()

import requests
import musicbrainzngs as mbz 
mbz.set_useragent("collector.io", "0.1", "(jeff@jeff.com)")


def artist_search(artist):
    artist_list = mbz.search_artists(query=artist)['artist-list'] 
    # print(f"artist list: {artist_list}")
    # artist = artist_list[0] 
    # print(f"artist list:{artist}")
    return artist_list

# Keyword arguments to the "search_*" functions limit keywords to
    # specific fields. The "limit" keyword argument is special (like as
    # "offset", not shown here) and specifies the number of results to
    # return.

def release_search(artist, album):
    print(f"artist: {artist} | album: {album}")
    result = mbz.search_releases(artist=artist, release=album, limit=10)
    # On success, result is a dictionary with a single key:
    # "release-list", which is a list of dictionaries.
    # print(result)
    return result



""" 
Function to find all release groups that matcht teh criteria

input: artist name and album
output: all release groups that match the criteria

example:
    artist_name = "U2"
    album_title = "The Joshua Tree"
    
    release_groups = search_release_group(artist_name, album_title)
"""
def release_group_search(artist_name, album_title):
    if artist_name and album_title:
        url = f"https://musicbrainz.org/ws/2/release-group/?query=artist:{artist_name} AND release:{album_title}&fmt=json"
    else:
        url = f"https://musicbrainz.org/ws/2/release-group/?query=artist:{artist_name}&fmt=json"
    response = requests.get(url)
    data = response.json()
    release_groups = data.get("release-groups", [])

    for release_group in release_groups:
        print("Title:", release_group.get("title"))
        print("Release Group ID:", release_group.get("id"))
        print()

    return release_groups

"""
Function to get the relesae groeup info.

input:  release group id
Output: dict with release group info
"""
def get_release_group_info(release_group_id):
    print(f"release group id: {release_group_id}")

    # url = f"https://musicbrainz.org/ws/2/release-group/{release_group_id}&fmt=json"
    url = f"https://musicbrainz.org/ws/2/release-group/{release_group_id}?inc=aliases%2Bartist-credits%2Breleases&fmt=json"	

    response = requests.get(url)
    print(f"response: {response}")
    
    if response.status_code == 200:
        print(f"response {response}")

        data = response.json()
        # print(f"response json {data}")
        # print("First release date:", data.get("first-release-date"))
        # print("Release Group Title:", data.get("title"))
        # print("Primary Type:", data.get("primary-type"))
        # print("Secondary Types:", data.get("secondary-types", []))
        # Print other relevant information as needed
    
        return data
    else:
        print(f"Release group information not found. Response is {response.status_code}")
        return None


def milliseconds_to_minutes_seconds(milliseconds):
    total_seconds = milliseconds // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"  # Format seconds with leading zero if necessary

    # # Example usage:
    # duration_milliseconds = 185693
    # duration_formatted = milliseconds_to_minutes_seconds(duration_milliseconds)
    # print(duration_formatted)  # Output: 3:05


import re

"""
Function to check if a date (e.g. release group first release date) has the correct format (YYYY-MM-DD)
If it is just a year turn it into the correct format

Input: date (either YYYY-MM-DD or YYYY)
Output: correctly formatted date -> YYYY-MM-DD
"""
def format_date(input_date):
    # Regular expression to match YYYY-MM-DD format
    yyyy_mm_dd_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    # Regular expression to match YYYY format
    yyyy_pattern = re.compile(r'^\d{4}$')

    if yyyy_mm_dd_pattern.match(input_date):
        # Input date is already in YYYY-MM-DD format
        return input_date
    elif yyyy_pattern.match(input_date):
        # Input date is in YYYY format
        return f"{input_date}-01-01"
    else:
        # Invalid format, return None or handle accordingly
        return "1900-01-01"

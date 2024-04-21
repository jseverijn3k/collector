import requests
import musicbrainzngs as mbz 
from .models import Artist
import uuid

mbz.set_useragent("collector.io", "0.1", "(jeff@jeff.com)")


def artist_search(artist):
    try:
        artist_list = mbz.search_artists(query=artist)['artist-list'] 
        # print(f"artist list: {artist_list}")
        # artist = artist_list[0] 
        # print(f"artist list:{artist}")
        return artist_list
    except mbz.ResponseError as e:
        print("Error searching artist:", e)
        return None
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

"""
Function toget all artists from a certain hitdossier-online list
"""

from bs4 import BeautifulSoup
import requests

def get_artists_from_hitdossier_online(url):

    # URL of the website
    url = "https://www.hitdossier-online.nl/npo-radio-2-top-2000-puntenlijst"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all td elements with class "totalen-artiesten"
        artist_elements = soup.find_all("td", class_="totalen-artiesten")
        
        # Extract artist names from the elements
        artists = [artist.text.strip() for artist in artist_elements]

        # Remove duplicates from the list
        unique_artists = list(set(artists))
        
        # Print the unique artist names with index numbers
        for index, artist in enumerate(unique_artists, start=1):
            print(f"{index}. {artist}")
        
        print(f"################################")
            
        # add artists to the databaase
        print(f"Add artists to the database")
        artists_added, artists_matched, artists_unmatched = add_artists_to_database(unique_artists)
        # Get the count of items in each list
        print(f"added_count = {len(artists_added)}")
        print(f"matched_count = {len(artists_matched)}")
        print(f"unmatched_count = {len(artists_unmatched)}")


        return unique_artists
    else:
        print("Error fetching the webpage")
        return []


"""
Function to add all artists from a list (e.g. hitdossier-online) to the database as an artist
using the following steps:

1. Iterate through your list of unique artist names.
2. For each artist, perform a search using the MusicBrainz API to get their MusicBrainz ID.
3. Check if the artist already exists in your database based on their MusicBrainz ID or name.
4. Add new artists to the database, update existing artists' MusicBrainz IDs if needed, and keep track of unmatched artists.

"""
def add_artists_to_database(artists_list):
    artists_added = []
    artists_matched = []
    artists_unmatched = []

    # print(f"artist list {artists_list}")
    for artist_name in artists_list:
        # Search for the artist on MusicBrainz
        search_result = artist_search(artist_name)

        if search_result:
            # Check if there are exact matches
            exact_matches = [artist for artist in search_result if artist['name'] == artist_name]
            # print(f"exact artist matches {exact_matches}")

            if exact_matches:
                # Get the MusicBrainz ID of the first exact match
                musicbrainz_id = exact_matches[0]['id']

                # Check if the artist already exists in the database
                existing_artist = Artist.objects.filter(name=artist_name).first()

                if existing_artist:
                    # Update the MusicBrainz ID if needed
                    if existing_artist.musicbrainz_id != musicbrainz_id:
                        existing_artist.musicbrainz_id = musicbrainz_id
                        existing_artist.save()
                        artists_matched.append(artist_name)
                    else:
                        artists_matched.append(artist_name)  # Artist already in DB with correct MBID
                else:
                    # Create a new artist entry in the database
                    new_artist = Artist.objects.create(
                        id=uuid.uuid4(),
                        musicbrainz_id=musicbrainz_id,
                        name=artist_name
                    )
                    artists_added.append(artist_name)
                    print(f"Artist added: {artist_name}")
            else:
                artists_unmatched.append(artist_name)  # No exact match found on MusicBrainz
                print(f"Artist unmatched: {artist_name}")
        else:
            artists_unmatched.append(artist_name)  # Error or no results from MusicBrainz
            print(f"Artist returrned error from MB: {artist_name}")

    return artists_added, artists_matched, artists_unmatched

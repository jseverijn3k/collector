
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


def milliseconds_to_minutes_seconds(milliseconds):
    total_seconds = milliseconds // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"  # Format seconds with leading zero if necessary

    # # Example usage:
    # duration_milliseconds = 185693
    # duration_formatted = milliseconds_to_minutes_seconds(duration_milliseconds)
    # print(duration_formatted)  # Output: 3:05
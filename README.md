# Documentation

## Backup and Restore routine

### Backup

1. stop the server
2. empty the backup folder -> delete all files
3. run: `./manage.py backup_data`

The backup folder should be created with:

* a backup_data.json file with all data
* a cover_art folder with all cover art

### Restore

1. delete the sqlite3.db database
2. run: `./manage.py migrate` -> to create a new database and migrate (create) all tables
3. run: `./manage.py createsuperuser` -> to create a super user (needed tot add a release to a collection which is ownede by a user)
   1. name: admin
   2. email: `admin@admin.com`
   3. password: mikdik
4. run: `./manage.py restore_data` -> all data from teh backup should be restored
5. run: `./manage.py runserver` -> to run the server and check if all data is restored

## TODO

### MVP

* add all artist albums / release groups (albums, eps, singles) to the database
  * also add them to the backup and restore routine
  * should we have a standard artist list that is being downloaded?
    * -> now only an overview of an artist in the database can be shown??
    * -> so something like a standard database setup... If so, should we make a standard 'stocklist' or something?? x-> MVP-2 is a BS4 scraper to scrape <https://www.hitdossier-online.nl>
      * create a function to:
        * read the stock list
        * query musicbrainz for artist mb_id
        * query the the releasegroups connected to the artist mb_id
        * add the found info (artist and release group) to the database (only if not already in the database of course)
        * create a command `./manage.py add_stocklist_to_db` -> as a standard command?
* change the artist_album url to artist_discography -> since not just albums but also EPs and singles are shown
  * add buttons -> want ohave to a release group
  * add indicator -> part of colelction to a release group
  * now when an artist has a lot of relese groups some are missing due to pagination? -> fix this
  * use secondary types to show as a sub within a category -> e.g. live is  subgroup within album, so is compilation
* show per artist which release groups (albums, eps, singles) you own
  * also add them to the backup and restore routine
* speed up the search when you search for a release -> now waiting for the cover art takes to long
* when there are a lot of releases more should be shown -> pagination?
~~* add barcode release search -> useful whene there are a lot of different release groups...~~
~~* add spinner to add release button to show that the api request is still ongoing~~
* add format (https://musicbrainz.org/doc/Release/Format) to search query --> PARTLY working... when I use vinyl I also get CDs if there are less than 10 (which is the limit) results 
* make a "want to buy list" -> based on the artist release groups you don't own yet (not releases)
  * export this as a text file so you can take it as a shopping list with you
  * also add this to the backup and restore routine

### MVP-2

* <https://www.hitdossier-online.nl/> -> lijsten scrapen en relateren aan artists
* create a BS4 scraper to scrape:
  * <https://www.hitdossier-online.nl/radio-veronica-top-1000-allertijden-artiestenlijst>
  * <https://www.hitdossier-online.nl/npo-radio-2-top-2000-2023>
  * and create an artist list
  * should we store the actual tracks in the database? so we can have an overview of all tracks w ehave and on which release (cd / vinyl / single) they can be found
  * and which track we still miss and want to own?
* create a better filter system -> format (cd / vinyl / etc..)
* show artist info -> from wikipedia

### Nice to haves

* create a barcode scanner -> to search on barcode
* create a shazam function -> to search on music played

## BUGS

* When adding Billy Joel - Greatest Hits Volume I and II -> only the tracks of the first disc are added

## Decisions

### Design decisions

* we add releases -> the thing you can actually buy, not release groups whioch are an abstract type

### Implementation decisions

* We start with a small (self defined stocklist):
  * based on the artists in 
    * <https://www.hitdossier-online.nl/radio-veronica-top-1000-allertijden-artiestenlijst>
    * <https://www.hitdossier-online.nl/npo-radio-2-top-2000-2023>
  * -> As of October 2023, MusicBrainz contains information on roughly 2.2 million artists, 3.9 million releases, and 30.4 million recordings -> otherwise we would have a lot of crap.. probably a thousand artists are enough for me right now...

# Documentation

## Backup and Restore routine

### Backup

1. stop the server
2. empty the backup folder -> delete all files
3. run: ./manage.py back_up data

The backup folder should be created with:

* a backup_data.json file with all data
* a cover_art folder with all cover art

### Restore

1. delete the sqlite3.db database
2. run: ./manage.py migrate -> to create a new database and migrate (create) all tables
3. run: ./manage.py createsuperuser -> to create a super user (needed tot add a release to a collection which is ownede by a user)
   1. name: admin
   2. email: "admin@admin.com"
   3. password: mikdik
4. run: ./manage.py restore_data -> all data from teh backup should be restored
5. run: ./manage.py runserver -> to run the server and check if all data is restored

## TODO

### MVP

* add all artist albums / release groups (albums, eps, singles) to the database
* show per artist which release groups (albums, eps, singles) you own
* speed up the search when you search for a release -> now waiting for the cover art takes to long
* when there are a lot of releases more should be shown -> pagination?

* make a "want to buy list" -> based on the artist release groups you don't own yet (not releases)
  * export this as a text file so you can take it as a shopping list with you
* create a better filter system -> format (cd / vinyl / etc..)

### MVP-2

* show artist info -> from wikipedia

### Nice to haves

* create a barcode scanner -> to search on barcode
* create a shazam function -> to search on music played

## Decisions

* we add releases -. the thing you can actually buy, not release groups whioch are an abstract type

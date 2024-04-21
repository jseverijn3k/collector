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

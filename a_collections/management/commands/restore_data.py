import os
import json
import uuid
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from a_collections.models import Artist, Record_Label, Release, Track, Cover_Art, Collection, Tag, Release_Group


class Command(BaseCommand):
    help = 'Restore data to Django app'

    def handle(self, *args, **kwargs):
        backup_dir = 'backup'  # Assuming backup directory is in the root of your project
        file_path = os.path.join(settings.BASE_DIR, backup_dir, 'backup_data.json')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f"Backup file {file_path} does not exist."))
            return
        
        with open(file_path, 'r') as f:
            backup_data = json.load(f)
        
        model_mapping = {
            'artists': Artist,
            'record_labels': Record_Label,
            'release_groups': Release_Group,
            'releases': Release,
            'tracks': Track,
            'cover_art': Cover_Art,
            'collections': Collection,
            'tags': Tag,
        }

        for model_name, objects in backup_data.items():
            model_class = model_mapping.get(model_name.lower())
            if model_class:
                for obj_list in objects:
                    for obj in obj_list:
                        try:
                            # handle the foreign keys
                            if model_name == 'collections':
                                print("######COLLECTIONS##########")
                                release_id = obj['release']
                                release_id = uuid.UUID(release_id)

                                release = Release.objects.get(id=release_id)
                                print(f"release is: {release} | type is: {type(release)}")
                                obj['release'] = release
                            
                                user = User.objects.get(id=obj['user'])
                                print(f"release is: {user} | type is: {type(user)}")
                                obj['user'] = user

                            
                            elif model_name == 'tracks':
                                print("######TRACKS##########")
                                release_id = obj['release']                            
                                release_id = uuid.UUID(release_id)
                                
                                release = Release.objects.get(id=release_id)
                                print(f"release is: {release} | type is: {type(release)}")
                                obj['release'] = release
                            
                            elif model_name == 'cover_art':
                                print("######COVER ART##########")
                                release_id = obj['release']
                                release_id = uuid.UUID(release_id)
                                
                                release = Release.objects.get(id=release_id)
                                print(f"release is: {release} | type is: {type(release)}")
                                obj['release'] = release
                            
                            elif model_name == 'release_groups':
                                print("######RELEASE GROUPS##########")

                                artist_str_id = obj['artist']
                                artist_id = uuid.UUID(artist_str_id)

                                artist = Artist.objects.get(id=artist_id)
                                print(f"artist is: {artist} type: {type(artist)}")
                                # Assign the Artist object to the artist field
                                obj['artist'] = artist

                            elif model_name == 'releases':
                                print("######RELEASES##########")
                                record_lab_id = obj['record_label']
                                record_id = uuid.UUID(record_lab_id)

                                record_label = Record_Label.objects.get(id=record_id)
                                print(f"record label is: {record_label} | type is: {type(record_label)}")

                                # Assign the Record_Label object to the record_label field
                                obj['record_label'] = record_label

                                release_group_str_id = obj['release_group']
                                release_group_id = uuid.UUID(release_group_str_id)

                                release_group = Release_Group.objects.get(id=release_group_id)
                                print(f"Release_group is: {release_group} type: {type(release_group)}")
                                # Assign the Release_Group object to the release_group field
                                obj['release_group'] = release_group
                                

                                # artist_str_id = obj['artist']
                                # artist_id = uuid.UUID(artist_str_id)

                                # artist = Artist.objects.get(id=artist_id)
                                # print(f"artist is: {artist} type: {type(artist)}")
                                # # Assign the Artist object to the artist field
                                # obj['artist'] = artist


                            # Check if the object already exists in the database
                            if not model_class.objects.filter(id=obj['id']).exists():
                                print(f"Creating object for model {model_name}: {obj}")
                                model_class.objects.create(**obj)
                            else:
                                print(f"Skipping creation of object for model {model_name}: {obj['musicbrainz_id']} already exists.")
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Failed to create object for model {model_name}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Model {model_name} not found in the mapping."))
        

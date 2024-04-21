import os
import json
import uuid
import shutil  # Add this import
from django.conf import settings


from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from a_collections.models import Artist, Record_Label, Release, Track, Cover_Art, Collection, Tag, Release_Group
from django.db.models.fields.files import ImageFieldFile


class Command(BaseCommand):
    help = 'Backup data from Django app'

    def handle(self, *args, **options):
        backup_dir = 'backup'
        os.makedirs(backup_dir, exist_ok=True)

        backup_data = {
            # 'artists': self.serialize_model(Artist.objects.all()),
            # 'record_labels': self.serialize_model(Record_Label.objects.all()),
            'artists': [self.serialize_model(Artist)],
            'record_labels': [self.serialize_model(Record_Label)],
            'release_groups': [self.serialize_model(Release_Group)],
            'releases': [self.serialize_model(Release)],
            'tracks': [self.serialize_model(Track)],
            'cover_art': [self.serialize_model(Cover_Art)],
            'collections': [self.serialize_model(Collection)],
            'tags': [self.serialize_model(Tag)],
        }

        print(f"backup data: {backup_data}")

        # Copy cover_art pictures to the backup directory
        # media_dir = 'media/cover_art'
        print(f"media root: {settings.MEDIA_ROOT}")
        # media_dir = os.path.join(settings.MEDIA_ROOT, "cover_art/")
        media_dir = str(settings.MEDIA_ROOT)
        print(f"media dir: {media_dir}")

        backup_cover_art_dir = os.path.join(backup_dir, 'cover_art')
        os.makedirs(backup_cover_art_dir, exist_ok=True)
        
        for cover_art in Cover_Art.objects.all():
            if cover_art.image:
                print(f"cover_art.image : {str(cover_art.image)}")
                # src_path = os.path.join(settings.BASE_DIR, str(cover_art.image))
                src_path = os.path.join(settings.BASE_DIR, str(cover_art.image))

                print(f"settings.BASE_DIR: {settings.BASE_DIR}")
                print(f"source path: {src_path}")
                # image_relative_path = cover_art.image.url[len(settings.MEDIA_URL):]  # Remove MEDIA_URL prefix
                image_relative_path = str(cover_art.image)
                relative_path = image_relative_path[len("/mediafiles"):]
                relative_path = media_dir + relative_path

                print(f"relative path: {relative_path}")
                # src_path = os.path.join(settings.MEDIA_ROOT, str(cover_art.image).lstrip('/'))
                src_path = os.path.join(settings.MEDIA_ROOT, str(relative_path)) 
                print(f"source path NEW: {src_path}")
    
                print(f"Absolute path: {os.path.abspath(src_path)}")

                dst_path = os.path.join(backup_cover_art_dir, str(cover_art.image))
                dst_image_relative_path = str(cover_art.image)
                dst_relative_path = dst_image_relative_path[len("/mediafiles"):]
                dst_path = str(settings.BASE_DIR) +"/backup/"+  str(dst_relative_path)
                print(f"destination path: {dst_path}")
                shutil.copyfile(src_path, dst_path)


        with open(os.path.join(backup_dir, 'backup_data.json'), 'w') as f:
            json.dump(backup_data, f, indent=4, cls=UUIDEncoder)

        print("Data backup completed successfully!!!!!")
        self.stdout.write(self.style.SUCCESS('Data backup completed successfully!'))

    def serialize_model(self, model):
        serialized_data = []
        for instance in model.objects.all():
            serialized_instance = {}
            for field in instance._meta.fields:
                field_name = field.name
                field_value = getattr(instance, field_name)
                if isinstance(field_value, uuid.UUID):
                    field_value = str(field_value)
                elif isinstance(field_value, ImageFieldFile):
                    field_value = str(field_value)  # Or you can save the path instead of the whole URL
                elif hasattr(field_value, 'pk'):
                    # If the field is a foreign key, serialize its primary key
                    field_value = field_value.pk
                serialized_instance[field_name] = field_value
            serialized_data.append(serialized_instance)
        return serialized_data



class UUIDEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

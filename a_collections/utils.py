import csv
from django.http import HttpResponse
from .models import Artist, Media, Record_Label


def download_csv(request):

    # Create a HttpResponse object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write headers
    writer.writerow(['Artist name', 'Media title', 'Media type', 'Media release year', 'Media catalog nr', 'Record label'])

    media_data = Media.objects.all()
    artist_data = Artist.objects.all()

    # Write data rows
    for obj1 in media_data:
        for obj2 in artist_data.filter(foreign_key_field=obj1):
            writer.writerow([obj2.name, obj1.title, obj1.type, obj1.release_year, obj1.catalog_number, obj1.record_label])

    return response
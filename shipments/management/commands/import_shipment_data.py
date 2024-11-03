
import csv
import os
from django.core.management.base import BaseCommand

from shipments.models import Article, Shipment, ArticleShipmentItem

class Command(BaseCommand):
    help = 'Load shipment data from a csv file'

    def handle(self, *args, **options):
        csv_file_name = 'data.csv'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, csv_file_name)        
        self.stdout.write(f"Attempting to open file at: {csv_file_path}")

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file.read().splitlines())
            for row in reader:
                self.stdout.write(f"Importing: {row['tracking_number']}")
                article, is_article_created = Article.objects.get_or_create(
                    name=row['article_name'],
                    price=row['article_price'],
                    sku=row['SKU']
                )
                shipment, created = Shipment.objects.get_or_create(
                    tracking_number=row['tracking_number'],
                    carrier=row['carrier'],
                    defaults={
                        'sender_address': row['sender_address'],
                        'receiver_address': row['receiver_address'],
                        'status': row['status']
                    }
                )
                ArticleShipmentItem.objects.get_or_create(
                    article=article,
                    shipment=shipment,
                    defaults={
                        'quantity': row['article_quantity']
                    }
                )
        self.stdout.write("Data imported successfully!")

from django.db import models

from .validators import validate_comma_separated_address

class Article(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Shipment(models.Model):
    articles = models.ManyToManyField(Article, through='ArticleShipmentItem', related_name='shipments')
    tracking_number = models.CharField(max_length=100)
    carrier = models.CharField(max_length=32)
    sender_address = models.CharField(max_length=255, validators=[validate_comma_separated_address])
    receiver_address = models.CharField(max_length=255, validators=[validate_comma_separated_address])

    class ShipmentStatus(models.TextChoices):
        IN_TRANSIT = 'IN_TRANSIT', 'in-transit'
        INBOUND_SCAN = 'INBOUND_SCAN', 'inbound-scan'
        DELIVERY = 'DELIVERY', 'delivery'
        TRANSIT = 'TRANSIT', 'transit'
        SCANNED = 'SCANNED', 'scanned'

    status = models.CharField(max_length=12, choices=ShipmentStatus.choices)

    class Meta:
        indexes = [
            models.Index(
                fields=['carrier', 'tracking_number'],
                name='carrier_tracking_number_index'
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=('carrier', 'tracking_number'),
                name='unique_carrier_tracking_number'
            )
        ]
    
    def __str__(self):
        return f'{self.carrier} - {self.tracking_number}'


class ArticleShipmentItem(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('article', 'shipment'),
                name='unique_article_shipment'
            )
        ]

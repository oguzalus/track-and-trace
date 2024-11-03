from django.contrib import admin

from .models import Article, Shipment, ArticleShipmentItem

admin.site.register(Article)
admin.site.register(Shipment)
admin.site.register(ArticleShipmentItem)

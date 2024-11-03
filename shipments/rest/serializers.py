from rest_framework import serializers
from shipments.models import Article, ArticleShipmentItem, Shipment
from shipments.weather_integration import get_client


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'name', 'price', 'sku']


class ArticleShipmentItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='article.name')
    price = serializers.DecimalField(source='article.price', max_digits=10, decimal_places=2)
    sku = serializers.CharField(source='article.sku')

    class Meta:
        model = ArticleShipmentItem
        fields = ['id', 'name', 'price', 'sku', 'quantity']


class ShipmentSerializer(serializers.ModelSerializer):
    articles = ArticleShipmentItemSerializer(many=True, source='articleshipmentitem_set', read_only=True)
    weather = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'carrier', 'sender_address',
            'receiver_address', 'status', 'articles', 'weather',
        ]
    
    def get_weather(self, obj):
        location = obj.receiver_address.split(',')[3]
        return get_client().get_weather(obj.receiver_address)

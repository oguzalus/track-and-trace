from rest_framework import viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response


from shipments.models import Article, Shipment, ArticleShipmentItem
from .serializers import ArticleSerializer, ShipmentSerializer, ArticleShipmentItemSerializer

from rest_framework.views import APIView

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ArticleShipmentItemViewSet(viewsets.ModelViewSet):
    queryset = ArticleShipmentItem.objects.select_related('article')
    serializer_class = ArticleShipmentItemSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.prefetch_related('articles')
    serializer_class = ShipmentSerializer

    filterset_fields = ['status', 'tracking_number', 'carrier']

    @action(
        detail=False,
        url_path=r'(?P<carrier>[^/.]+)/(?P<tracking_number>[^/.]+)',
        url_name='get_shipment',
        permission_classes=[permissions.AllowAny]
    )
    def get_shipment(self, request, carrier, tracking_number):
        """ Get a single shipment by tracking number and carrier, without authentication. """
        shipment = get_object_or_404(self.get_queryset(), tracking_number=tracking_number, carrier=carrier)
        serializer = self.get_serializer(shipment)
        return Response(serializer.data)
    
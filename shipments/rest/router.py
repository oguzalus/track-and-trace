from rest_framework.routers import DefaultRouter

from shipments.views import ArticleViewSet, ArticleShipmentItemViewSet, ShipmentViewSet

router = DefaultRouter()

router.register(r'articles', ArticleViewSet)
router.register(r'article_shipment_items', ArticleShipmentItemViewSet)
router.register(r'shipments', ShipmentViewSet)

urls = router.urls

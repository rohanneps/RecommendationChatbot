from django.urls import path

from .views import RecommendationListView, RecommendationDetailView

app_name = 'recommendation'

urlpatterns = [
    path('all', RecommendationListView.as_view(), name='all_recommendations'),
    path('details/<int:pk>/', RecommendationDetailView.as_view(), name='recommendation_detail'),
]
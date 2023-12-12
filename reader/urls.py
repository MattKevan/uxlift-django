from django.urls import path
from . import views  # Assuming you have views you want to map
from .views import PostListView, refresh_feeds_ajax, submit_post

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('submit/', views.submit_url, name='submit_url'),
    path('sites/', views.list_sites, name='list_sites'),
    path('refresh-feeds/', refresh_feeds_ajax, name='refresh-feeds-ajax'),
    path('submit-post/', submit_post, name='submit_post'),
    path('topics/', views.topics, name='topics'),
    path('topics/<slug:tag_slug>/', views.topic_page, name='topic_page'),
    path('tools/', views.tools, name='tools'),
    path('tools/<slug:tool_slug>/', views.tool_page, name='tool_page'),

]
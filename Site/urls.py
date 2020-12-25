from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path
from Site import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/update/<int:pk>', views.UpdateArticle.as_view(), name='update_post'),
    path('articles/create', views.article_create, name='article_create'),
    path('create-newsletter/email', views.newsletter, name='newsletter'),
    url(r'article/view/(?P<id>\d+)/(?P<slug>[\w-]+)/$', views.post_details, name='article_detail'),
    path('like', login_required(views.like_photo), name='like_photo'),
    path('delete_post/<int:id>', views.delete_post, name='delete'),
    path('request/remove-newsletter/', views.DeleteNewsletter.as_view(), name='remove'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
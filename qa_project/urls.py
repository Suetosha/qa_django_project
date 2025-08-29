
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
    openapi.Info(
        title="Q&A API",
        default_version='v1',
        description="API-сервис для вопросов и ответов",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('qa_api.urls')),
    path('swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),

]

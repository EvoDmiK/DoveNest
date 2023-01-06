'''config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
'''
from django.urls import path, include, re_path
from django.contrib import admin

urlpatterns = [
    ## admin 페이지
    path('admin/', admin.site.urls),

    ## 구현할 페이지들 ''은 메인 페이지
    path('community/', include('community.urls')),
    path('profile/', include('UserProfile.urls')),
    path('news/', include('news.urls')),
    path('', include('main.urls')),

    ## 실험 페이지
    path('exp/', include('experiment.urls')),

    ## 소셜 로그인 관련 페이지들
    re_path(r'^accounts/', include('allauth.urls')),
]

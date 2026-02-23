"""
URL configuration for tools_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
"""
from django.contrib import admin
from django.urls import path,include
from tools.views import merge_pdf,compress_image,jpg_to_pdf,compress_pdf,home,split_pdf
from tools.views import (
    pdf_to_word,
    resize_image,
    protect_pdf,
    unlock_pdf,add_text_pdf
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('merge-pdf/', merge_pdf, name='merge_pdf'),
    path("compress-image/", compress_image, name="compress_image"),
    path("jpg-to-pdf/", jpg_to_pdf, name="jpg_to_pdf"),
    path("compress-pdf/", compress_pdf, name="compress_pdf"),
    path("", home, name="home"),
    path("split-pdf/", split_pdf, name="split_pdf"),
    path("pdf-to-word/", pdf_to_word, name="pdf_to_word"),
    path("resize-image/", resize_image, name="resize_image"),
    path("protect-pdf/", protect_pdf, name="protect_pdf"),
    path("unlock-pdf/", unlock_pdf, name="unlock_pdf"),
    path("add-text-pdf/", add_text_pdf, name="add_text_pdf"),
]

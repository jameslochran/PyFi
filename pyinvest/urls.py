"""pyinvest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
# from django.contrib import admin
# from django.urls import path
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
from django.contrib import admin, auth
from django.contrib.auth import views as auth_views
from django.urls import path

from pyfy import views
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    #AUTH
    path('signup', views.SignUp.as_view(), name='signup'),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    #Portfolios
    path('portfolio/create', views.CreatePortfolio.as_view(), name='create_portfolio'),
    path('portfolio/<int:pk>', views.DetailPortfolio.as_view(), name='detail_portfolio'),
    # path('dashboard', views.DashPortfolio.as_view(), name='dashboard'),
    path('portfolio/<int:pk>/update', views.UpdatePortfolio.as_view(), name='update_portfolio'),
    path('portfolio/<int:pk>/delete', views.DeletePortfolio.as_view(), name='delete_portfolio'),
    # path('<int:pk>/upvote', views.upvote, name='upvote'),
    #video
    path('portfolio/<int:pk>/addstock', views.add_Stock, name='add_stock'),
    path('stock/search', views.stock_search, name='stock_search'),
    path('stock/lookup', views.lookup, name='lookup'),
    path('stock/research', views.research, name='research'),
    path('portfolio/<int:pk>/detail', views.detail, name='detail'),
    path('portfolio/<int:pk>/total', views.dash_Total, name='total'),
    path('stock/pricelookup/<int:pk>', views.priceLookup, name='pricelookup'),
    path('stock/symbol', views.symbol, name='symbol'),
    path('stock/<int:pk>/delete', views.DeleteStock.as_view(), name='delete_stock'),
    path('stock/<int:pk>/update', views.UpdateStock.as_view(), name='update_stock'),
    # url('', include('pwa.urls')),  # You MUST use an empty string as the URL prefix
    # path('', include('pwa.urls')),


]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

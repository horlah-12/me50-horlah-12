from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings", views.listing, name="listings"),
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("create", views.create_listing, name="create_listing"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("watchlist/add/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist/remove/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("categories", views.categories_view, name="categories"),
    path("category/<str:category_name>", views.category_listings_view, name="category_listings")
    

]

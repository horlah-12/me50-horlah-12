from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from decimal import Decimal, InvalidOperation

from .models import User, Listing, Watchlist, Bid, Comment, Winner


def index(request):
    watchlist_listing_ids = []
    if request.user.is_authenticated:
        watchlist_listing_ids = Watchlist.objects.filter(user=request.user).values_list("listing_id", flat=True)

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True),
        "watchlist_listing_ids": watchlist_listing_ids
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

def listing(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
    })

    

def listing_view(request, listing_id=None):
    if listing_id is None:
        return HttpResponseRedirect(reverse("index"))

    listing = get_object_or_404(Listing, id=listing_id)
    error = None

    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))

        action = request.POST.get("action")

        if action == "bid" and listing.active:
            try:
                bid_amount = Decimal(request.POST["bid_amount"])
            except (InvalidOperation, KeyError):
                error = "Enter a valid bid amount."
            else:
                highest_bid = listing.bids.order_by("-amount").first()
                minimum_bid = highest_bid.amount if highest_bid else listing.starting_bid

                if bid_amount < listing.starting_bid:
                    error = "Your bid must be at least as large as the starting bid."
                elif highest_bid and bid_amount <= highest_bid.amount:
                    error = "Your bid must be greater than the current highest bid."
                else:
                    Bid.objects.create(listing=listing, bidder=request.user, amount=bid_amount)
                    return HttpResponseRedirect(reverse("listing", args=[listing.id]))

        elif action == "close" and listing.owner == request.user and listing.active:
            highest_bid = listing.bids.order_by("-amount").first()
            listing.active = False
            listing.save()

            if highest_bid:
                Winner.objects.update_or_create(
                    listing=listing,
                    defaults={
                        "user": highest_bid.bidder,
                        "amount": highest_bid.amount
                    }
                )

            return HttpResponseRedirect(reverse("listing", args=[listing.id]))

        elif action == "comment":
            content = request.POST.get("comment", "").strip()
            if content:
                Comment.objects.create(listing=listing, commenter=request.user, content=content)
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
            error = "Comment cannot be empty."

    highest_bid = listing.bids.order_by("-amount").first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid
    winner = getattr(listing, "winner", None)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "listing_id": listing_id,
        "highest_bid": highest_bid,
        "current_price": current_price,
        "winner": winner,
        "comments": listing.comments.order_by("-timestamp"),
        "error": error
    })
    

def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    categories = [
        {"id": "Fashion", "name": "Fashion"},
        {"id": "Toys", "name": "Toys"},
        {"id": "Electronics", "name": "Electronics"},
        {"id": "Home", "name": "Home"},
        {"id": "Books", "name": "Books"},
        {"id": "Sports", "name": "Sports"},
        {"id": "Music", "name": "Music"},
        {"id": "Other", "name": "Other"},
    ]

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST.get("image_url", "")
        category = request.POST.get("category", "")

        listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url or None,
            category=category or None,
            owner=request.user,
        )
        listing.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html", {
        "categories": categories
    })


def watchlist_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    return render(request, "auctions/watchlist.html", {
        "listings": Listing.objects.filter(watchlisted_by__user=request.user, active=True)
    })


def add_to_watchlist(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        listing = get_object_or_404(Listing, id=listing_id)
        Watchlist.objects.get_or_create(user=request.user, listing=listing)

    return HttpResponseRedirect(reverse("index"))


def remove_from_watchlist(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        Watchlist.objects.filter(user=request.user, listing_id=listing_id).delete()

    return HttpResponseRedirect(reverse("watchlist"))


def categories_view(request, category_name=None):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.filter(active=True).exclude(category__isnull=True).exclude(category="").values_list("category", flat=True).distinct()
    }) 

def category_listings_view(request, category_name):
    return render(request, "auctions/category_listings.html", {
        "category_name": category_name,
        "listings": Listing.objects.filter(active=True, category=category_name)
    })

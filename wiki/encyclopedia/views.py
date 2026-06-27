from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
import random

from . import util

try:
    import markdown2
    md_available = True
except ImportError:
    md_available = False


def markdown_to_html(markdown_content):
    """Convert markdown to HTML using markdown2 if available, else basic conversion."""
    if md_available:
        return markdown2.markdown(markdown_content)
    else:
        # Basic markdown conversion
        import re
        html = markdown_content
        
        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Links
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        
        # Unordered lists
        html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        html = re.sub(r'</ul>\s*<ul>', '', html)
        
        # Paragraphs
        paragraphs = html.split('\n\n')
        html = '\n'.join([f'<p>{p}</p>' if p.strip() and not p.strip().startswith('<') else p for p in paragraphs])
        
        return html


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    """Display a single encyclopedia entry."""
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found."
        }, status=404)
    
    html_content = markdown_to_html(content)
    
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })


def new(request):
    """Handle creating a new encyclopedia entry."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        
        if not title or not content:
            return render(request, "encyclopedia/new.html", {
                "error": "Title and content are required."
            })
        
        # Check if entry already exists
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/new.html", {
                "error": "An entry with this title already exists."
            })
        
        util.save_entry(title, content)
        return redirect("entry", title=title)
    
    return render(request, "encyclopedia/new.html")


def edit(request, title):
    """Handle editing an encyclopedia entry."""
    entry_content = util.get_entry(title)
    
    if entry_content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found."
        }, status=404)
    
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if not content:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "content": entry_content,
                "error": "Content is required."
            })
        
        util.save_entry(title, content)
        return redirect("entry", title=title)
    
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": entry_content
    })


def search(request):
    """Handle search functionality."""
    query = request.GET.get("q", "").strip()
    
    if not query:
        return redirect("index")
    
    # Check for exact match
    if util.get_entry(query) is not None:
        return redirect("entry", title=query)
    
    # Search for substring matches (case-insensitive)
    all_entries = util.list_entries()
    results = [entry for entry in all_entries if query.lower() in entry.lower()]
    
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results
    })


def random_page(request):
    """Redirect to a random encyclopedia entry."""
    entries = util.list_entries()
    if not entries:
        return redirect("index")
    
    random_entry = random.choice(entries)
    return redirect("entry", title=random_entry)


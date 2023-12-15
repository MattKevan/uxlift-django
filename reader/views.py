from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render, redirect, get_object_or_404
from .forms import SiteForm, PostForm
from django.contrib import messages
from .models import Site, Post, Topic, Tool
from django.views.generic import ListView
from django.http import JsonResponse
from django.views import View
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.db.models import Q, Count
from urllib.parse import urlparse

@login_required
def submit_url(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            existing_site = Site.objects.filter(url=url).first()
            if existing_site:
                messages.error(request, "A site with this URL already exists.")
            else:
                submitted_site = form.save(commit=False)
                submitted_site.user = request.user
                submitted_site.save()  # This will trigger the logic in the model's save method
                messages.success(request, "Thank you for submitting the site. Details have been fetched and saved.")
                return redirect('home')
    else:
        form = SiteForm()
    return render(request, 'reader/submit-site.html', {'form': form})

@login_required
def submit_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            messages.success(request, "Thank you for submitting the post.")
            return redirect('home')  # Redirect to the home page
    else:
        form = PostForm()
    return render(request, 'reader/submit-post.html', {'form': form})


def list_sites(request):
    sites = Site.objects.all()
    return render(request, 'reader/sites.html', {'sites': sites})


class PostListView(ListView):
    model = Post
    template_name = 'pages/home.html'  # replace with your template
    context_object_name = 'posts'
    ordering = ['-date_published']  # '-' indicates descending order
    paginate_by = 50

from django.http import JsonResponse

def refresh_feeds_ajax(request):
    total_sites = Site.objects.filter(status='P').count()
    total_posts = 0
    errors = []

    for site in Site.objects.filter(status='P'):
        try:
            posts_before = Post.objects.filter(site=site).count()
            site.fetch_posts()
            posts_after = Post.objects.filter(site=site).count()
            total_posts += (posts_after - posts_before)
        except Exception as e:
            errors.append(str(e))

    return JsonResponse({
        'total_sites': total_sites,
        'total_posts': total_posts,
        'errors': errors,
    })

# Topics landing page
def topics(request):
    tags = Topic.objects.all()
    return render(request, 'reader/topics.html', {'tags': tags})


def topic_page(request, tag_slug):
    # Retrieve the tag object
    tag = get_object_or_404(Topic, slug=tag_slug)

    # Filter posts by the tag name or slug
    posts_list = Post.objects.filter(topics__name=tag.name)

    # Set up pagination
    paginator = Paginator(posts_list, 20)  # 20 posts per page

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)

    # Filter tools by the tag name or slug
    tools = Tool.objects.filter(topics__name=tag.name)

    return render(request, 'reader/topic-page.html', {
        'posts': posts,
        'tools': tools,
        'tag': tag
    })

# Tools landing page
def tools(request):
    tools = Tool.objects.all().order_by('-date')[:9]
    tags = Topic.objects.annotate(num_tools=Count('tool')).filter(num_tools__gt=0)
    return render(request, 'reader/tools.html', {'tags': tags, 'tools':tools})

# Individual tool page
def tool_page(request, tool_slug):
    tool = get_object_or_404(Tool, slug=tool_slug)
    return render(request, 'reader/tool-page.html', {'tool': tool})
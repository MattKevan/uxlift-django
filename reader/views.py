from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SiteForm, PostForm
from django.contrib import messages
from .models import Site, Post
from django.views.generic import ListView
from django.http import JsonResponse
from django.views import View
import requests
from bs4 import BeautifulSoup

from django.db.models import Q
from .tasks import fetch_posts

@login_required
def submit_url(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            url = form.cleaned_data['url']
            existing_site = Site.objects.filter(Q(title=title) | Q(url=url)).first()
            if existing_site:
                messages.error(request, "A site with this title or URL already exists.")
            else:
                submitted_url = form.save(commit=False)
                submitted_url.user = request.user
                submitted_url.save()
                fetch_posts.delay(submitted_url.id)  # Call the Celery task
                messages.success(request, "Thank you for submitting the URL. Posts are being fetched in the background.")
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

            # get page content
            response = requests.get(new_post.url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # get site title, icon, and published date
            new_post.site_name = soup.find('meta', property='og:site_name')['content'] if soup.find('meta', property='og:site_name') else None
            new_post.site_title = soup.title.string if soup.title else None
            new_post.site_icon = soup.find('link', rel='apple-touch-icon')['href'] if soup.find('link', rel='apple-touch-icon') else None
            new_post.image_path = soup.find('meta', property='og:image')['content'] if soup.find('meta', property='og:image') else None
            new_post.content = soup.find('meta', property='og:description')['content'] if soup.find('meta', property='og:description') else None

            new_post.save()
            messages.success(request, "Thank you for submitting the post.")
            return redirect('home')  # assuming 'home' is the name of your homepage view
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

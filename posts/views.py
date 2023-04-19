from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.cache import cache
from datetime import timedelta


def index(request):
    cache_key = 'index_page'
    posts = cache.get(cache_key)

    if posts is None:
        posts = Post.objects.all().order_by('-pub_date')
        cache.add(cache_key, posts, 20)

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'index.html', {'page': page_obj, 'paginator': paginator})



def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)[:12]
    return render(request, "group.html", {"group": group, "posts": posts})


@login_required
def new_post(request):    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post_get = form.save(commit=False)
            post_get.author = request.user
            post_get.save()
            return redirect('index')    
    form = PostForm()      
    return render(request, 'new.html', {'form': form})  


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(author=user_profile)
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)
    
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=user_profile).exists()
    followers_count = Follow.objects.filter(author=user_profile).count()
    following_count = Follow.objects.filter(user=user_profile).count()
    
    context = {
        "user_profile": user_profile,
        "page": page,
        "paginator": paginator,
        "following": following,
        "followers_count": followers_count,
        "following_count": following_count,
    }
    
    return render(request, "profile.html", context)

 
 
def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm()  # Добавьте эту строку для создания формы комментария
    return render(request, 'post.html', {'post': post, 'form': form})  # Добавьте 'form': form в контекст



@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)

    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
    else:
        form = PostForm(instance=post)

    return render(request, 'post_edit.html', {'form': form, 'post': post})

def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )

def server_error(request):
    return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("post", username=username, post_id=post_id)
    else:
        form = CommentForm()
    
    context = {
        "form": form,
        "post": post,
    }
    return render(request, "add_comment.html", context)

@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    # Добавьте пагинацию
    paginator = Paginator(post_list, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    return render(request, "follow.html", {"page": page, "paginator": paginator})

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username=username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    follow.delete()
    return redirect("profile", username=username)
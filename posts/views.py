from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

def index(request):
        post_list = Post.objects.order_by('-pub_date').all()
        paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.

        page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
        page = paginator.get_page(page_number)  # получить записи с нужным смещением
        return render(
            request,
            'index.html',
            {'page': page, 'paginator': paginator}
       )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)[:12]
    return render(request, "group.html", {"group": group, "posts": posts})


@login_required
def new_post(request):    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post_get = form.save(commit=False)
            post_get.author = request.user
            post_get.save()
            return redirect('index')    
    form = PostForm()      
    return render(request, 'new.html', {'form': form})  


def profile(request, username):
        # тут тело функции
        return render(request, 'profile.html', {})
 
 
def post_view(request, username, post_id):
        # тут тело функции
        return render(request, 'post.html', {})


def post_edit(request, username, post_id):
        # тут тело функции. Не забудьте проверить, 
        # что текущий пользователь — это автор записи.
        # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
        # который вы создали раньше (вы могли назвать шаблон иначе)
        return render(request, 'post_new.html', {})
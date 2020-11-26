from urllib.parse import quote_plus
from django.contrib.sites.shortcuts import get_current_site
from Site.forms import CommentForm, ArticleCreate, UpdatePost
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from Site.models import Article, Comment, NewsLetter
from django.core.mail import EmailMessage
from validate_email import validate_email
from django.views.generic import UpdateView
from django.contrib import messages
from User.views import EmailThread

def proper_pagination(post, index):
    start_index = 0
    end_index = 7
    if post.number > index:
        start_index = post.number - index
        end_index = start_index + end_index
    return (start_index, end_index)


def home(request):
    post_list = Article.published.all().order_by('-id')
    paginator = Paginator(post_list, 6)
    page = request.GET.get('page')
    try:
        post = paginator.page(page)
    except PageNotAnInteger:
        post = paginator.page(1)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)

    if page is None:
        start_index= 0
        end_index = 7
    else:
        (start_index , end_index) = proper_pagination(post, index=4)
    page_range = list(paginator.page_range)[start_index:end_index]
    query = request.GET.get('q')
    authored = Article.objects.filter(Author__username=request.user.username)
    if query:
        post = Article.published.filter(
            Q(title__icontains=query) |
            Q(Author__username__icontains=query)
        )
    context = {
        'post': post,
        'authored_post': authored,
        'page_range':page_range
    }
    return render(request, 'blog/home.html', context)




def post_details(request, id, slug):
    post = Article.objects.get(id=id, slug=slug)
    share_string = quote_plus(post.slug)
    comments = Comment.objects.filter(post=post, reply=None).order_by('id')
    if request.method == 'POST':
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Comment.objects.get(id=reply_id)
            comment = Comment.objects.create(post=post, user=request.user, content=content, reply=comment_qs)
            comment.save()
    else:
        comment_form = CommentForm()
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        is_liked = True
    authored = Article.objects.filter(Author__username=request.user.username)
    context = {
        'post': post,
        'comments': comments,
        'share_string': share_string,
        'comment_form': comment_form,
        'total_likes': post.total_likes(),
        'is_liked': is_liked,
        'authored_post': authored,

    }
    if request.is_ajax():
        html = render_to_string('blog/comment-section.html', context, request=request)
        return JsonResponse({'form': html})
    return render(request, 'blog/article_details.html', context)


def like_photo(request):
    post = get_object_or_404(Article, id=request.POST.get('id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    context = {
        'post': post,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('blog/like-section.html', context, request=request)
        return JsonResponse({'form': html})


def article_create(request):
    if request.user.is_staff or request.user.is_superuser:
        authored = Article.objects.filter(Author__username=request.user.username)
        if request.method == 'POST':
            form = ArticleCreate(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.Author = request.user
                post.save()
                return HttpResponseRedirect(post.get_absolute_url())
        else:
            ArticleCreate()
        form = ArticleCreate()
        context = {
            'form': form,
            'authored_post': authored,
        }
        return render(request, 'blips-create/article-create.html', context)
    return render(request, 'blog/error.html')

class UpdateArticle(UpdateView):
    model = Article
    template_name = 'blips-create/update-article.html'
    form_class = UpdatePost

def delete_post(request, id):
    post = get_object_or_404(Article, id=id)
    if request.user != post.Author:
        return Http404()
    post.delete()
    messages.warning(request, 'deleted successfully')
    return redirect('home')


def newsletter(request):
    context = {
        'has_error': False
    }
    email = request.POST.get('newsletter')
    if not validate_email(email):
        messages.add_message(request, messages.ERROR, 'please provide a valid email..')
        context['has_error'] = True
    if NewsLetter.objects.filter(newsletter=email).exists():
        messages.add_message(request, messages.ERROR, 'email already used  by another user')
        context['has_error'] = True
    if context['has_error']:
        return HttpResponse('')

    letter = NewsLetter.objects.create(newsletter=email)
    from django.core.mail import EmailMultiAlternatives

    subject, from_email, to = 'Subcription to Newsletter', settings.EMAIL_HOST_USER , email
    text_content = 'This is an important message.'
    html_content = '<p>This email has successfully been added to Newsletter, You will recieve notification on new posts <br> <button><a href="https://bitshub.uc.r.appspot.com/">Go To Page</a></button></p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    messages.add_message(request, messages.SUCCESS, 'email successfully added to newsletter section.')
    return HttpResponse('')

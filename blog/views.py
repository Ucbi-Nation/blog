from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponseRedirect
from blog.models import Post, Preference, Category,CommentPreference
from .models import Comments
from users.models import Follow, Profile
from .forms import PostForm,PostFor
import sys
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from .forms import NewCommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def is_users(post_user, logged_user):
    return post_user == logged_user


def ve(request):
    return render(request, 'blog/msg.html')

def test(request):

    return render(request, 'blog/test.html')


def get_author(user):
    qs = Profile.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def get_autho(user):
    qs = User.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


PAGINATION_COUNT = 10


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author') \
                           .annotate(author_count=Count('author')) \
                           .order_by('-author_count')[:6]

        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux['author']).first())
        # if Preference.objects.get(user = self.request.user):
        #     data['preference'] = True
        # else:
        #     data['preference'] = False
        data['preference'] = Preference.objects.all()
        # print(Preference.objects.get(user= self.request.user))
        data['all_users'] = all_users[:6]
        data['all_user'] = Profile.objects.all()[:5]
        data['tag'] = Post.objects.filter(top=1).order_by('-date_posted')
        data['popular'] = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
        data['category'] = Category.objects.all().order_by('-title')[:26]
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        # user = self.request.user
        # qs = Follow.objects.filter(user=user)
        # follows = [user]
        # for obj in qs:
        # follows.append(obj.follow_user)
        return Post.objects.all().order_by('-date_posted')


class ProfileListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/user.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author')\
            .annotate(author_count=Count('author'))\
            .order_by('-author_count')[:6]

        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux['author']).first())
        # if Preference.objects.get(user = self.request.user):
        #     data['preference'] = True
        # else:
        #     data['preference'] = False
        data['preference'] = Preference.objects.all()
        # print(Preference.objects.get(user= self.request.user))
        data['all_users'] = all_users
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)
        follows = [user]
        for obj in qs:
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')


class PostCategory(ListView):
    model = Post, Category
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def category(self):
        return get_object_or_404(Post, category=self.kwargs.get('category'))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author') \
                           .annotate(author_count=Count('author')) \
                           .order_by('-author_count')[:6]

        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux['author']).first())
        # if Preference.objects.get(user = self.request.user):
        #     data['preference'] = True
        # else:
        #     data['preference'] = False
        data['preference'] = Preference.objects.all()
        # print(Preference.objects.get(user= self.request.user))
        data['all_users'] = all_users
        data['all_user'] = Profile.objects.all()[:5]
        data['tag'] = Post.objects.filter(top=1).order_by('-date_posted')
        data['popular'] = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
        data['category'] = Category.objects.all().order_by('title')
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        cat = Category.objects.get(title=self.kwargs.get('category'))
        # user = self.request.user
        # qs = Follow.objects.filter(user=user)
        # follows = [user]
        # for obj in qs:
        # follows.append(obj.follow_user)
        return Post.objects.filter(categories=cat).order_by('-date_posted')



class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/test.html'
    context_object_name = 'posts'
    paginate_by = PAGINATION_COUNT
    form_class = PostFor

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user
        print(logged_user.username == '', file=sys.stderr)

        if logged_user.username == '' or logged_user is None:
            can_follow = False
        else:
            can_follow = (Follow.objects.filter(user=logged_user,
                                                follow_user=visible_user).count() == 0)
        data = super().get_context_data(**kwargs)

        data['user_profile'] = visible_user
        user = self.visible_user()
        data['all_user'] = Profile.objects.all()[:5]
        data['form'] = PostFor(instance=self.request.user)
        data['tag'] = Post.objects.filter(top=1).order_by('-date_posted')
        data['data'] = User.objects.get(username=user)
        data['title'] = 'Create'
        data['popular'] = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
        data['category'] = Category.objects.all().order_by('title')
        data['can_follow'] = can_follow
        return data

    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by('-date_posted')

    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            follows_between = Follow.objects.filter(user=request.user,
                                                    follow_user=self.visible_user())

            if 'follow' in request.POST:
                new_relation = Follow(user=request.user, follow_user=self.visible_user())
                if follows_between.count() == 0:
                    new_relation.save()
            elif 'unfollow' in request.POST:
                if follows_between.count() > 0:
                    follows_between.delete()

        return self.get(self, request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comments.objects.filter(post=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        xx = Post.objects.get(id=self.kwargs.get('pk'))
        data['author_same'] = Post.objects.filter(author=xx.author).order_by('-date_posted').exclude(
            id=self.kwargs.get('pk'))[:3]
        data['form'] = NewCommentForm(instance=self.request.user)
        data['popular'] = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
        data['category'] = Category.objects.all().order_by('title')
        data['tag'] = Post.objects.filter(top=1).order_by('-date_posted')
        data['all_user'] = Profile.objects.all()[:5]
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comments(content=request.POST.get('content'),
                               author=self.request.user,
                               post=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)


def post_single(request, pk,slug):
    post = get_object_or_404(Post, pk=pk)

    allcomments = post.comments.filter(status=True)
    category = Category.objects.all().order_by('title')
    comm = Preference.objects.all()
    page = request.GET.get('page', 1)
    xx = post
    xx.views = xx.views + 1
    xx.save()

    paginator = Paginator(allcomments, 10)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    user_comment = None

    if request.method == 'POST':
        comment_form = NewCommentForm(request.POST,request.FILES)
        author = get_author(request.user)
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False)
            user_comment.name = str(request.user.username)
            user_comment.post = post
            user_comment.author = request.user
            try:
                user_comment.thumbnail = request.FILES["thumbnail"]
                user_comment.save()
            except:
                user_comment.save()
            return HttpResponseRedirect('/post/' + str(pk))
    else:
        comment_form = NewCommentForm()
    popular = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
    all_user = Profile.objects.all()[:5]
    return render(request, 'blog/detail.html',
                  {'post': post, 'comm': comm, 'comments': user_comment, 'category': category, 'comment': comments,
                   'comment_form': comment_form, 'allcomments': allcomments,'popular':popular,'all_user':all_user})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView,):
    model = Post
    template_name = 'blog/post_delete.html'
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['all_user'] = Profile.objects.all()[:5]
        data['tag'] = Post.objects.filter(top=1).order_by('-date_posted')
        data['popular'] = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
        data['category'] = Category.objects.all().order_by('title')
        return data

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView,):
    model = Comments
    template_name = 'blog/comment_delete.html'
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['all_user'] = Profile.objects.all()[:5]
        data['tag'] = Post.objects.filter(top=1).order_by('-date_posted')
        data['popular'] = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
        data['category'] = Category.objects.all().order_by('title')
        return data


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_new.html'
    success_url = '/'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'
        context['category'] = Category.objects.all().order_by('title')
        return context


def post_create(request):
    title = 'Create'
    url = request.META.get('HTTP_REFERER')
    form = PostForm(request.POST or None, request.FILES or None)
    category = Category.objects.all().order_by('title')
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return HttpResponseRedirect(url)
            #return redirect(reverse("/", kwargs={
             #   'id': form.instance.id
            #}))
    context = {
        'title': title,
        'form': form,
        'category': category
    }
    return render(request, "blog/post_new.html", context)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content']
    template_name = 'blog/post_new.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Edit a post'
        data['category'] = Category.objects.all().order_by('title')
        return data


class UpdateComment(LoginRequiredMixin, UserPassesTestMixin, UpdateView,):
    model = Comments
    fields = ['content', 'thumbnail']
    template_name = 'blog/comment.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Edit a comment'
        data['category'] = Category.objects.all().order_by('title')
        return data



class FollowsListView(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['category'] = Category.objects.all().order_by('title')
        data['follow'] = 'follows'
        return data


class FollowersListView(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(follow_user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'followers'
        data['category'] = Category.objects.all().order_by('title')
        return data


# Like Functionality====================================================================================
@login_required
def postpreference(request, postid, userpreference):
    if request.method == "POST":
        eachpost = get_object_or_404(Post, id=postid)
        obj = ''
        valueobj = ''
        try:
            obj = Preference.objects.get(user=request.user, post=eachpost)
            valueobj = obj.value
            valueobj = int(valueobj)
            userpreference = int(userpreference)
            if valueobj != userpreference:
                obj.delete()
                upref = Preference()
                upref.user = request.user
                upref.post = eachpost
                upref.value = userpreference
                if userpreference == 1 and valueobj != 1:
                    eachpost.likes += 1
                    eachpost.dislikes -= 1
                elif userpreference == 2 and valueobj != 2:
                    eachpost.dislikes += 1
                    eachpost.likes -= 1
                upref.save()
                eachpost.save()
                context = {'eachpost': eachpost,
                           'postid': postid}
                return redirect('blog-home')
            elif valueobj == userpreference:
                obj.delete()
                if userpreference == 1:
                    eachpost.likes -= 1
                elif userpreference == 2:
                    eachpost.dislikes -= 1
                eachpost.save()
                context = {'eachpost': eachpost,
                           'postid': postid}
                return redirect('blog-home')

        except Preference.DoesNotExist:
            upref = Preference()
            upref.user = request.user
            upref.post = eachpost
            upref.value = userpreference
            userpreference = int(userpreference)
            if userpreference == 1:
                eachpost.likes += 1
            elif userpreference == 2:
                eachpost.dislikes += 1
            upref.save()
            eachpost.save()

            context = {'post': eachpost,
                       'postid': postid}

            return redirect('blog-home')

    else:
        eachpost = get_object_or_404(Post, id=postid)
        context = {'eachpost': eachpost,
                   'postid': postid}

        return redirect('blog-home')




# Comment Like Functionality====================================================================================
@login_required
def commentpreference(request, postid, userpreference):
    url = request.META.get('HTTP_REFERER')  # get last url
    if request.method == "POST":
        eachpost = get_object_or_404(Comments, id=postid)
        obj = ''
        valueobj = ''
        try:
            obj = CommentPreference.objects.get(user=request.user, post=eachpost)
            valueobj = obj.value
            valueobj = int(valueobj)
            userpreference = int(userpreference)
            if valueobj != userpreference:
                obj.delete()
                upref = Preference()
                upref.user = request.user
                upref.post = eachpost
                upref.value = userpreference
                if userpreference == 1 and valueobj != 1:
                    eachpost.likes += 1
                    eachpost.dislikes -= 1
                elif userpreference == 2 and valueobj != 2:
                    eachpost.dislikes += 1
                    eachpost.likes -= 1
                upref.save()
                eachpost.save()
                context = {'eachpost': eachpost,
                           'postid': postid}
                return HttpResponseRedirect(url)
            elif valueobj == userpreference:
                obj.delete()
                if userpreference == 1:
                    eachpost.likes -= 1
                elif userpreference == 2:
                    eachpost.dislikes -= 1
                eachpost.save()
                context = {'eachpost': eachpost,
                           'postid': postid}
                return HttpResponseRedirect(url)

        except CommentPreference.DoesNotExist:
            upref = CommentPreference()
            upref.user = request.user
            upref.post = eachpost
            upref.value = userpreference
            userpreference = int(userpreference)
            if userpreference == 1:
                eachpost.likes += 1
            elif userpreference == 2:
                eachpost.dislikes += 1
            upref.save()
            eachpost.save()

            context = {'post': eachpost,
                       'postid': postid}

            return HttpResponseRedirect(url)

    else:
        eachpost = get_object_or_404(Post, id=postid)
        context = {'eachpost': eachpost,
                   'postid': postid}

        return HttpResponseRedirect(url)

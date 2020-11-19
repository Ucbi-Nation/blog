from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404, JsonResponse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Count
from django.contrib.auth.models import User
from users.models import Follow, Profile
from blog.models import Post, Preference, Category,CommentPreference
from users.models import Follow
import sys

from django.shortcuts import render,get_object_or_404

from .forms import ChannelMessageForm
from .models import Channel, ChannelMessage,ChannelUser

def is_users(post_user, logged_user):
    return post_user == logged_user


class ChannelFormMixin(FormMixin):
    form_class = ChannelMessageForm
    # success_url = './'
    def get_success_url(self):
        return self.request.path
    # handle the form with this mixin
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        form = self.get_form()
        if form.is_valid():
            channel = self.get_object()
            user = self.request.user
            content = form.cleaned_data.get("content")
            channel_obj = ChannelMessage.objects.create(channel=channel, user=user, content=content)
            if request.is_ajax():
                # Django Rest Framework
                return JsonResponse({"content": channel_obj.content, "username": channel_obj.user.username }, status=201)
            return super().form_valid(form)
        else:
            if request.is_ajax():
                return JsonResponse({"errors": form.errors}, status=400)
            return super().form_invalid(form)



class ChannelDetailView(LoginRequiredMixin, ChannelFormMixin, DetailView):
    template_name = 'dm/private_message.html'
    queryset = Channel.objects.all()
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        obj = context['object']
        # if self.request.user not in obj.users.all():
        #     raise PermissionDenied
        context['is_channel_member'] = self.request.user in obj.users.all()
        return context

    # def get_queryset(self):
    #     user = self.request.user # definitely a user
    #     username = user.username
    #     qs = Channel.objects.all().filter_by_username(username)
    #     return qs

class PrivateMessageDetailView(LoginRequiredMixin, ChannelFormMixin, DetailView):
    model = ChannelUser
    context_object_name = 'posts'
    template_name = 'dm/messenger.html'
    # def get_template_names(self, *args, **kwargs):
    #     return ['dm/private_message.html']

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get("username")
        my_username = self.request.user.username
        if username == my_username:
            my_channel_obj, _ = Channel.objects.get_or_create_current_user_private_message(self.request.user)
            return my_channel_obj
        channel_obj, _ = Channel.objects.get_or_create_private_message(my_username, username)
        if channel_obj == None:
            raise Http404
        return channel_obj

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))


 #   def test_func(self):
  #      print(str(self.kwargs.get("username")))
        #xx=ChannelUser.objects.get(user=self.kwargs.get("username"))

   #     return is_users(get_object_or_404(User,username=self.kwargs.get("username")), self.request.user)


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
        user = self.visible_user()
        xxx= Follow.objects.filter(user=user).order_by('-date')
        user = User.objects.get(username=self.kwargs.get("username"))
        data['follow'] = Follow.objects.filter(follow_user=self.request.user)
        count = Follow.objects.filter(follow_user=self.request.user).count()
        if count <=10:
            data['others'] = Profile.objects.all()[:10-count]
        data['messengers'] = ChannelUser.objects.filter(user=user)
        # print(Preference.objects.get(user= self.request.user))
        data['all_users'] = all_users[:6]
        username = self.kwargs.get("username")
        my_username = self.request.user.username
        data['id_search'] = Channel.objects.filter(users=my_username and user).first()
        id_channel = Channel.objects.filter(users=my_username and user).first()
        data['ids']=ChannelMessage.objects.filter(channel=id_channel).count()
        #ch_u_a = ChannelUser(user=user_a, channel=channel_obj)
        #ch_u_b = ChannelUser(user=user_b, channel=channel_obj)
        #ChannelUser.objects.bulk_create([ch_u_a, ch_u_b])
        data['all_user'] = Profile.objects.all()[:5]
        data['user'] = Profile.objects.get(user=user)
        data['username'] = self.kwargs.get("username")
        data['tag'] = Post.objects.filter(top=1).order_by('-date_posted')
        data['popular'] = Post.objects.filter().order_by('-views').order_by('-date_posted')[:7]
        data['category'] = Category.objects.all().order_by('-title')[:26]
        print(all_users, file=sys.stderr)
        return data

# Create your views here.
def private_message_view(request, username, *args, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponse("Nope..")
    my_username = request.user.username
    channel_obj, created = Channel.objects.get_or_create_private_message(my_username, username)
    if created:
        print("yes it was")
    channel_users = channel_obj.channeluser_set.all().values("user__username")
    print(channel_users)
    channel_messages = channel_obj.channelmessage_set.all()
    print(channel_messages.values("content"))
    return HttpResponse(f"channel items - {channel_obj.id}")
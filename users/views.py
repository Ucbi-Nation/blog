from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from blog.models import Post,Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

PAGINATION_COUNT = 10

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    category = Category.objects.all().order_by('title')
    return render(request, 'users/signup.html', {'form': form,'category': category})


@login_required
def profile(request):
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, f'Account has been updated.')
            return redirect('profile')
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user.profile)
    category = Category.objects.all().order_by('title')
    return render(request, 'users/profile.html', {'uform': uform, 'pform': pform, 'category': category})


@login_required
def SearchView(request):
    if request.method == 'POST':
        paginate_by = PAGINATION_COUNT
        kerko = request.POST.get('search')
        print(kerko)
        results = Post.objects.filter(title__contains=kerko, content__contains=kerko)
        page = request.GET.get('page', 1)
        result = User.objects.filter(username__contains=kerko)
        paginator = Paginator(results, 4)
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)
        category = Category.objects.all().order_by('title')
        context = {
            'results': results,
            'result': result,
            'category': category,
            'comment': comments,

        }
        return render(request, 'users/search_result.html', context)

#@login_required
#def SearchView(request):
#    if request.method == 'POST':
 #       kerko = request.POST.get('search')
  #      print(kerko)
   #     results = User.objects.filter(username__contains=kerko)
    #    context = {
     #       'results':results
      #  }
    #else:
     #   kerko = request.POST.get('search')
      #  print(kerko)
       # results = None
        #context={
         #   'results':results
        #}
        #return render(request, 'users/search_result.html', context)-->

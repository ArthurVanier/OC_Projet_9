from django.shortcuts import render, redirect
from .forms import login_form, sign_up_form, ticket_form, subscription_form, review_form, review_to_ticket_form
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Ticket, UserFollows, Review
from django.core.exceptions import ObjectDoesNotExist
from operator import attrgetter
from django.core.files.uploadedfile import SimpleUploadedFile


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = login_form()
    return render(request, 'index.html', {'form': form})


def login_process(request):
    if request.method == "POST":
        form = login_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('dashboard')
    return redirect('index')


def dashboard(request):
    if request.user.is_authenticated:
        follow_list = UserFollows.objects.filter(user=request.user)

        review_list = [review for review in Review.objects.filter(user=request.user).order_by('-time_created')[:5]]
        ticket_list = [ticket for ticket in Ticket.objects.filter(user=request.user).order_by('-time_created')[:5]]
        for follow in follow_list:
            review_list = review_list + [review for review in Review.objects.filter(user=follow.followed_user).order_by('-time_created')[:5]]
            ticket_list = ticket_list + [ticket for ticket in Ticket.objects.filter(user=follow.followed_user).order_by('-time_created')[:5]]

        review_list.sort(key=attrgetter('time_created'), reverse=True)
        review_list = review_list[:5]
        ticket_list.sort(key=attrgetter('time_created'), reverse=True)
        ticket_list = ticket_list[:5]

        for review in review_list:
            for index in range(len(ticket_list)):
                if review.ticket.id == ticket_list[index].id:
                    del ticket_list[index]
                    break

        final_list = review_list + ticket_list
        final_list.sort(key=attrgetter('time_created'), reverse=True)

        for post in final_list:
            if post.TYPE == 'ticket':
                try:
                    Review.objects.get(ticket=post)
                    post.HAS_REVIEW = True
                except ObjectDoesNotExist:
                    pass
        return render(request, 'dashboard.html', {'post_list': final_list[:5]})
    return redirect('index')


def sign_up(request):
    form = sign_up_form()
    return render(request, 'sign_up.html', {'form': form})


def sign_up_process(request):
    if request.method == 'POST':
        form = sign_up_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if User.objects.filter(username=username).count() == 0 and User.objects.filter(password=password).count() == 0:
                email = form.cleaned_data['email']
                user = User(username=username, email=email)
                user.set_password(password)
                user.save()
                return redirect('index')
    return redirect('sign_up')


def logout_process(request):
    logout(request)
    return redirect('index')


def create_ticket(request):
    form = ticket_form()
    return render(request, 'create_ticket.html', {'form': form})


def create_ticket_process(request):
    if request.method == 'POST':
        form = ticket_form(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            image = form.cleaned_data['image']
            user = request.user
            ticket = Ticket(title=title, description=description, image=image, user=user)
            ticket.save()
            return redirect('dashboard')
    return redirect('create_ticket')


def subscription(request):
    form = subscription_form()
    follow_list = UserFollows.objects.filter(user=request.user)
    follower_list = UserFollows.objects.filter(followed_user=request.user)
    return render(request, 'subscription.html', {'form': form, 'follow_list': follow_list, 'follower_list': follower_list})


def subscription_process(request):
    if request.method == 'POST':
        form = subscription_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                followed_user = User.objects.get(username__iexact=username)
                if username != request.user.username:
                    UserFollows(user=request.user, followed_user=followed_user).save()
                else:
                    print("meme user")
            except ObjectDoesNotExist:
                print("User dosnt exist")
    return redirect('subscription')


def create_review(request, ticket_id=-1):
    form = None
    data = {'ticket_id': ticket_id}
    if ticket_id != -1:
        ticket = Ticket.objects.get(pk=ticket_id)
        data['is_awsner'] = True
        data['title'] = ticket.title
        data['description'] = ticket.description
        data['image'] = ticket.image
        data['username'] = ticket.user.username
        data['time_created'] = ticket.time_created
        form = review_to_ticket_form()
    else:
        data['is_awsner'] = False
        form = review_form()
    return render(request, 'create_review.html', {"form": form, "data": data})


def create_review_process(request, ticket_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.__contains__('title'):
                form = review_form(request.POST, request.FILES)
                if form.is_valid():
                    title = form.cleaned_data['title']
                    description = form.cleaned_data['description']
                    image = form.cleaned_data['image']
                    headline = form.cleaned_data['headline']
                    body = form.cleaned_data['body']
                    rating = int(form.cleaned_data['rating'][0])
                    try:
                        Ticket.objects.get(title=title)
                        print('Ticket already exist')
                    except ObjectDoesNotExist:
                        ticket = Ticket.objects.create(title=title, description=description, image=image, user=request.user)
                        Review.objects.create(ticket=ticket, headline=headline, body=body, rating=rating, user=request.user)
                        return redirect('dashboard')
            else:
                form = review_to_ticket_form(request.POST)
                if form.is_valid():
                    headline = form.cleaned_data['headline']
                    body = form.cleaned_data['body']
                    rating = int(form.cleaned_data['rating'][0])

                    ticket = Ticket.objects.get(pk=ticket_id)
                    Review.objects.create(ticket=ticket, headline=headline, body=body, rating=rating, user=request.user)
                    return redirect('dashboard')
    return redirect('create_review', ticket_id=ticket_id)


def my_post(request):
    post_list = []
    if request.user.is_authenticated:
        ticket_list = Ticket.objects.filter(user=request.user)
        review_list = Review.objects.filter(user=request.user)

    post_list = [ticket for ticket in ticket_list] + [review for review in review_list]
    post_list.sort(key=attrgetter('time_created'), reverse=True)
    return render(request, 'my_post.html', {'post_list': post_list})


def modify_post(request, post_type, post_id):
    form = None
    data = {'post_type': post_type, 'post_id': post_id}
    if post_type == 'ticket':
        try:
            print("Je modifi un ticket")
            ticket = Ticket.objects.get(pk=post_id)

            photo = open(ticket.image.path, 'rb')
            file_data = {'image': SimpleUploadedFile(photo.name, photo.read())}
            form = ticket_form({'title': ticket.title, 'description': ticket.description, "image": file_data})
            data['image'] = ticket.image
        except ObjectDoesNotExist:
            pass
    else:
        try:
            review = Review.objects.get(pk=post_id)
            form = review_to_ticket_form({
                'headline': review.headline,
                'body': review.body,
                'rating': review.rating
            })
            data['title'] = review.ticket.title
            data['description'] = review.ticket.description
            data['image'] = review.ticket.image
        except ObjectDoesNotExist:
            pass
    print(form.fields['image'])
    return render(request, 'modify_post.html', {'form': form, 'data': data})


def modify_post_process(request, post_type, post_id):
    if request.method == "POST":
        if post_type == 'ticket':
            ticket = Ticket.objects.get(pk=post_id)
            form = ticket_form(request.POST, request.FILES)
            if form.is_valid():
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                image = form.cleaned_data['image']

                ticket.title = title
                ticket.description = description
                ticket.image = image

                ticket.save()
        else:
            review = Review.objects.get(pk=post_id)
            form = review_to_ticket_form(request.POST, request.FILES)
            if form.is_valid():
                headline = form.cleaned_data['headline']
                body = form.cleaned_data['body']
                rating = form.cleaned_data['rating']

                review.headline = headline
                review.body = body
                review.rating = rating
                review.save()

    return redirect('my_post')


def delete_post_process(request, post_type, post_id):
    if post_type == 'ticket':
        ticket = Ticket.objects.get(pk=post_id)
        ticket.delete()
    else:
        review = Review.objects.get(pk=post_id)
        review.delete()

    return redirect('my_post')

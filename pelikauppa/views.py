from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Game, GameOwnerships, Purchase
from .forms import UserForm, UserProfileForm, GameForm
from django.template import RequestContext
from django.core import mail
from django.contrib.auth.models import User
from hashlib import md5
from django.urls import reverse
import json
from datetime import datetime

# The main page of the website.
def index(request):
    return render(request, template_name='pelikauppa/index.html')

# The general error message used in miscellaneous situations.
def general_error(request):
    return render(request, template_name='pelikauppa/general_error.html')

# User registration.
def register(request):
    if request.method == 'POST':
        userform = UserForm(request.POST, prefix='user')
        profileform = UserProfileForm(request.POST, prefix='userprofile')

        if (userform.is_valid() and profileform.is_valid and
                userform.cleaned_data['password'] == userform.cleaned_data[
                    'confirm_password']):
            user = userform.save(commit=False)
            user.set_password(userform.cleaned_data['password'])
            user.is_active = False
            user.save()
            userprofile = profileform.save(commit=False)
            userprofile.user = user
            userprofile.save()

            # Send confirmation email
            with mail.get_connection() as connection:
                confirmation_link = 'http://' + str(request.get_host()) + str(reverse('pelikauppa:activate', args=[user.pk]))
                mail.EmailMessage('Tunnuksen aktivointi', confirmation_link,
                'pelikauppa@pelikauppa.com', [user.email],
                connection=connection).send()

            return render(request, 'pelikauppa/message.html',
                    dict(message='Rekisteröinti onnistui. Aktivoi tili sähköpostiin tulleella vahvistuslinkillä.'))
    else:
        userform = UserForm(prefix='user')
        profileform = UserProfileForm(prefix='userprofile')

    return render(request, 'pelikauppa/register.html',
            dict(userform=userform,userprofileform=profileform))

# The user account activation (mockup, doesn't actually use an email activation)
def activate(request, key):
    user = get_object_or_404(User, pk=key)
    if user.is_active == False:
        user.is_active = True
        user.save()

    return render(request, 'pelikauppa/message.html',
            dict(message='Aktivointi onnistui, voit nyt kirjautua sisään.'))


# Checks whether user logging in has a valid credentials and whether they are
# a player or a developer.
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.profile.is_developer:
                    return redirect(reverse('pelikauppa:developer_add_game'))
                else:

                    return redirect(reverse('pelikauppa:add_game_to_player'))

            else:
                # Error message for disabled account
                pass
    return render(request, template_name='pelikauppa/login.html')

def logout_user(request):
    logout(request)
    return redirect(reverse('pelikauppa:index'))

# The page where the individual games are played.
def game_view(request):
    return render(request, template_name='pelikauppa/game_view.html')

# Called when an user saves their data from within the JavaScript game.
def save_game_data(request):
    if request.method == 'POST':

        query_dict = request.POST


        json_msg = query_dict['json_msg']
        json_to_dict = json.loads(json_msg)
        game_url = json_to_dict['gameURL']
        curr_user_name = json_to_dict['currUser']
        curr_user = User.objects.get(username=curr_user_name)
        curr_game = Game.objects.get(url=game_url)
        curr_ownership = GameOwnerships.objects.get(game=curr_game, gameOwner=curr_user)

        curr_ownership.data = json_msg

        curr_ownership.save()

        return HttpResponse('Success')

# Used when user loads data.
def load_game_data(request):

    if request.method == 'GET':

        query_dict = request.GET
        game_url = query_dict['gameURL']
        curr_user_name = query_dict['currUser']
        curr_user = User.objects.get(username=curr_user_name)
        curr_game = Game.objects.get(url=game_url)
        curr_ownership = GameOwnerships.objects.get(game=curr_game, gameOwner=curr_user)


        if (curr_ownership.data != None):
            return HttpResponse(curr_ownership.data)

        return HttpResponse('empty')

# Called when user submits their score.
def submit_high_score(request):
    if request.method == 'POST':
        query_dict = request.POST

        game_url = query_dict['gameURL']
        curr_user_name = query_dict['currUser']
        curr_user = User.objects.get(username=curr_user_name)
        curr_game = Game.objects.get(url=game_url)
        curr_ownership = GameOwnerships.objects.get(game=curr_game, gameOwner=curr_user)
        if (curr_ownership.high_score is None or float(query_dict['score']) > curr_ownership.high_score):
            curr_ownership.high_score = float(query_dict['score'])
            curr_ownership.save()
        return HttpResponse('Success')

# Developer basic page. Has functionality to add new games or remove existing ones.
def developer_add_game(request):
    if not request.user.profile.is_developer:
        return general_error(request)

    if request.method == 'POST':
        game_form = GameForm(request.POST, prefix='game')

        if (game_form.is_valid()):
            game = game_form.save(commit=False)
            game.developer = request.user
            game.save()
            return render(request, 'pelikauppa/message.html',
                    dict(message='Peli lisätty.'))
    else:
        game_form = GameForm(prefix='game')
    dev_game_list = Game.objects.filter(developer=request.user)
    return render(request, 'pelikauppa/developer_add_game.html',
            dict(gameform=game_form, devgamelist=dev_game_list))

# Called when a developer removes their game.
def developer_remove_game(request):
    if not request.user.profile.is_developer:
        return general_error(request)

    if request.method == 'POST':
        game_to_be_removed = Game.objects.get(pk=request.POST.get('selected_game'))
        game_to_be_removed.delete()

        return developer_add_game(request)

    else:
        return general_error(request)


# Player list view of all games and all player's games.
def player_starting_view(request):
    store_game_list = Game.objects.all()
    player_game_list = []
    if request.user.is_authenticated:
        player_game_ownerships = GameOwnerships.objects.filter(gameOwner=request.user)
        for ownership in player_game_ownerships:
            player_game_list.append(ownership.game)
    return render(request, 'pelikauppa/game_list.html',
                  dict(allgames=store_game_list, playergames=player_game_list))

# Adds a game to player's game library.
def add_game_to_player(request):
    if request.method == 'POST':
        ownership = GameOwnerships()
        ownership.gameOwner = request.user

        ownership.game = Game.objects.get(name=request.POST.get('selected_game'))
        ownership.save()

        purchase = Purchase()
        purchase.game = Game.objects.get(name=request.POST.get('selected_game'))
        purchase.time = datetime.now()
        purchase.save()

    return player_starting_view(request)

# Opens the single game view where the game is played.
def open_game_view(request):
    game_url = request.POST.get('selected_game_url')

    curr_game = Game.objects.get(url=game_url)
    game_ownerships = GameOwnerships.objects.filter(game=curr_game)

    high_score_list = []
    for ownership in game_ownerships:
        item = { 'name': ownership.gameOwner,
            'highscore': ownership.high_score }
        if ownership.high_score is not None:
            high_score_list.append(item)
    high_score_list.sort(key=lambda value: value['highscore'], reverse=True)

    return render(request, 'pelikauppa/game_view.html', dict(gameurl=game_url, curruser=request.user,
                                                                highscores=high_score_list))


# Handles the purchase.
def purchase(request):
    if not request.user.is_authenticated:
        return redirect(reverse('pelikauppa:login_user'))
    #if request.method == 'POST':
    #pid = "ostos1"
    sid = "wsd17kevat17"
    game = Game.objects.get(pk=request.POST.get('selected_game'))
    pid = str(game.name)
    amount = str(game.price)
    #amount = "50"
    secret_key = "abd51612a6c33bd3828e92a5f64f93f2"
    checksumstr = "pid={}&sid={}&amount={}&token={}".format(pid, sid, amount, secret_key)
    # checksumstr is the string concatenated above
    m = md5(checksumstr.encode("ascii"))
    checksum = m.hexdigest()
    # checksum is the value that should be used in the payment request
    return render(request, "pelikauppa/purchase.html",
            {'pid':pid, 'sid':sid, 'amount':amount, 'checksum':checksum})

def purchase_cancel(request):
    return render(request, 'pelikauppa/purchase_cancel.html')

def purchase_error(request):
    return render(request, 'pelikauppa/purchase_error.html')

# Called if the payment service OK's the payment. Checksum is checked here.
def purchase_success(request):
    pid = request.GET.get('pid')
    ref = request.GET.get('ref')
    result = request.GET.get('result')
    checksum = request.GET.get('checksum')
    secret_key = "abd51612a6c33bd3828e92a5f64f93f2"
    checksumstr = "pid={}&ref={}&result={}&token={}".format(pid, ref, result, secret_key)
    m = md5(checksumstr.encode("ascii"))
    checksum2 = m.hexdigest()
    if checksum == checksum2:
        return render(request, 'pelikauppa/purchase_success.html', {'pid':pid})
    else:
        return render(request, 'pelikauppa/purchase_error.html')

# Handles the sales data.
def game_sales(request):
    this_game_purchases = []
    if request.user.is_authenticated:
        this_game = Game.objects.get(pk=request.POST.get('selected_game'))
        this_game_purchases = Purchase.objects.filter(game=this_game)


    return render(request, 'pelikauppa/game_sales.html',
                  {'list':this_game_purchases})

from django.conf.urls import url
from . import views

app_name = 'pelikauppa'

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register, name='register'),
        url(r'^activate/(?P<key>.+)$', views.activate, name='activate'),
        url(r'^login_user/$', views.login_user, name='login_user'),
        url(r'^logout_user/$', views.logout_user, name='logout_user'),
        url(r'^developer_add_game/$', views.developer_add_game, name='developer_add_game'),
        url(r'^developer_remove_game/$', views.developer_remove_game, name='developer_remove_game'),
        url(r'^game_view/$', views.game_view, name='game_view'),
        url(r'^save_game_data/$', views.save_game_data, name='save_game_data'),
        url(r'^load_game_data/$', views.load_game_data, name='load_game_data'),
        url(r'^submit_high_score/$', views.submit_high_score, name='submit_high_score'),
        url(r'^add_game_to_player/$', views.add_game_to_player, name='add_game_to_player'),
        url(r'^open_game_view/$', views.open_game_view, name='open_game_view'),
        url(r'^player_starting_view/$', views.player_starting_view, name='player_starting_view'),
        url(r'^purchase/$', views.purchase, name='purchase'),
        url(r'^purchase_success/', views.purchase_success, name='purchase_success'),
        url(r'^purchase_cancel/$', views.purchase_cancel, name='purchase_cancel'),
        url(r'^purchase_error/$', views.purchase_error, name='purchase_error'),
        url(r'^general_error/$', views.general_error, name='general_error'),
        url(r'^game_sales/$', views.game_sales, name='game_sales'),
        ]

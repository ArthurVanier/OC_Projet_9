from django.urls import path, register_converter

from . import views 

class NegativeIntConverter:
    regex = '-?\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%d' % value

register_converter(NegativeIntConverter, 'negint')

urlpatterns = [
    path('', views.index, name='index'),
    path('login_process',views.login_process,name='login_process'),
    path('dashboard',views.dashboard, name='dashboard'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('sign_up_process', views.sign_up_process, name='sign_up_process'),
    path('logout_process', views.logout_process, name='logout_process'),
    path('create_ticket', views.create_ticket, name='create_ticket'),
    path('create_ticket_process', views.create_ticket_process, name='create_ticket_process'),
    path('subscription', views.subscription, name='subscription'),
    path('subscription_process', views.subscription_process, name='subscription_process'),
    path('create_review/<negint:ticket_id>', views.create_review, name='create_review'),
    path('create_review_process/<negint:ticket_id>', views.create_review_process, name="create_review_process"),
    path('my_post', views.my_post, name='my_post'),
    path('modify_post/<str:post_type>/<int:post_id>',views.modify_post,name='modify_post'),
    path('modify_post_process/<str:post_type>/<int:post_id>',views.modify_post_process,name='modify_post_process'),
    path('delete_post_process/<str:post_type>/<int:post_id>',views.delete_post_process,name='delete_post_process'),
]



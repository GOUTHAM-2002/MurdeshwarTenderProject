from django.urls import path, re_path

from vendors import views
from vendors.views import register, login, index, home
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('project_list/', views.project_list, name='project_list'),
    path('home/', home, name='home'),
    path('project/create/', views.project_create, name='project_create'),
    path('project/edit/', views.project_update, name='project_update'),
    path('project/delete/', views.project_delete, name='project_delete'),
    path('register/', register, name='register'),
    path('login/', login, name='login_user'),
    path('', index, name='index'),
    path('tender/create/', views.create_tender, name='create_tender'),
    path('tender/<int:tender_id>/update/', views.update_tender, name='update_tender'),
    path('tender/<int:tender_id>/delete/', views.delete_tender, name='delete_tender'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]

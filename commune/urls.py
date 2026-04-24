from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "commune"

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.register, name="register"),
    path("connexion/", views.CommuneLoginView.as_view(), name="login"),
    path(
        "deconnexion/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("publication/<slug:slug>/", views.publication_detail, name="publication_detail"),
    path("publication/<slug:slug>/like/", views.toggle_like, name="toggle_like"),
    path("publication/<slug:slug>/commenter/", views.add_comment, name="add_comment"),
    path("notifications/", views.notification_list, name="notifications"),
    path(
        "notifications/lues/",
        views.notifications_mark_all_read,
        name="notifications_mark_all_read",
    ),
    path(
        "notifications/<int:pk>/lue/",
        views.notification_mark_read,
        name="notification_mark_read",
    ),
    path("admin-commune/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-commune/utilisateurs/", views.admin_users, name="admin_users"),
    path("admin-commune/publication/nouvelle/", views.admin_publication_create, name="admin_publication_create"),
    path(
        "admin-commune/publication/<slug:slug>/modifier/",
        views.admin_publication_edit,
        name="admin_publication_edit",
    ),
    path(
        "admin-commune/publication/<slug:slug>/supprimer/",
        views.admin_publication_delete,
        name="admin_publication_delete",
    ),
    path(
        "admin-commune/commentaire/<int:pk>/visibilite/",
        views.admin_comment_toggle_visibility,
        name="admin_comment_toggle_visibility",
    ),
    path(
        "admin-commune/utilisateur/<int:pk>/actif/",
        views.admin_user_toggle_active,
        name="admin_user_toggle_active",
    ),
]

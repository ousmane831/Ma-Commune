from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    BootstrapAuthenticationForm,
    CitizenRegistrationForm,
    CommentForm,
    PublicationForm,
)
from .models import Comment, Like, Notification, Publication, User


def home(request):
    qs = Publication.objects.filter(is_published=True).select_related("author")
    return render(request, "commune/home.html", {"publications": qs})


def publication_detail(request, slug):
    publication = get_object_or_404(
        Publication.objects.select_related("author"),
        slug=slug,
        is_published=True,
    )
    is_admin = request.user.is_authenticated and request.user.is_commune_admin
    top = publication.comments.filter(parent__isnull=True).select_related("author")
    if not is_admin:
        top = top.filter(is_visible=True)
    comments = top.prefetch_related("replies", "replies__author")
    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(user=request.user, publication=publication).exists()
    like_count = publication.likes.count()
    comment_form = CommentForm() if request.user.is_authenticated else None
    abs_url = request.build_absolute_uri(publication.get_absolute_url())
    return render(
        request,
        "commune/publication_detail.html",
        {
            "publication": publication,
            "comments": comments,
            "liked": liked,
            "like_count": like_count,
            "comment_form": comment_form,
            "is_admin": is_admin,
            "share_url": abs_url,
            "share_title": publication.title,
        },
    )


@require_POST
@login_required
def toggle_like(request, slug):
    publication = get_object_or_404(Publication, slug=slug, is_published=True)
    like, created = Like.objects.get_or_create(user=request.user, publication=publication)
    if not created:
        like.delete()
        messages.info(request, "J'aime retiré.")
    else:
        messages.success(request, "Merci pour votre soutien !")
        if publication.author_id and publication.author_id != request.user.id:
            Notification.objects.create(
                recipient_id=publication.author_id,
                notification_type=Notification.TYPE_LIKE,
                message=f"{request.user.get_username()} a aimé votre publication « {publication.title[:80]} ».",
                link=publication.get_absolute_url(),
                related_publication=publication,
            )
    return redirect("commune:publication_detail", slug=slug)


@require_POST
@login_required
def add_comment(request, slug):
    publication = get_object_or_404(Publication, slug=slug, is_published=True)
    form = CommentForm(request.POST)
    parent_id = request.POST.get("parent")
    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, pk=parent_id, publication=publication)
    if form.is_valid():
        c = form.save(commit=False)
        c.publication = publication
        c.author = request.user
        c.parent = parent
        c.save()
        messages.success(request, "Commentaire publié.")
    else:
        messages.error(request, "Le commentaire est invalide.")
    return redirect("commune:publication_detail", slug=slug)


def register(request):
    if request.user.is_authenticated:
        return redirect("commune:home")
    if request.method == "POST":
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Bienvenue sur la plateforme de la commune de Niakhar.")
            return redirect("commune:home")
    else:
        form = CitizenRegistrationForm()
    return render(request, "commune/register.html", {"form": form})


class CommuneLoginView(LoginView):
    template_name = "commune/login.html"
    authentication_form = BootstrapAuthenticationForm


@login_required
def notification_list(request):
    qs = request.user.notifications.all()[:100]
    return render(request, "commune/notifications.html", {"notifications": qs})


@require_POST
@login_required
def notifications_mark_all_read(request):
    now = timezone.now()
    request.user.notifications.filter(read_at__isnull=True).update(read_at=now)
    messages.success(request, "Toutes les notifications sont marquées comme lues.")
    next_url = request.POST.get("next") or reverse("commune:notifications")
    return HttpResponseRedirect(next_url)


@require_POST
@login_required
def notification_mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not n.read_at:
        n.read_at = timezone.now()
        n.save(update_fields=["read_at"])
    link = n.link or reverse("commune:home")
    return HttpResponseRedirect(link)


def _admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_commune_admin:
            return HttpResponseForbidden("Accès réservé aux administrateurs.")
        return view_func(request, *args, **kwargs)

    return wrapper


@_admin_required
def admin_users(request):
    users = User.objects.annotate(pub_count=Count("publications")).order_by("-date_joined")
    return render(request, "commune/admin_users.html", {"users": users})


@_admin_required
def admin_dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    stats = {
        "users_total": User.objects.count(),
        "publications_total": Publication.objects.count(),
        "comments_total": Comment.objects.count(),
        "likes_total": Like.objects.count(),
        "users_week": User.objects.filter(date_joined__gte=week_ago).count(),
        "comments_week": Comment.objects.filter(created_at__gte=week_ago).count(),
        "publications_week": Publication.objects.filter(created_at__gte=week_ago).count(),
    }
    recent_comments = (
        Comment.objects.select_related("author", "publication")
        .order_by("-created_at")[:15]
    )
    return render(
        request,
        "commune/admin_dashboard.html",
        {"stats": stats, "recent_comments": recent_comments},
    )


@_admin_required
def admin_publication_create(request):
    if request.method == "POST":
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.author = request.user
            pub.save()
            messages.success(request, "Publication créée.")
            return redirect(pub.get_absolute_url())
    else:
        form = PublicationForm()
    return render(request, "commune/admin_publication_form.html", {"form": form, "title": "Nouvelle publication"})


@_admin_required
def admin_publication_edit(request, slug):
    publication = get_object_or_404(Publication, slug=slug)
    if request.method == "POST":
        form = PublicationForm(request.POST, request.FILES, instance=publication)
        if form.is_valid():
            form.save()
            messages.success(request, "Publication mise à jour.")
            return redirect(publication.get_absolute_url())
    else:
        form = PublicationForm(instance=publication)
    return render(
        request,
        "commune/admin_publication_form.html",
        {"form": form, "title": "Modifier la publication", "publication": publication},
    )


@_admin_required
@require_POST
def admin_publication_delete(request, slug):
    publication = get_object_or_404(Publication, slug=slug)
    publication.delete()
    messages.success(request, "Publication supprimée.")
    return redirect("commune:home")


@_admin_required
@require_POST
def admin_comment_toggle_visibility(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.is_visible = not comment.is_visible
    comment.save(update_fields=["is_visible"])
    messages.success(
        request,
        "Commentaire masqué." if not comment.is_visible else "Commentaire visible à nouveau.",
    )
    return redirect(comment.publication.get_absolute_url())


@_admin_required
@require_POST
def admin_user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(
            request,
            "Utilisateur désactivé." if not user.is_active else "Utilisateur réactivé.",
        )
    next_url = request.POST.get("next") or reverse("commune:admin_dashboard")
    return HttpResponseRedirect(next_url)

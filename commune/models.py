from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class User(AbstractUser):
    ROLE_CITIZEN = "citizen"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_CITIZEN, "Citoyen"),
        (ROLE_ADMIN, "Administrateur"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CITIZEN,
    )
    bio = models.CharField(max_length=300, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    @property
    def is_commune_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser


class Publication(models.Model):
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content = models.TextField("Contenu")
    image = models.ImageField("Image", upload_to="publications/", blank=True, null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="publications",
        verbose_name="Auteur",
    )
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)
    is_published = models.BooleanField("Publié", default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Publication"
        verbose_name_plural = "Publications"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "publication"
            slug = base
            n = 0
            while Publication.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("commune:publication_detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    content = models.TextField("Contenu")
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField("Visible", default=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    def __str__(self):
        return f"Commentaire de {self.author} sur {self.publication_id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "publication"], name="unique_like_user_publication")
        ]
        verbose_name = "J'aime"
        verbose_name_plural = "J'aime"


class Notification(models.Model):
    TYPE_MENTION = "mention"
    TYPE_REPLY = "reply"
    TYPE_LIKE = "like"
    TYPE_GENERIC = "generic"
    TYPE_CHOICES = [
        (TYPE_MENTION, "Mention"),
        (TYPE_REPLY, "Réponse"),
        (TYPE_LIKE, "J'aime"),
        (TYPE_GENERIC, "Autre"),
    ]
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=500, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    related_comment = models.ForeignKey(
        Comment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.message[:80]

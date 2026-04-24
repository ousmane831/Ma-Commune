from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Comment, Notification, User
from .utils import extract_mentioned_usernames


def _notify_mentions(comment: Comment):
    usernames = extract_mentioned_usernames(comment.content)
    if not usernames:
        return
    pub = comment.publication
    url = pub.get_absolute_url()
    for username in usernames:
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            continue
        if user.pk == comment.author_id:
            continue
        Notification.objects.create(
            recipient=user,
            notification_type=Notification.TYPE_MENTION,
            message=f"{comment.author.get_username()} vous a mentionné(e) dans un commentaire.",
            link=url + f"#comment-{comment.pk}",
            related_comment=comment,
            related_publication=pub,
        )


def _notify_reply(comment: Comment):
    if not comment.parent_id:
        return
    parent = comment.parent
    if parent.author_id == comment.author_id:
        return
    pub = comment.publication
    Notification.objects.create(
        recipient=parent.author,
        notification_type=Notification.TYPE_REPLY,
        message=f"{comment.author.get_username()} a répondu à votre commentaire.",
        link=pub.get_absolute_url() + f"#comment-{comment.pk}",
        related_comment=comment,
        related_publication=pub,
    )


@receiver(post_save, sender=Comment)
def comment_saved(sender, instance: Comment, created, **kwargs):
    if not created or not instance.is_visible:
        return
    _notify_reply(instance)
    _notify_mentions(instance)

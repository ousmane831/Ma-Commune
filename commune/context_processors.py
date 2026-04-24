def notifications_unread(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(read_at__isnull=True).count()
    else:
        count = 0
    return {"unread_notifications_count": count}

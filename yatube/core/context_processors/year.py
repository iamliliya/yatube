from django.utils import timezone


def year(request):
    """Возвращает текущий год."""
    return {
        'year': timezone.now().year
    }

from .models import get_or_create_student_profile


def profile_context(request):
    if request.user.is_authenticated:
        profile = get_or_create_student_profile(request.user)
        return {'profile': profile}
    return {'profile': None}

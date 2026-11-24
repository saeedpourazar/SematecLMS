
def user_role(request):
    is_sematec_staff = False

    if request.user.is_authenticated:
        is_sematec_staff = request.user.groups.filter(
            name='Sematec Staff'
        ).exists()

    return {
        'is_sematec_staff': is_sematec_staff
    }


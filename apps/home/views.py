from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from apps.core.models import EstablishmentProfile

@login_required(login_url='login')
def show_home(request):

    profile, _ = EstablishmentProfile.objects.get_or_create(user=request.user)
    user_havens = profile.safe_havens.all()
    protocols = profile.protocols.all()
    
    total_havens_count = user_havens.count()
    total_people_helped = user_havens.aggregate(Sum('people_helped'))['people_helped__sum'] or 0
    
    context = {
        'profile': profile,
        'user_havens': user_havens,
        'protocols': protocols,
        'total_havens_count': total_havens_count,
        'total_people_helped': total_people_helped,
    }
    return render(request, "home/home.html", context)
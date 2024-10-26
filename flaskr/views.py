# views.py
from django.shortcuts import render, redirect
from .models import UserProfile, QuizScore
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    quiz_scores = QuizScore.objects.filter(user=request.user)
    context = {
        'form': form,
        'quiz_scores': quiz_scores,
    }
    return render(request, 'profile.html', context)

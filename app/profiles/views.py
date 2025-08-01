from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render

User = get_user_model()

@login_required
def profile_list_view(request):
    my_username = request.user.username
    context = {
        "object_list": User.objects.filter(is_active=True), 
        "my_current_username": my_username
    }
    return render(request, "profiles/list.html", context)

@login_required()
def profile_detail_view(request, username=None, *args, **kwargs):
    user = request.user
    print(
        user.has_perm("subscriptions.basic"),
        user.has_perm("subscriptions.pro"),
        user.has_perm("subscriptions.advanced")
    )
    """
    user_groups = user.groups.all()
    print(f"User groups: {user_groups}")
    print("HOLA; User is a Basic user.")
    if user_groups.filter(name__icontains='Basic').exists():
        print("User is a Basic user.")
        return HttpResponse("Congrats! You are a Basic user.")
    """
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    print(f"Is the profile user same as request user? {is_me}")
    context = {
        "object_list": profile_user_obj,
        "instance": profile_user_obj,
        "owner": is_me,
    }
    return render(request, 'profiles/detail.html', context)

"""
@login_required()
def user_only_view(request, *args, **kwargs):
    # print(request.user.is_staff)
    return render(request, "protected/user-only.html", {})

@login_required
def profile_view(request, username= None, *args, **kwargs):
    user = request.user
    #print(user.has_perm(""))
    #profile_user_obj = User.objects.get(username=username)
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    print(f"Is the profile user same as request user? {is_me}")
    return HttpResponse (f"Hello World, this is the profile view of {username}!\n" \
                        f"and the user id is {profile_user_obj.id} and email is {profile_user_obj.email}.\n" \
                        f"But the request-user is {user} and the request-id is {user.id}")

#(f"Hello World, this is the profile view of {username}! and the user id is {profile_user_obj.id} and email is {profile_user_obj.email}. But the request-user is {user}") 


"""

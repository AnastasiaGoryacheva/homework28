import json

from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from avito_project import settings
from user.models import User, Location


class UserView(ListView):
    models = User
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.annotate(total_ads=Count('ad'))

        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        users = []
        for user in self.object_list:
            users.append({
                'id': user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_name": user.user_name,
                "age": user.age,
                "role": user.role,
                'location': list(map(str, user.locations.all())),
                'total_ads': len(self.object_list),
            })
        response = {
            'items': users,
            'num_page': page_obj.paginator.num_pages,
            'total': page_obj.paginator.count
        }
        return JsonResponse(response, safe=False, json_dumps_params={"ensure_ascii": False})


class UserDetailView(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        response = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_name': user.user_name,
            'role': user.role,
            'age': user.age,
            'location': list(map(str, user.locations.all())),
        }
        return JsonResponse(response, json_dumps_params={"ensure_ascii": False})


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(CreateView):
    model = User
    fields = ['user_name', 'password', 'first_name', 'last_name', 'role', 'age', 'location']

    def post(self, request, *args, **kwargs):
        user_data = json.loads(request.body)
        user = User.objects.create(
            user_name=user_data["user_name"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            age=user_data["age"],
        )

        for location_name in user_data['locations']:
            location, _ = Location.objects.get_or_create(name=location_name)
            user.locations.add(location)

        response = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_name': user.user_name,
            'role': user.role,
            'age': user.age,
            'location': list(map(str, user.locations.all())),
        }
        return JsonResponse(response, json_dumps_params={"ensure_ascii": False})


@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ['user_name', 'password', 'first_name', 'last_name', 'role', 'age', 'location']

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        user_data = json.loads(request.body)
        self.object.user_name = user_data['user_name']
        self.object.password = user_data['password']
        self.object.first_name = user_data['first_name']
        self.object.last_name = user_data['last_name']
        self.object.age = user_data['age']

        for location_name in user_data['locations']:
            location, _ = Location.objects.get_or_create(name=location_name)
            self.object.locations.add(location)

        self.object.save()

        response = {
            'id': self.object.id,
            'first_name': self.object.first_name,
            'last_name': self.object.last_name,
            'user_name': self.object.user_name,
            'role': self.object.role,
            'age': self.object.age,
            'location': list(map(str, self.object.locations.all())),
        }
        return JsonResponse(response, json_dumps_params={"ensure_ascii": False})


@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({"status": "ok/delete"}, status=200)

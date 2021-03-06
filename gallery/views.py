from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  RedirectView, UpdateView)
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from gallery.models import Image

# Create your views here.


# def home(request):
#     context: {
#         'images': Image.objects.filter(approved=True)
#     }
#     return render(request, 'gallery/home.html', context)


class ImageListView(ListView):
    model = Image
    template_name = 'gallery/home.html'
    context_object_name = 'images'
    paginate_by = '6'

    def get_queryset(self):
        return Image.objects.filter(approved=True).order_by('-date_posted')


class ImageByLikesListView(ListView):
    model = Image
    template_name = 'gallery/home.html'
    context_object_name = 'images'
    paginate_by = '6'

    def get_queryset(self):
        return Image.objects.filter(approved=True).order_by('-total_likes')


class ImageNonApprovedListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Image
    template_name = 'gallery/images_for_approval.html'
    context_object_name = 'images'
    paginate_by = '6'

    def get_queryset(self):
        return Image.objects.filter(approved=False)

    def test_func(self):
        if self.request.user.is_superuser == True:
            return True
        return False


class ImageDetailView(DetailView):
    model = Image


class ImageCreateView(LoginRequiredMixin, CreateView):
    model = Image
    fields = [
        'title',
        'image'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ImageLikeAPIToggle(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None, *args, **kwargs):
        image_obj = get_object_or_404(Image, pk=kwargs['pk'])
        user = self.request.user
        updated = False 
        liked = False

        if user.is_authenticated:
            if user in image_obj.likes.all():
                liked = False
                image_obj.likes.remove(user)
            else:
                liked = True
                image_obj.likes.add(user)
            updated = True

        counts=image_obj.likes.count()

        image_obj.total_likes = counts
        image_obj.save()

        data = {
            "updated": updated,
            "liked": liked,
            "likescount": counts
        }

        return Response(data)


class ImageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Image
    fields = [
        'approved'
    ]

    def test_func(self):
        image = self.get_object()
        if self.request.user.is_superuser == True:
            return True
        return False

class ImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Image
    success_url = '/'

    def test_func(self):
        if self.request.user.is_superuser == True:
            return True
        return False

def about(request):
    return render(request, 'gallery/about.html', {'title': 'About'})

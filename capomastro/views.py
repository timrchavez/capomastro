from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = "home.html"

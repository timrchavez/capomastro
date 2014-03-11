import json
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View, ListView, DetailView, TemplateView
from braces.views import (
    LoginRequiredMixin, PermissionRequiredMixin, CsrfExemptMixin)

from jenkins.models import JenkinsServer, Build, Job
from jenkins.tasks import import_build_task


class NotificationHandlerView(CsrfExemptMixin, View):

    http_method_names = ["post"]

    def get_server(self, request):
        """
        Attempt to locate the remote server for this request.
        """
        remote_addr=request.META["REMOTE_ADDR"]
        try:
            return JenkinsServer.objects.get(remote_addr=remote_addr)
        except JenkinsServer.DoesNotExist:
            logging.warn(
                "Could not find server with REMOTE_ADDR: %s" % remote_addr)

    def post(self, request, *args, **kwargs):
        """
        Handle incoming Jenkins notifications.
        """
        server = self.get_server(request)
        if not server:
            return HttpResponse(status=412)
        notification = json.loads(request.body)
        if notification["build"].get("phase") == "FINISHED":
            try:
                job = server.job_set.get(name=notification["name"])
            except Job.DoesNotExist:
                logging.warn(
                    "Notification for unknown job '%s'" % notification["name"])
                return HttpResponse(status=412)
            else:
                job.build_set.create(
                    number=notification["build"]["number"],
                    result=notification["build"]["status"],
                    url=notification["build"]["url"],
                    phase=notification["build"]["phase"])
                import_build_task.delay(job.pk, notification["build"]["number"])
        return HttpResponse(status=200)


class JenkinsServerListView(LoginRequiredMixin, ListView):

    model = JenkinsServer


class JenkinsServerDetailView(LoginRequiredMixin, DetailView):

    model = JenkinsServer
    context_object_name = "server"

    def get_context_data(self, **kwargs):
        """
        Supplement the server with the jobs for this server.
        """
        context = super(
            JenkinsServerDetailView, self).get_context_data(**kwargs)
        context["jobs"] = context["server"].job_set.all()
        return context


class JenkinsServerJobBuildsIndexView(LoginRequiredMixin, TemplateView):

    template_name = "jenkins/jenkinsserver_job_builds_index.html"

    def get_context_data(self, **kwargs):
        context = super(
            JenkinsServerJobBuildsIndexView, self).get_context_data(**kwargs)
        server = get_object_or_404(JenkinsServer, pk=kwargs["server_pk"])
        job = get_object_or_404(server.job_set, pk=kwargs["job_pk"])
        context["builds"] = job.build_set.all()
        context["job"] = job
        context["server"] = server
        return context


__all__ = [
    "NotificationHandlerView", "JenkinsServerListView",
    "JenkinsServerDetailView", "JenkinsServerJobBuildsIndexView"]

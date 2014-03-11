from django.forms import ModelForm

from projects.models import Project, Dependency


class ProjectForm(ModelForm):

#    def __init__(self, *args, **kwargs):
#        super(ProjectForm, self).__init__(*args, **kwargs)
#
    class Meta:
        model = Project

    def save(self, commit=True):
        project = super(ProjectForm, self).save()
        return project

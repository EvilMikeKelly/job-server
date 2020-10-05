from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Job, Workspace


class JobCreateForm(forms.ModelForm):
    class Meta:

        fields = [
            "workspace",
            "force_run",
            "force_run_dependencies",
            "action_id",
            "callback_url",
        ]
        model = Job

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))


class WorkspaceCreateForm(forms.ModelForm):
    class Meta:
        fields = [
            "name",
            "repo",
            "branch",
            "owner",
            "db",
        ]
        model = Workspace
        widgets = {
            "name": forms.TextInput(),
            "repo": forms.TextInput(),
            "branch": forms.TextInput(),
            "owner": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

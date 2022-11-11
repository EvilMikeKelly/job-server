from django import forms
from first import first

from .authorization.forms import RolesForm
from .models import JobRequest


class JobRequestCreateForm(forms.ModelForm):
    class Meta:
        fields = [
            "force_run_dependencies",
            "will_notify",
        ]
        model = JobRequest
        widgets = {
            "will_notify": forms.RadioSelect(
                choices=[(True, "Yes"), (False, "No")],
            ),
        }

    def __init__(self, actions, backends, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #  add action field based on the actions passed in
        choices = [(a, a) for a in actions]
        self.fields["requested_actions"] = forms.MultipleChoiceField(
            choices=choices,
            widget=forms.CheckboxSelectMultiple,
            error_messages={
                "required": "Please select at least one of the Actions listed above."
            },
        )

        # only set an initial if there is one backend since the selector will
        # be hidden on the page
        initial = backends[0][0] if len(backends) == 1 else None

        # bulid the backends field based on the backends passed in
        self.fields["backend"] = forms.ChoiceField(
            choices=backends, initial=initial, widget=forms.RadioSelect
        )


class JobRequestSearchForm(forms.Form):
    identifier = forms.CharField()


class ProjectMembershipForm(RolesForm):
    pass


class WorkspaceArchiveToggleForm(forms.Form):
    is_archived = forms.BooleanField(required=False)


class WorkspaceCreateForm(forms.Form):
    name = forms.SlugField(
        help_text="Enter a descriptive name which makes this workspace easy to identify.  It will also be the name of the directory in which you will find results after jobs from this workspace are run."
    )
    purpose = forms.CharField(help_text="Describe the purpose of this workspace.")
    branch = forms.CharField()

    def __init__(self, repos_with_branches, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.repos_with_branches = repos_with_branches

        # construct the repo Form field
        repo_choices = [(r["url"], r["name"]) for r in self.repos_with_branches]
        self.fields["repo"] = forms.ChoiceField(
            label="Repo",
            choices=repo_choices,
        )

        # has there been a repo selected already?
        if "data" in kwargs and "repo" in kwargs["data"]:
            repo = first(
                self.repos_with_branches,
                key=lambda r: r["url"] == kwargs["data"]["repo"],
            )
        else:
            repo = first(self.repos_with_branches)

        # construct the branch Form field
        branch_choices = [(b, b) for b in repo["branches"]]
        self.fields["branch"] = forms.ChoiceField(
            label="Branch",
            choices=branch_choices,
        )

    def clean(self):
        cleaned_data = super().clean()
        repo_url = cleaned_data["repo"]
        branch = cleaned_data["branch"]

        repo = first(self.repos_with_branches, key=lambda r: r["url"] == repo_url)
        if repo is None:
            msg = "Unknown repo, please reload the page and try again"
            raise forms.ValidationError(msg)

        # normalise branch names so we can do a case insensitive match
        branches = [b.lower() for b in repo["branches"]]
        if branch.lower() not in branches:
            raise forms.ValidationError(f'Unknown branch "{branch}"')

    def clean_name(self):
        name = self.cleaned_data["name"]

        return name.lower()


class WorkspaceEditForm(forms.Form):
    purpose = forms.CharField(help_text="Describe the purpose of this workspace.")


class WorkspaceNotificationsToggleForm(forms.Form):
    should_notify = forms.BooleanField(required=False)

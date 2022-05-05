from django import forms
from django.db.models.functions import Lower

from applications.forms import YesNoField
from applications.models import Application, ResearcherRegistration
from jobserver.authorization.forms import RolesForm
from jobserver.backends import backends_to_choices
from jobserver.models import Backend, Org, Project


def user_label_from_instance(obj):
    full_name = obj.get_full_name()
    return f"{obj.username} ({full_name})" if full_name else obj.username


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return user_label_from_instance(obj)


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return user_label_from_instance(obj)


class PickUsersMixin:
    """
    A generic form for picking Users to link to another object.

    We connect users to different objects (eg Orgs) via membership models.  In
    the Staff Area we want a UI to handle creating those connections.  In
    particular we want to order Users by their username, ignoring case, and
    display them with both username and full name.
    """

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = users.order_by(Lower("username"))
        self.fields["users"] = UserModelMultipleChoiceField(queryset=users)


class ApplicationApproveForm(forms.Form):
    org = forms.ModelChoiceField(queryset=Org.objects.order_by("name"))
    project_name = forms.CharField(help_text="Update the study name if necessary")

    def clean_project_name(self):
        project_name = self.cleaned_data["project_name"]

        if Project.objects.filter(name=project_name).exists():
            raise forms.ValidationError(f'Project "{project_name}" already exists.')

        return project_name


class OrgAddGitHubOrgForm(forms.Form):
    name = forms.CharField()


class OrgAddMemberForm(PickUsersMixin, forms.Form):
    pass


class ProjectAddMemberForm(PickUsersMixin, RolesForm):
    pass


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        fields = [
            "name",
            "org",
        ]
        model = Project

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        orgs = Org.objects.order_by("name")

        self.fields["org"] = forms.ModelChoiceField(queryset=orgs)


class ProjectEditForm(forms.ModelForm):
    class Meta:
        fields = [
            "name",
            "copilot",
            "copilot_support_ends_at",
        ]
        model = Project

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = users.order_by(Lower("username"))
        self.fields["copilot"] = UserModelChoiceField(queryset=users, required=False)
        self.fields["copilot_support_ends_at"].required = False


class ProjectFeatureFlagsForm(forms.Form):
    flip_to = forms.ChoiceField(
        choices=[
            ("enable", "enable"),
            ("disable", "disable"),
        ],
    )


class ProjectLinkApplicationForm(forms.Form):
    application = forms.CharField()

    def __init__(self, instance, *args, **kwargs):
        # this is used by a subclass of UpdateView, which expects a ModelForm,
        # so all we're doing here is dropping the `instance` arg.
        super().__init__(*args, **kwargs)

    def clean_application(self):
        pk = self.cleaned_data["application"]

        try:
            application = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            raise forms.ValidationError("Unknown Application")

        if application.project:
            raise forms.ValidationError("Can't link Application to multiple Projects")

        return application


class ProjectMembershipForm(RolesForm):
    pass


class ResearcherRegistrationEditForm(forms.ModelForm):
    does_researcher_need_server_access = YesNoField()
    has_taken_safe_researcher_training = YesNoField()
    phone_type = forms.TypedChoiceField(
        choices=ResearcherRegistration.PhoneTypes.choices,
        empty_value=None,
        required=False,
        widget=forms.RadioSelect,
    )

    class Meta:
        fields = [
            "name",
            "job_title",
            "email",
            "does_researcher_need_server_access",
            "telephone",
            "phone_type",
            "has_taken_safe_researcher_training",
            "training_with_org",
            "training_passed_at",
            "daa",
            "github_username",
        ]
        model = ResearcherRegistration


class UserForm(RolesForm):
    is_superuser = forms.BooleanField(required=False)

    def __init__(self, *, available_backends, **kwargs):
        super().__init__(**kwargs)

        # build choices from the available backends
        choices = backends_to_choices(available_backends)

        self.fields["backends"] = forms.MultipleChoiceField(
            choices=choices,
            required=False,
            widget=forms.CheckboxSelectMultiple,
        )

    def clean_backends(self):
        """Convert backend names to Backend instances"""
        return Backend.objects.filter(slug__in=self.cleaned_data["backends"])


class UserOrgsForm(forms.Form):
    def __init__(self, *, available_orgs, **kwargs):
        super().__init__(**kwargs)

        # build choices from the available orgs
        # choices = backends_to_choices(available_orgs)

        self.fields["orgs"] = forms.ModelMultipleChoiceField(
            # choices=choices,
            queryset=available_orgs,
            required=False,
            widget=forms.CheckboxSelectMultiple,
        )

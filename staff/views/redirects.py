from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, View

from jobserver.authorization import CoreDeveloper
from jobserver.authorization.decorators import require_role
from redirects.models import Redirect


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class RedirectDelete(View):
    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(Redirect, pk=self.kwargs["pk"])

        obj.delete()

        messages.success(request, f"Deleted redirect for {obj.type}: {obj.obj.name}")

        return redirect("staff:redirect-list")


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class RedirectDetail(DetailView):
    model = Redirect
    template_name = "staff/redirect_detail.html"


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class RedirectList(ListView):
    model = Redirect
    ordering = "-old_url"
    template_name = "staff/redirect_list.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "types": ["project", "workspace"],
            "q": self.request.GET.get("q", ""),
        }

    def get_queryset(self):
        qs = super().get_queryset()

        if q := self.request.GET.get("q"):
            qs = qs.filter(
                Q(old_url__icontains=q)
                | Q(project__name__icontains=q)
                | Q(workspace__name__icontains=q)
                | Q(created_by__username__icontains=q)
                | Q(created_by__fullname__icontains=q)
            ).distinct()

        if object_type := self.request.GET.get("type"):
            qs = qs.filter(**{f"{object_type}__isnull": False})

        return qs

import functools
import itertools

from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from jobserver.authorization import CoreDeveloper
from jobserver.authorization.decorators import require_role
from jobserver.models import Backend, User, Workspace


# configure searchable models here, each must have get_staff_url defined
configured_searches = [
    {"model": Backend, "fields": ["name", "slug"], "order_by": "name"},
    {
        "model": User,
        "fields": ["first_name", "last_name", "username"],
        "order_by": "username",
    },
    {"model": Workspace, "fields": ["name", "repo"], "order_by": "name"},
]


def get_results(q):
    """
    Turn a search term into queries for each configured model

    This takes the given search term and for each model configured to be
    searchable does:

        1. creates a Q(field=search_term) instance
        2. combines them with a logical OR, typically expressed with a | (pipe)
        3. creates a QuerySet for the model
        4. adds that QuerySet to a list for later

    The list of QuerySets is consumed, turning it in a flat list (via a
    generator) of Model isntances across all searchable models which returned
    results.

    """
    if not q:
        return []

    queries = []
    for target in configured_searches:
        qwargs = functools.reduce(
            Q.__or__, (Q(**{f"{f}__icontains": q}) for f in target["fields"])
        )
        qs = target["model"].objects.filter(qwargs).order_by(target["order_by"])

        queries.append(qs)

    return list(itertools.chain.from_iterable(queries))


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class Index(View):
    def get(self, request, *args, **kwargs):
        q = self.request.GET.get("q")
        results = get_results(q)

        # group the results by their model's classname for display in the view
        results = itertools.groupby(results, key=lambda m: m.__class__.__name__)

        # consume the groupby generator such that Django won't butcher it
        # https://stackoverflow.com/a/16171518/158304
        results = [(grouper, list(values)) for grouper, values in results]

        context = {
            "q": q,
            "results": results,
        }

        return TemplateResponse(
            request,
            "staff/index.html",
            context=context,
        )

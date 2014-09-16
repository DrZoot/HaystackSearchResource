from django.conf.urls import url
from django.core.paginator import Paginator, InvalidPage
from tastypie.resources import ModelResource
from haystack.query import SearchQuerySet
from tastypie.utils import trailing_slash
from django.http import Http404


class HaystackSearchResource(ModelResource):
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
            url(r"^(?P<resource_name>%s)/autocomplete%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_autocomplete'), name="api_get_autocomplete"),
        ]

    def get_search(self, request, **kwargs):
        sqs = SearchQuerySet().models(self.get_model()).auto_query(request.GET.get('q', '')).load_all()
        return self.get_haystack_search(request, sqs)

    def get_autocomplete(self, request, **kwargs):
        q = {}
        q[self.get_autocomplete_field()] = request.GET.get('q', '')
        sqs = SearchQuerySet().models(self.get_model()).autocomplete(**q).load_all()
        return self.get_haystack_search(request, sqs)

    def get_haystack_search(self, request, sqs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        paginator = Paginator(sqs, self.get_page_size())

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404('No results at page {}'.format(request.GET.get('page', 1)))

        objects = []

        for result in page.object_list:
            if result is None:
                # This is because of whoosh, it returns None entries
                # for objects that match but are excluded by the
                # .models(klass) filter
                continue
            bundle = self.build_bundle(obj=result.object, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def get_model(self):
        '''Return the model for the model resource'''
        return getattr(self, 'model', NotImplemented)

    def get_autocomplete_field(self):
        '''Return the name of the field to use for autocomplete lookups'''
        return getattr(self, 'autocomplete_field', NotImplemented)

    def get_page_size(self):
        '''Return the page size to return'''
        return getattr(self, 'page_size', 20)

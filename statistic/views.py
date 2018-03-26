from account.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from jobboard.decorators import choose_role_required
from django.contrib.contenttypes.models import ContentType
from django.urls import resolve


class StatisticView(ListView):
    template_name = 'statistic/statistic_list.html'
    ordering = '-date_created'
    paginate_by = 20
    allow_empty = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pk = None
        self.related_model = None
        self.related_model_object = None

    @method_decorator(login_required)
    @method_decorator(choose_role_required)
    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk')
        try:
            model = ContentType.objects.get(model=resolve(request.META['PATH_INFO']).url_name)
        except ContentType.DoesNotExist:
            print('Not exist!')
        else:
            self.model = model.model_class()
            self.set_related_model()
        return self.check_related_object(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.filter(obj_id=self.pk).exclude(role=self.request.role,
                                                       role_obj_id=self.request.role_object.id)

    def set_related_model(self):
        related_model_name = self.model.related_model_name
        related_model_cont = ContentType.objects.get(model=related_model_name)
        self.related_model = related_model_cont.model_class()

    def check_related_object(self, request, *args, **kwargs):
        self.related_model_object = get_object_or_404(self.related_model, pk=self.pk)
        user_field = self.related_model_object.user_field_name
        if getattr(self.related_model_object, user_field) != request.role_object:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'related': self.related_model_object})
        return context

from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView
from jobboard.mixins import OnlyEmployerMixin
from pipeline.models import Pipeline, ActionType
from vacancy.models import Vacancy


class PipelineConstructorView(OnlyEmployerMixin, TemplateView):
    template_name = 'pipeline/constructor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_types'] = ActionType.objects.all()
        context['vacancy'] = get_object_or_404(Vacancy, pk=kwargs.get('pk'))
        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        print(args)
        print(kwargs)
        return super().get(request, *args, **kwargs)

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, DeleteView

from jobboard.mixins import OnlyEmployerMixin
from .forms import CompanyForm, OfficeForm
from .models import Company, Address, Office


class CompaniesView(OnlyEmployerMixin, ListView):
    model = Company

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(employer=self.request.role_object)


class NewCompanyView(OnlyEmployerMixin, CreateView):
    form_class = CompanyForm
    template_name = 'company/company_form.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def form_valid(self, form):
        form.instance.employer = self.request.role_object
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            address = Address.objects.create(raw=kwargs['data']['legal_address'])
            data = kwargs['data'].copy()
            data['legal_address'] = address.id
            kwargs['data'] = data
        return kwargs

    def get_success_url(self):
        return reverse('companies')


class CompanyDetailsView(DetailView):
    model = Company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['office_form'] = OfficeForm()
        return context


class CompanyDeleteView(OnlyEmployerMixin, DeleteView):
    model = Company

    def dispatch(self, request, *args, **kwargs):
        company = self.get_object()
        if not company.employer == request.role_object:
            messages.warning(request, 'You can\'t delete this company')
            return HttpResponseRedirect(reverse('profile'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('companies')


class CompanyNewOfficeView(OnlyEmployerMixin, View):
    def post(self, request, *args, **kwargs):
        company = get_object_or_404(Company, pk=kwargs.get('pk'), employer=request.role_object)
        office = Office()
        office.company = company
        office.address = Address.objects.create(raw=request.POST.get('address'))
        office.main = 'main' in request.POST
        office.save()
        if request.is_ajax:
            return JsonResponse({'id': office.pk, 'label': str(office)})
        return HttpResponseRedirect(reverse('company', kwargs={'pk': company.pk}))

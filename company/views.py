from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, DeleteView, RedirectView

from company.tasks import set_member_role, change_member_role
from jobboard.handlers.oracle import OracleHandler
from .forms import CompanyForm, OfficeForm
from .models import Company, Address, Office, SocialLink, RequestToCompany


class CompaniesView(ListView):
    model = Company

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None
        self.oracle = OracleHandler()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CompaniesView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        companies = self.oracle.get_member_companies(self.request.user.contract_address)
        return qs.filter(contract_address__in=companies)


class NewCompanyView(CreateView):
    form_class = CompanyForm
    template_name = 'company/company_form.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = None

    def form_valid(self, form):
        form.instance.created_by = self.request.user
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


class CompanyDeleteView(DeleteView):
    model = Company

    def dispatch(self, request, *args, **kwargs):
        company = self.get_object()
        if not company.employer == request.role_object:
            messages.warning(request, 'You can\'t delete this company')
            return HttpResponseRedirect(reverse('profile'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('companies')


class CompanyNewOfficeView(View):

    def post(self, request, *args, **kwargs):
        try:
            company = request.user.companies.get(pk=kwargs.get('pk'))
        except Company.DoesNotExist:
            if request.is_ajax():
                return HttpResponse(status=400)
            return HttpResponseRedirect(reverse('profile'))
        else:
            office = Office()
            office.company = company
            office.address = Address.objects.create(raw=request.POST.get('address'))
            office.main = 'main' in request.POST
            office.save()
            if request.is_ajax():
                return JsonResponse({'id': office.pk, 'label': str(office)})
            return HttpResponseRedirect(reverse('company', kwargs={'pk': company.pk}))


class NewSocialLink(CreateView):
    model = SocialLink
    fields = ['company', 'link', ]

    def get_success_url(self):
        return self.object.company.get_absolute_url()


class AddCompanyMember(RedirectView):
    pattern_name = 'company'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        member_role = request.POST.get('role')
        invite = request.POST.get('req')
        try:
            inv = RequestToCompany.objects.get(pk=invite)
        except RequestToCompany.DoesNotExist:
            pass
        else:
            set_member_role.delay(inv.company.contract_address, request.user.id, inv.member.id, member_role)
            inv.delete()
            return super().get(request, *args, pk=inv.company.id)


class ChangeCompanyMember(RedirectView):
    pattern_name = 'company'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        company = get_object_or_404(Company, pk=request.POST.get('company_id'))
        member_id = request.POST.get('member_id')
        role = request.POST.get('role')
        change_member_role.delay(company.contract_address, member_id, request.user.id, role)
        return super().get(request, *args, pk=company.id)

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Member, InviteCode


def make_phones_verified(modeladmin, request, queryset):
    queryset.update(phone_number_verified=True)


make_phones_verified.short_description = "Mark selected user phones as verified"


def make_phones_unverified(modeladmin, request, queryset):
    queryset.update(phone_number_verified=False)


make_phones_unverified.short_description = "Mark selected user phones as unverified"


class MemberAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Member
    list_display = ['email', 'username', 'country_code', 'phone_number', 'contract_address']
    actions = [make_phones_verified, make_phones_unverified, ]


def make_links(n):
    links = []
    for i in range(n):
        links.append(InviteCode())
    InviteCode.objects.bulk_create(links)


def make_5_links(modeladmin, request, queryset):
    make_links(5)
    messages.info(request, '5 invite links were created')


def make_50_links(modeladmin, request, queryset):
    make_links(50)
    messages.info(request, '50 invite links were created')


def make_100_links(modeladmin, request, queryset):
    make_links(100)
    messages.info(request, '100 invite links were created')


make_5_links.short_description = 'Make 5 invite links'
make_50_links.short_description = 'Make 50 invite links'
make_100_links.short_description = 'Make 100 invite links'


class InviteCodeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in InviteCode._meta.fields]
    actions = [make_5_links, make_50_links, make_100_links]

    class Meta:
        model = InviteCode


admin.site.register(Member, MemberAdmin)
admin.site.register(InviteCode, InviteCodeAdmin)

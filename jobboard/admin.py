from django.contrib import admin
from .models import Specialisation, Keyword, Candidate, Employer, Transaction, TransactionHistory


class AdminSpecialisation(admin.ModelAdmin):
    list_display = ('title', 'parent')

    class Meta:
        model = Specialisation


class AdminKeywords(admin.ModelAdmin):
    list_display = ('word',)

    class Meta:
        model = Keyword


class AdminCandidate(admin.ModelAdmin):
    list_display = [field.name for field in Candidate._meta.fields]

    class Meta:
        model = Candidate


class AdminEmployer(admin.ModelAdmin):
    list_display = [field.name for field in Employer._meta.fields]

    class Meta:
        model = Employer


class AdminTxn(admin.ModelAdmin):
    list_display = [field.name for field in Transaction._meta.fields]

    class Meta:
        model = Transaction


class AdminTransactionHistory(admin.ModelAdmin):
    list_display = [field.name for field in TransactionHistory._meta.fields]

    class Meta:
        model = TransactionHistory


admin.site.register(Specialisation, AdminSpecialisation)
admin.site.register(Keyword, AdminKeywords)
admin.site.register(Candidate, AdminCandidate)
admin.site.register(Employer, AdminEmployer)
admin.site.register(Transaction, AdminTxn)
admin.site.register(TransactionHistory, AdminTransactionHistory)

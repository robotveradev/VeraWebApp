from django.contrib import admin
from .models import Specialisation, Keyword, Transaction, TransactionHistory


class AdminSpecialisation(admin.ModelAdmin):
    list_display = ('title', 'parent')

    class Meta:
        model = Specialisation


class AdminKeywords(admin.ModelAdmin):
    list_display = ('word',)

    class Meta:
        model = Keyword


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
admin.site.register(Transaction, AdminTxn)
admin.site.register(TransactionHistory, AdminTransactionHistory)

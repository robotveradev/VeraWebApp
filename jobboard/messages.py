from django.utils.translation import ugettext_lazy as _

MESSAGES = {
    'VacancyChange': _('Vacancy status change now pending.') + '&nbsp;<span data-uk-spinner="ratio: 0.5"></span>',
    'Not_VacancyChange':
        '<span class="red-text" data-uk-icon="ban"></span>&emsp;To add new pipeline action you have to disable vacancy.',
    'ActionDeleted': _('Action delete now pending...') + '&nbsp;<span data-uk-spinner="ratio: 0.5"></span>',
    'NewAction': _('Transaction for add new action now pending...') + '&nbsp;<span data-uk-spinner="ratio: 0.5"></span>',
}

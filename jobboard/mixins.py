from django.utils.decorators import method_decorator
from jobboard.decorators import choose_role_required, role_required


class ChooseRoleMixin:

    @method_decorator(choose_role_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OnlyEmployerMixin:

    @method_decorator(role_required('employer'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OnlyCandidateMixin:

    @method_decorator(role_required('candidate'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class OnlyOwnerMixin(ChooseRoleMixin):

    def dispatch(self, request, *args, **kwargs):
        print(request.role_object.user_name_field)
        return super().dispatch(request, *args, **kwargs)

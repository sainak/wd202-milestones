from django.contrib.auth.mixins import LoginRequiredMixin


class ObjectOwnerMixin(LoginRequiredMixin):
    """
    Restrict access to the endpoint to the owner of the object.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)

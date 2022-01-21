from django.contrib.auth.mixins import LoginRequiredMixin


class ObjectOwnerMixin(LoginRequiredMixin):
    """
    Restrict access to the endpoint to the owner of the object.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def form_valid(self, form):
        # if its delete, we don't need to set the user
        if self.request.POST.get("confirm_delete") is None:
            form.instance.user = self.request.user
        return super().form_valid(form)


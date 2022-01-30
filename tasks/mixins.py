class ObjectOwnerMixin:
    """
    Restrict access to the endpoint to the owner of the object.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

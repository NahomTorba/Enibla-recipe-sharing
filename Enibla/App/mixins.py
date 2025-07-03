from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

class AuthorRequiredMixin(LoginRequiredMixin):
    """
    Mixin that ensures only the author of an object can access the view.
    """
    def dispatch(self, request, *args, **kwargs):
        # First check if user is authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get the object and check if current user is the author
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied("You don't have permission to edit this recipe.")
        
        return super().dispatch(request, *args, **kwargs)

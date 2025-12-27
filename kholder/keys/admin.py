from django.contrib import admin
from .models import Key


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
	# Only allow editing the `label` field and deleting objects.
	# Disable adding new objects from the admin UI by returning False
	# from `has_add_permission`.
	fields = ("label",)
	list_display = ("label", "created_at", "updated_at")
	readonly_fields = ("created_at", "updated_at")
	search_fields = ("label",)
	ordering = ("-created_at",)
	# Hide "Save as new" option to avoid creating copies
	save_as = False

	def has_add_permission(self, request):
		# Disable the "Add" button in the admin UI
		return False

from django.contrib import admin

from drf_firebase3_auth.models import FirebaseUser, FirebaseUserProvider


@admin.register(FirebaseUser)
class FirebaseUserAdmin(admin.ModelAdmin):
    pass

@admin.register(FirebaseUserProvider)
class FirebaseUserProviderAdmin(admin.ModelAdmin):
    list_display = ('firebase_user', 'provider_id', )
    list_filter = ('provider_id', )

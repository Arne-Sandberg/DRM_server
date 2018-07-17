from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import User, ContractCase, UserInfo, ContractStage, NotifyEvent


class UserInfoInline(admin.TabularInline):
    model = UserInfo


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    inlines = [
        UserInfoInline,
    ]

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'family_name', 'admin', 'judge')
    list_filter = ('admin', 'judge')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'family_name', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('admin', 'judge')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'family_name',
                       'password1', 'password2')}
        ),
    )
    search_fields = ('email', 'name', 'family_name', 'info__payment_num',
                     'info__tax_number', 'info__organization_name')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


class ContractStageInline(admin.StackedInline):
    model = ContractStage


class ContractCaseAdmin(admin.ModelAdmin):
    inlines = [
        ContractStageInline,
    ]


admin.site.register(ContractCase, ContractCaseAdmin)


class NotifyEventAdmin(admin.ModelAdmin):
    pass


admin.site.register(NotifyEvent, NotifyEventAdmin)

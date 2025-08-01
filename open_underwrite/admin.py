from django.contrib import admin
from .models import LoanRequest

@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = (
        'loan_id', 'first_name', 'last_name', 'age',
        'loan_amount', 'credit_score', 'status', 'request_date'
    )
    search_fields = ('loan_id', 'first_name', 'last_name')
    list_filter = ('status', 'education', 'employment_type', 'marital_status')

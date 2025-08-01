from django.db import models

class LoanRequest(models.Model):
    loan_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()
    age = models.IntegerField()

    income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_score = models.IntegerField(default=0)
    months_employed = models.IntegerField(default=0)
    num_credit_lines = models.IntegerField(default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    loan_term = models.IntegerField(default=0)
    dti_ratio = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    education = models.CharField(max_length=20, default='High School')
    employment_type = models.CharField(max_length=20, default='Full-Time')
    marital_status = models.CharField(max_length=20, default='Single')
    other_loans = models.BooleanField(default=False)
    total_loan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    has_mortgage = models.BooleanField(default=False)
    total_mortgage_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    has_dependents = models.BooleanField(default=False)
    loan_purpose = models.CharField(max_length=20, default='Other')
    has_cosigner = models.BooleanField(default=False)

    verification_passkey = models.CharField(max_length=6, unique=True)
    status = models.CharField(max_length=10, default='Judging')
    request_date = models.DateField(auto_now_add=True)


class BankSettings(models.Model):
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)

    def __str__(self):
        return f"Interest Rate: {self.interest_rate}%"


class ModelTrainingStatus(models.Model):
    trained = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Trained" if self.trained else "Not Trained"

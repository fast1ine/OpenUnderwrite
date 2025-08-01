from django.test import TestCase
from .models import LoanRequest

class LoanRequestModelTest(TestCase):
    def setUp(self):
        self.loan = LoanRequest.objects.create(
            loan_id="TEST123",
            first_name="John",
            last_name="Doe",
            dob="1990-01-01",
            age=34,
            income=5000,
            annual_income=60000,
            loan_amount=20000,
            credit_score=700,
            months_employed=36,
            num_credit_lines=3,
            interest_rate=5.5,
            loan_term=24,
            dti_ratio=0.3,
            education="Bachelor's",
            employment_type="Full-Time",
            marital_status="Single",
            other_loans=False,
            total_loan_amount=20000,
            has_mortgage=False,
            total_mortgage_amount=0,
            has_dependents=False,
            loan_purpose="Business",
            has_cosigner=False,
            verification_passkey="123456"
        )

    def test_loan_request_creation(self):
        loan = LoanRequest.objects.get(loan_id="TEST123")
        self.assertEqual(loan.first_name, "John")
        self.assertEqual(loan.credit_score, 700)
        self.assertEqual(loan.status, "Judging")

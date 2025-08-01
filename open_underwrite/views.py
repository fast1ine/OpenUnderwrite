from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import LoanRequest, BankSettings, ModelTrainingStatus
import pandas as pd
import joblib
import random
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def loan_request(request):
    years  = range(1900, datetime.now().year + 1)
    months = range(1, 13)
    days   = range(1, 32)
    settings_obj  = BankSettings.objects.first()
    interest_rate = settings_obj.interest_rate if settings_obj else 5.00

    return render(request, 'requests.html', {
        'years': years,
        'months': months,
        'days': days,
        'interest_rate': interest_rate,
        'now': datetime.now(),
    })

def loan_status(request):
    if request.method == 'POST':
        passkey = request.POST.get('passkey')
        if not passkey:
            return render(request, 'status.html', {'error': '확인용 암호를 입력하세요.'})

        loan = LoanRequest.objects.filter(verification_passkey=passkey).first()
        if not loan:
            return render(request, 'status.html', {'error': '해당 암호로 신청서를 찾을 수 없습니다.'})

        return render(request, 'status.html', {'loan': loan, 'passkey': passkey})

    return render(request, 'status.html')

def admin_status(request):
    flag          = ModelTrainingStatus.objects.first()
    model_trained = flag.trained if flag else False
    loans         = LoanRequest.objects.all() if model_trained else []
    return render(request, 'admin_status.html', {
        'model_trained': model_trained,
        'loans': loans
    })

def admin_settings(request):
    if request.method == 'POST' and 'save_rate' in request.POST:
        rate = safe_float(request.POST.get('interest_rate'), 5.00)
        BankSettings.objects.update_or_create(defaults={'interest_rate': rate})

    settings_obj = BankSettings.objects.first()
    return render(request, 'admin_settings.html', {
        'settings': settings_obj or BankSettings(interest_rate=5.00)
    })

@csrf_exempt
def train_model(request):
    if request.method == 'POST' and request.FILES.get('file'):
        data = pd.read_csv(request.FILES['file']).dropna()
        data_encoded = pd.get_dummies(data.drop('LoanID', axis=1), drop_first=True)

        X = data_encoded.drop('Default', axis=1)
        y = data_encoded['Default']

        feature_names = X.columns.tolist()
        joblib.dump(feature_names, settings.FEATURES_PATH)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = LogisticRegression(max_iter=5000)
        model.fit(X_scaled, y)

        joblib.dump(model,  settings.MODEL_PATH)
        joblib.dump(scaler, settings.SCALER_PATH)

        ModelTrainingStatus.objects.all().delete()
        ModelTrainingStatus.objects.create(trained=True)

        return redirect('admin_status')

    return redirect('admin_settings')

def admin_status_detail(request, passkey):
    loan        = get_object_or_404(LoanRequest, verification_passkey=passkey)
    probability = 0.0

    try:
        model         = joblib.load(settings.MODEL_PATH)
        scaler        = joblib.load(settings.SCALER_PATH)
        feature_names = joblib.load(settings.FEATURES_PATH)

        df = pd.DataFrame([{
            'Age': loan.age,
            'Income': float(loan.income),
            'LoanAmount': float(loan.loan_amount),
            'CreditScore': loan.credit_score,
            'MonthsEmployed': loan.months_employed,
            'NumCreditLines': loan.num_credit_lines,
            'InterestRate': float(loan.interest_rate),
            'LoanTerm': loan.loan_term,
            'DTIRatio': float(loan.dti_ratio),
            'Education': loan.education,
            'EmploymentType': loan.employment_type,
            'MaritalStatus': loan.marital_status,
            'HasMortgage': 'Yes' if loan.has_mortgage else 'No',
            'HasDependents': 'Yes' if loan.has_dependents else 'No',
            'LoanPurpose': loan.loan_purpose,
            'HasCoSigner': 'Yes' if loan.has_cosigner else 'No'
        }])

        enc    = pd.get_dummies(df)
        enc    = enc.reindex(columns=feature_names, fill_value=0)
        scaled = scaler.transform(enc)

        prob_default = model.predict_proba(scaled)[0][1]
        probability   = round((1 - prob_default) * 100, 2)

    except Exception as e:
        print("Probability Error: ", e)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            loan.status = 'Approved'
            loan.save()
        elif action == 'reject':
            loan.status = 'Rejected'
            loan.save()
        return redirect('admin_status_detail', passkey=passkey)

    return render(request, 'admin_status_detail.html', {
        'loan': loan,
        'probability': probability
    })

@csrf_exempt
def submit_loan_request(request):
    if request.method == 'POST':
        dob_y = request.POST.get('dob_year')
        dob_m = request.POST.get('dob_month')
        dob_d = request.POST.get('dob_day')
        dob   = datetime.strptime(f"{dob_y}-{dob_m}-{dob_d}", "%Y-%m-%d")
        age   = datetime.now().year - int(dob_y)

        months_employed   = int(request.POST.get('months_employed_year') or 0) * 12 \
                          + int(request.POST.get('months_employed_month') or 0)
        income            = safe_float(request.POST.get('income'))
        loan_amount       = safe_float(request.POST.get('loan_amount'))
        annual_income     = safe_float(request.POST.get('annual_income'), 1)
        total_loan_amount = safe_float(request.POST.get('total_loan_amount')) \
                          + safe_float(request.POST.get('total_mortgage_amount'))
        dti_ratio         = total_loan_amount / annual_income if annual_income else 0

        settings_obj  = BankSettings.objects.first()
        interest_rate = settings_obj.interest_rate if settings_obj else 5.00

        passkey = ''.join(random.choices('0123456789', k=6))
        loan    = LoanRequest.objects.create(
            loan_id               = request.POST.get('loan_id', f"LN{random.randint(1000,9999)}"),
            first_name            = request.POST.get('first_name'),
            last_name             = request.POST.get('last_name'),
            dob                   = dob,
            age                   = age,
            income                = income,
            annual_income         = annual_income,
            loan_amount           = loan_amount,
            credit_score          = int(request.POST.get('credit_score') or 0),
            months_employed       = months_employed,
            num_credit_lines      = int(request.POST.get('num_credit_lines') or 0),
            interest_rate         = interest_rate,
            loan_term             = int(request.POST.get('loan_term') or 0),
            dti_ratio             = dti_ratio,
            education             = request.POST.get('education', 'High School'),
            employment_type       = request.POST.get('employment_type', 'Full-Time'),
            marital_status        = request.POST.get('marital_status', 'Single'),
            other_loans           = request.POST.get('other_loans') == 'Yes',
            total_loan_amount     = total_loan_amount,
            has_mortgage          = request.POST.get('has_mortgage') == 'Yes',
            total_mortgage_amount = safe_float(request.POST.get('total_mortgage_amount')),
            has_dependents        = request.POST.get('has_dependents') == 'Yes',
            loan_purpose          = request.POST.get('loan_purpose', 'Other'),
            has_cosigner          = request.POST.get('has_cosigner') == 'Yes',
            verification_passkey  = passkey
        )
        return render(request, 'status.html', {
            'loan': loan,
            'passkey': passkey
        })
    return redirect('loan_request')

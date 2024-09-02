from django.shortcuts import render
from django.http import HttpResponse
from .utils import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import NotificationSetting
from .forms import NotificationSettingForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.core.management.base import BaseCommand

def index(request):
    return HttpResponse("Welcome to Report Analysis")

def summary_report(request):
    if request.method == 'POST':
        # Generate the summary report
        report_file_path = generate_summary_report(request)

        # Prepare response to download the generated report
        with open(report_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_file_path)}"'

        # Redirect to summary page with visualization
        return redirect('summary_report')  # Use the correct name 'summary_report'

    # Render the initial form or page where user triggers report generation
    return render(request, 'reports/generate_report.html')


def settings(request):
    return render(request, 'reports/settings.html')

def generate_summary_report(request):
    report_file_path = 'summary_report.xlsx'
    process_excel(report_file_path, request)  # Pass the request object to process_excel
    return report_file_path

@login_required
def notification_settings(request):
    settings = NotificationSetting.objects.filter(user=request.user)
    form = NotificationSettingForm()

    if request.method == 'POST':
        form = NotificationSettingForm(request.POST)
        if form.is_valid():
            setting = form.save(commit=False)
            setting.user = request.user
            setting.save()
            return redirect('notification_settings')

    context = {
        'settings': settings,
        'form': form
    }
    return render(request, 'reports/notification_settings.html', context)

def upload_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        
        # Save the uploaded file temporarily
        file_path = handle_uploaded_file(excel_file)
        
        if file_path:
            # Process the uploaded file
            success, message = process_excel(file_path)
            
            # Delete the temporary file after processing
            os.remove(file_path)
            
            if success:
                return HttpResponse(f"File processed successfully: {message}")
            else:
                return HttpResponse(f"Error processing file: {message}")
        else:
            return HttpResponse("Error saving uploaded file.")

    print("Rendering upload.html template...")  # Add this line for debugging
    return render(request, 'reports/upload.html')

def handle_uploaded_file(uploaded_file):
    try:
        # Define a temporary directory to store uploaded files
        temp_dir = 'uploaded_files/'
        
        # Ensure the directory exists
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create a temporary file path
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Write the uploaded file to the temporary file path
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        return file_path
    except Exception as e:
        print(f"Error handling uploaded file: {str(e)}")
        return None

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form
    }
    return render(request, 'registration/login.html', context)


def weather_report(request):
    city = 'New York'  # Example city
    weather_data = get_weather_data(city)
    if weather_data:
        context = {'weather_data': weather_data}
    else:
        context = {'error_message': 'Failed to fetch weather data.'}
    return render(request, 'reports/weather_reports.html', context)


def currency_conversion(request):
    amount = 100  # Example amount
    from_currency = 'USD'
    to_currency = 'EUR'
    conversion_data = convert_currency(amount, from_currency, to_currency)
    if conversion_data:
        context = {'conversion_data': conversion_data}
    else:
        context = {'error_message': 'Failed to perform currency conversion.'}
    return render(request, 'reports/currency_conversion.html', context)

def send_message_view(request):
    to_number = 'whatsapp:+9195XXXXXXXX'  # Replace with actual recipient's phone number
    message_body = 'Hello Please check your daily sales Analysis reports'
    
    try:
        message_sid = send_whatsapp_message(to_number, message_body)
        return HttpResponse(f'Message sent with SID: {message_sid}')
    except Exception as e:
        return HttpResponse(f'Error sending message: {str(e)}')
    

def generate_report_view(request):
    # Generate daily summary report
    report_file = generate_summary_report(request)
    
    # Save report file to database
    report = Report.objects.create(title='Daily Summary Report', report_file=report_file)
    
    return HttpResponse(f'Report generated and saved: {report_file}')

def send_report_view(request):
    # Get the latest report from the database (assuming there's a single latest report)
    latest_report = Report.objects.latest('generated_at')
    
    # Send email with the latest report attached
    if send_daily_summary_report_email(latest_report.report_file.path):
        return HttpResponse('Report sent via email successfully.')
    else:
        return HttpResponse('Failed to send report via email.')
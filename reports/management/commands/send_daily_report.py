from django.core.management.base import BaseCommand
from reports.utils import generate_summary_report, send_daily_summary_report_email
from reports.models import Report

class Command(BaseCommand):
    help = 'Generates and sends daily summary report'

    def handle(self, *args, **kwargs):
        # Generate daily summary report
        report_file = generate_summary_report()

        # Save report file to database
        report = Report.objects.create(title='Daily Summary Report', report_file=report_file)

        # Send email with the report attached
        if send_daily_summary_report_email(report_file):
            self.stdout.write(self.style.SUCCESS('Successfully sent daily summary report'))
        else:
            self.stdout.write(self.style.ERROR('Failed to send daily summary report'))
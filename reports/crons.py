from django_cron import CronJobBase, Schedule
from django.core.management import call_command

class ReadEmailsCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # every 1 hour

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'reports.read_emails_cron_job'  # a unique code

    def do(self):
        call_command('read_emails')
        

class SendReportCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # every 24 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'reports.send_report_cron_job'  # a unique code

    def do(self):
        call_command('send_report')
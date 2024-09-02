from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail


class SalesData(models.Model):
    store_id = models.CharField(max_length=50)
    date = models.DateField()
    product_id = models.CharField(max_length=50)
    quantity_sold = models.IntegerField()
    total_sales = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class RawData(models.Model):
    store_id = models.CharField(max_length=50)
    date = models.DateField()
    product_id = models.CharField(max_length=50)
    quantity_sold = models.IntegerField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Store {self.store_id} - {self.date}"


class ProcessedData(models.Model):
    date = models.DateField()
    store_id = models.CharField(max_length=50)
    daily_total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    top_selling_product = models.CharField(max_length=100)

    def __str__(self):
        return f"Processed Data for Store {self.store_id} - {self.date}"


class EmailAddress(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class NotificationSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)  # Example: "Sales drop below threshold"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.condition}"


@receiver(post_save, sender='reports.NotificationSetting')
def notification_handler(sender, instance, created, **kwargs):
    if created and instance.is_active:
        # Example: Send email notification
        subject = f"Notification: {instance.condition}"
        message = f"Dear {instance.user.username},\n\n{instance.condition}.\n\nRegards,\nYour Application"
        recipient_list = [instance.user.email]
        send_mail(subject, message, None, recipient_list)
        
class Report(models.Model):
    title = models.CharField(max_length=200)
    report_file = models.FileField(upload_to='reports/%Y/%m/%d/')
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

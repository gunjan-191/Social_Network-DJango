import pandas as pd
from .models import *
from django.core.mail import EmailMessage
from django.conf import settings
import spacy, os 
from textblob import TextBlob
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from twilio.rest import Client
from django.conf import settings
# from django.contrib import messages

nlp = spacy.load("en_core_web_sm")

#################email part
def process_excel(file_path, request):
    try:
        # Ensure the file exists
        if not os.path.exists(file_path):
            return False, "Excel file does not exist."

        # Read Excel file into DataFrame
        df = pd.read_excel(file_path)
        
        # Check if the DataFrame has fewer than 10 rows
        if len(df) < 10:
            print("The Excel file contains fewer than 10 rows of data.")
            return False, "Excel file contains fewer than 10 rows of data."

        # Calculate daily total sales for each store
        daily_sales = df.groupby(['Store ID', 'Date']).agg({'Total Sales': 'sum'}).reset_index()

        # Identify the top-selling product for each store
        top_selling_product = df.groupby(['Store ID', 'Product ID']).agg({'Quantity Sold': 'sum'}).reset_index()
        top_selling_product = top_selling_product.loc[top_selling_product.groupby('Store ID')['Quantity Sold'].idxmax()]
        
        # Merge daily_sales and top_selling_product data
        merged_data = pd.merge(daily_sales, top_selling_product[['Store ID', 'Product ID']], on='Store ID', how='left')
        
        # Save merged_data to CSV for verification
        merged_data.to_csv('daily_sales.csv', index=False)

        # Aggregate the total sales by product across all stores
        total_sales_by_product = df.groupby('Product ID').agg({'Total Sales': 'sum'}).reset_index()

        # Save data to CSV for verification
        top_selling_product.to_csv('top_selling_product.csv', index=False)
        total_sales_by_product.to_csv('total_sales_by_product.csv', index=False)
        
        
        # Create bar chart for daily total sales for each store
        for store_id in daily_sales['Store ID'].unique():
            store_sales = daily_sales[daily_sales['Store ID'] == store_id]
            plt.figure(figsize=(10, 6))
            plt.bar(store_sales['Date'], store_sales['Total Sales'])
            plt.title(f'Daily Total Sales for Store {store_id}')
            plt.xlabel('Date')
            plt.ylabel('Total Sales')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'daily_total_sales_store_{store_id}.png')
            plt.close()

        # Create bar chart for total sales by product
        plt.figure(figsize=(10, 6))
        plt.bar(total_sales_by_product['Product ID'], total_sales_by_product['Total Sales'])
        plt.title('Total Sales by Product')
        plt.xlabel('Product ID')
        plt.ylabel('Total Sales')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('total_sales_by_product.png')
        plt.close()

        print("Excel processing and graph generation complete.")

        # Save raw sales data to the database (RawData model)
        for _, row in df.iterrows():
            raw_data_entry = RawData(
                store_id=row['Store ID'],
                date=row['Date'],
                product_id=row['Product ID'],
                quantity_sold=row['Quantity Sold'],
                total_sales=row['Total Sales']
            )
            raw_data_entry.save()

        # Save processed daily summary data to the database (ProcessedData model)
        for _, row in daily_sales.iterrows():
            processed_data_entry = ProcessedData(
                store_id=row['Store ID'],
                date=row['Date'],
                daily_total_sales=row['Total Sales'],
                top_selling_product=top_selling_product[top_selling_product['Store ID'] == row['Store ID']]['Product ID'].values[0]
            )
            processed_data_entry.save()

        # Save SalesData object
        for _, row in df.iterrows():
            SalesData.objects.create(
                store_id=row['Store ID'],
                date=row['Date'],
                product_id=row['Product ID'],
                quantity_sold=row['Quantity Sold'],
                total_sales=row['Total Sales']
            )

        return True, "Excel file processed successfully."

    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")
        return False, f"Error processing Excel file: {str(e)}"
    
        
def generate_summary_report(request):
    df = pd.DataFrame(list(SalesData.objects.all().values()))
    summary = df.groupby(['store_id', 'date']).agg({
        'quantity_sold': 'sum',
        'total_sales': 'sum'
    }).reset_index()

    report_file = 'summary_report.xlsx'
    summary.to_excel(report_file, index=False)
    return report_file

def send_email_report(request):
    report_file = generate_summary_report(request)
    email = EmailMessage(
        'Daily Sales Summary Report',
        'Please find attached the daily sales summary report.',
        settings.DEFAULT_FROM_EMAIL,
        ['recipient1@example.com', 'recipient2@example.com']
    )
    email.attach_file(report_file)
    email.send()
    
###########email part end here#############

###start of Email Analysis Function@@################
def analyze_email_content(content):
    doc = nlp(content)
    categories = {
        "sales": ["sale", "discount", "offer"],
        "support": ["issue", "problem", "support", "help"],
        "inquiry": ["question", "inquiry", "information"]
    }
    
    email_category = "general"
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in doc.text.lower():
                email_category = category
                break

    # Sentiment analysis using TextBlob
    sentiment_score = TextBlob(content).sentiment.polarity
    if sentiment_score > 0.1:
        sentiment = "positive"
    elif sentiment_score < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    priority = "low"
    if email_category in ["sales", "support"] or sentiment == "negative":
        priority = "high"

    return email_category, sentiment, priority

import requests
def get_weather_data(city):
    api_key = 'token'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'  # Adjust units as needed
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def convert_currency(amount, from_currency, to_currency):
    api_key = 'your_fixer_io_api_key'
    base_url = 'http://data.fixer.io/api/convert'
    params = {
        'access_key': api_key,
        'from': from_currency,
        'to': to_currency,
        'amount': amount
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    


def get_twilio_client():
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    return Client(account_sid, auth_token)

def send_whatsapp_message(to_number, message_body):
    client = get_twilio_client()
    from_number = settings.TWILIO_WHATSAPP_NUMBER

    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number
    )

    return message.sid  # Optionally, you can return message SID for tracking

def send_daily_summary_report_email(report_file_path):
    subject = 'Daily Summary Report'
    message = 'Please find attached the daily summary report.'
    from_email = settings.EMAIL_HOST_USER
    to_emails = ['recipient1@example.com', 'recipient2@example.com']
    
    email = EmailMessage(subject, message, from_email, to_emails)
    
    # Attach the report file
    with open(report_file_path, 'rb') as f:
        email.attach(os.path.basename(report_file_path), f.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


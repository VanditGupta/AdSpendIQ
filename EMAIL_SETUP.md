# 📧 Email Alert Setup for Master Portfolio Pipeline

## 🎯 Overview

The `master_portfolio_pipeline_dag.py` now includes comprehensive email alerting for:
- **Pipeline Start**: Notification when the portfolio pipeline begins
- **Pipeline Completion**: Success notification when all phases complete

## ⚙️ Configuration

### 1. Update Email Recipients

Edit your `.env` file and update the `EMAIL_RECIPIENTS` variable:

```bash
EMAIL_RECIPIENTS=your.email@example.com,team.email@company.com
```

**Note**: Multiple emails can be separated by commas.

### 2. Airflow Email Configuration

Add these environment variables to your `.env` file:

```bash
# Email Configuration
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT=587
AIRFLOW__SMTP__SMTP_USER=your-email@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD=your-app-password
AIRFLOW__SMTP__SMTP_MAIL_FROM=your-email@gmail.com
AIRFLOW__SMTP__SMTP_STARTTLS=True
AIRFLOW__SMTP__SMTP_SSL=False
```

### 3. Gmail App Password Setup

For Gmail, you'll need to create an App Password:

1. Go to Google Account Settings
2. Enable 2-Factor Authentication
3. Generate App Password for "Mail"
4. Use the generated password in `SMTP_PASSWORD`

## 📧 Email Templates

### Pipeline Start Alert
- **Subject**: 🚀 Portfolio Pipeline Started - [Date]
- **Content**: Pipeline overview, objectives, and start time
- **Sent**: Immediately after pipeline initialization

### Pipeline Completion Alert
- **Subject**: 🎉 Portfolio Pipeline Completed Successfully - [Date]
- **Content**: Complete phase status table, technical skills demonstrated
- **Sent**: After all phases complete successfully

## 🚀 Installation

Install the SMTP provider:

```bash
pip install apache-airflow-providers-smtp
```

## 🔍 Testing

Test the email functionality:

```bash
# Test the master DAG
airflow dags test master_portfolio_pipeline_dag 2025-01-15

# Check email tasks specifically
airflow tasks test master_portfolio_pipeline_dag send_start_email 2025-01-15
airflow tasks test master_portfolio_pipeline_dag send_completion_email 2025-01-15
```

## 📋 Email Alert Workflow

```
Pipeline Start → Start Alert Email → Pipeline Execution → Completion Alert Email
     ↓                    ↓                    ↓                    ↓
Initialize → Send Start Email → Run All Phases → Send Completion Email
```

## 🎨 Customization

You can customize the email templates by modifying:
- `send_pipeline_start_alert()` function
- `send_pipeline_completion_alert()` function

Both functions generate HTML content with styling and can be easily modified.

## 🔧 Troubleshooting

### Common Issues:
1. **SMTP Connection Failed**: Check host, port, and credentials
2. **Authentication Failed**: Verify username and app password
3. **Email Not Sent**: Check Airflow logs for error messages

### Debug Commands:
```bash
# Check Airflow configuration
airflow config get-value smtp smtp_host
airflow config get-value smtp smtp_port

# Test email configuration
airflow tasks test master_portfolio_pipeline_dag send_pipeline_start_alert 2025-01-15
```

---

**Note**: Email alerts are now fully integrated into the master portfolio pipeline DAG and will automatically notify you of pipeline status!

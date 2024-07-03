from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from get_data_from_ragic import get_data_by_tag
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 需要設置一個密鑰用於Flask的session

load_dotenv()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            # 連接到 Outlook SMTP 伺服器並驗證登入
            server = smtplib.SMTP('smtp.outlook.com', 587)
            server.starttls()
            server.login(email, password)
            server.quit()
            
            # 如果登入成功，將帳號存入 session 中
            session['email'] = email
            session['password'] = password
            return redirect(url_for('send_email'))
        
        # 登入錯誤，跳出錯誤訊息
        except smtplib.SMTPAuthenticationError:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if 'email' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        recipient_group = request.form.get('recipient_group')
        print("recipient_group: ", recipient_group)
        
        email_content = request.form.get('email_content')
        print("email_content: ", email_content)
        
        if recipient_group and email_content:
            customers = get_data_by_tag(recipient_group)
            if customers:
                print(f"customer:\n{customers}")
                success = send_emails_to_customers(customers, email_content)
                if success:
                    return redirect(url_for('send_email', status='sent'))
                else:
                    return redirect(url_for('send_email', status='error'))
    
    return render_template('send_email.html')

def send_emails_to_customers(customers, content):
    email = session['email']
    password = session['password']

    try:
        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login(email, password)

        for customer in customers:
            receiver_email = customer['email']
            receiver_name = customer['name']
            print(f'Sending email to {receiver_name} : {receiver_email}')

            message = MIMEMultipart("alternative")
            message["Subject"] = "Important Notice"
            message["From"] = email
            message["To"] = receiver_email
            
            html_content = content.replace('{receiver_name}', receiver_name)
            message.attach(MIMEText(html_content, "html"))
            
            try:
                server.sendmail(email, receiver_email, message.as_string())
                print(f'Email sent to {receiver_email} successfully')
            except Exception as e:
                print(f'Failed to send email to {receiver_email}. Error: {str(e)}')
                continue

        server.quit()
        return True
    
    except Exception as e:
        print(f'Send mail failed. Error message: {str(e)}')
        return False

if __name__ == '__main__':
    app.run(debug=True)

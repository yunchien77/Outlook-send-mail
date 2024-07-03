from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from cfp import EmailSender  # Assuming EmailSender is a custom class handling email configuration

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 需要設置一個密鑰用於Flask的session

# 初始化 EmailSender，使用 config.ini 中的設定
#sender = EmailSender('config.ini')

def send_emails(file_name, email, password):
    if not os.path.isfile(file_name):
        print('File not found')
        return False
    
    if file_name.endswith('.xlsx'):
        df = pd.read_excel(file_name)
    elif file_name.endswith('.csv'):
        df = pd.read_csv(file_name)
    else:
        print('File type not supported')
        return False
    
    print('Start sending emails...')
    
    with open(r'template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    print('Template read success')

    try:
        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login(email, password)
        print('Login success')

        for index, row in df.iterrows():
            receiver_email = row['Email']
            receiver_name = row['Name']
            print(f'Sending email to {receiver_name} : {receiver_email}')

            message = MIMEMultipart("alternative")
            message["Subject"] = "Email Test"
            message["From"] = email  # Use the logged in email as the sender
            message["To"] = receiver_email
            
            html = template.replace('{receiver_name}', receiver_name)
            message.attach(MIMEText(html, "html"))
            
            try:
                server.sendmail(email, receiver_email, message.as_string())
                print(f'Email sent to {receiver_email} successfully')
            except Exception as e:
                print(f'Failed to send email to {receiver_email}. Error: {str(e)}')
                continue

        server.quit()
        print('All emails sent!')
        return True
    
    except Exception as e:
        print(f'Send mail failed. Error message: {str(e)}')
        return False


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
        file_name = request.form['file_name']
        email = session['email']
        password = session['password']
        
        success = send_emails(file_name, email, password)
        
        if success:
            return redirect(url_for('send_email', status='sent'))
        else:
            return redirect(url_for('send_email', status='error'))
    
    return render_template('send_email.html')



if __name__ == '__main__':
    app.run(debug=True)

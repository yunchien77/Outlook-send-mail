from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from get_data_from_ragic import get_data_by_tag
from dotenv import load_dotenv
from pypinyin import lazy_pinyin

app = Flask(__name__)
app.secret_key = 'your_secret_key'

load_dotenv()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            server = smtplib.SMTP('smtp.outlook.com', 587)
            server.starttls()
            server.login(email, password)
            server.quit()

            session['email'] = email
            session['password'] = password
            return redirect(url_for('send_email'))
        except smtplib.SMTPAuthenticationError:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if 'email' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        recipient_group = request.form.get('recipient_group')
        email_subject = request.form.get('email_subject')
        email_content = request.form.get('email_content')
        #attachment = request.files['attachment']
        attachments = request.files.getlist('attachments')

        if recipient_group and email_subject and email_content:
            attachment_paths = []
            for attachment in attachments:
                if attachment and allowed_file(attachment.filename):
                    #filename = secure_filename(attachment.filename)
                    #filename = attachment.filename
                    #filename = secure_filename(os.path.basename(attachment.filename))
                    filename = secure_filename(''.join(lazy_pinyin(attachment.filename)))
                    print("***", filename)
                    
                    attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    attachment.save(attachment_path)
                    attachment_paths.append(attachment_path)

            customers = get_data_by_tag(recipient_group)
            if customers:
                success = send_emails_to_customers(customers, email_subject, email_content, attachment_paths)
                if success:
                    return redirect(url_for('send_email', status='sent'))
                else:
                    return redirect(url_for('send_email', status='error'))

    return render_template('send_email.html')

def send_emails_to_customers(customers, subject, content, attachment_paths):
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
            message["Subject"] = subject
            message["From"] = email
            message["To"] = receiver_email

            html_content = content.replace('\n', '<br>').replace('{receiver_name}', receiver_name)
            message.attach(MIMEText(html_content, "html"))

            # 如果有上傳附件
            for attachment_path in attachment_paths:
                with open(attachment_path, "rb") as attachment_file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {os.path.basename(attachment_path)}",
                    )
                    message.attach(part)

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
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

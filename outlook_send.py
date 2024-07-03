from email.message import EmailMessage
import smtplib

sender = "cherry.yeh@cancerfree.io"
recipient = "emailjustforyouuuuu@gmail.com"
message = '''
Hello World!
Nice to meet you!

by Cherry
'''

email = EmailMessage()
email["From"] = sender
email["To"] = recipient
email["Subject"] = "Test Email"
email.set_content(message)

smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
smtp.starttls()
smtp.login(sender, "@HCYyu0207")
print('login success')
smtp.sendmail(sender, recipient, email.as_string())
smtp.quit()
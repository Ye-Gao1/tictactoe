import discord, os, smtplib
from discord import app_commands
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TOKEN = os.environ['Token']
EMAIL_ADDRESS = 'Yeg7311@gmail.com'
EMAIL_PASSWORD = os.environ['email']

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def send_email(to_email, name, user_message):
    print("Setting up SMTP connection...")
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    print("SMTP connection established successfully.")

    msg = MIMEMultipart()
    subject = f"Message from {name}"
    msg_body = user_message

    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(msg_body, 'plain'))
    print(f"Prepared email for {to_email} with subject: {subject}")
    mail.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())


@tree.command(name="mail", description="Send an email via Gmail")
async def send_mail(interaction: discord.Interaction, email: str, name: str, message: str):
    print(f"Received command to send email to {email} with name {name}")
    send_email(email, name, message)
    await interaction.response.send_message(f"Email sent to {email} successfully!")

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user} and slash commands are ready.')

client.run(TOKEN)

import time,sys, smtplib, json, request
from coinbase.wallet.client import Client 
from requests.auth import AuthBase		 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

below = 0   	#If bitcoin price is below this #, send me a alert (change over to 0)
over = 0 	#If bitcoin price is under this #, send me a alert (change below to 0)
braked = False		#A variable that doesnt let the program constantly email me
goingUp = False		#if its went past the "below" (which tells me to buy) and is now going up, this will be true and will reset the alerter
goingDown = False 	#if its went past the "over" (which tells me to sell) and is now going up, this will be true and will reset the alerter
i = 0

#Email Addresses + Messages:
senderEmail = "Your Email"
receiverEmail = "your email password"
senderPass = "Your Email Password"
msg = MIMEMultipart()
msg['From'] = senderEmail
msg['To'] = receiverEmail 

#Autharizing Coinbase API:
API_KEY = 'GET THE KEY FROM COINBASE'	 #Get API KEY, API SECRET, and API version from coinbase
API_SECRET = 'GET THE KEY FROM COINBASE'
class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        })
        return request
def checkAndEmail():
	global braked, goingDown, goingUp
	if (price<below) and (over == 0):
		x = "Alert: below %s" %below
		msg['Subject'] = x
		body = "BUY" 
		braked = True
		goingDown = True
		print(x)
		emailMe(body)
	if (price>over) and (below == 0):
		x = "Alert: OVER %s" %over
		msg['Subject'] = x
		body = "SELL" #Email Body
		braked = True
		goingUp = True
		print(x)
		emailMe(body)
	elif (price<below) and (price>over) and (below != 0) and (over != 0):
		x = "Alert: BETWEEN %s and %s" %(over, below)
		msg['Subject'] = x
		body = "SAFE?" 
		braked = True
		print(x)
		emailMe(body)
def emailMe(body):
	print("sending...")
	sys.stdout.write(str(braked)+"_2    ")
	msg.attach(MIMEText(body, 'plain'))
	text = msg.as_string()			
	#Logging Into Sender's Email:
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(senderEmail, senderPass) 
	#Send Email:
	server.sendmail(senderEmail, receiverEmail, text)
	print("sent")
	server.quit()

print("MONITORING...")
client = Client(API_KEY, API_SECRET, api_version='2018-01-24')
currency_code = 'USD' 
while True:
	price = client.get_spot_price(currency=currency_code)
	price = float(price.amount)
	if (braked == False):
		checkAndEmail()
	if (braked == True):
		if (goingDown == True) and (price>below) and (over == 0): 
			braked = False
			print("Restarting Alerts")
		if (goingUp == True) and (price<over) and (below == 0): 
			braked = False
			print("Restarting Alerts")
	sys.stdout.write(str(i)+"     ")
	print(price)
	i = i+1
	time.sleep(.3)

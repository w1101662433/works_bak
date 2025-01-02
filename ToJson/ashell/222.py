from libs.print_error_info import *

url = 'https://sandbox-api.digikey.com/v1/oauth2/token'
data = dict(
    code='cDdv3ijb',
    client_id="SUA9LIOtOKW4OuG8QA7ntJdORvE9emff",
    client_secret="u32nOnZPNtFv8e8r",
    redirect_uri="https://www.fivcan.com/de_jie_webhook/",
    grant_type='authorization_code',
)
res = requests.post(url=url, data=data)
print(res.text)

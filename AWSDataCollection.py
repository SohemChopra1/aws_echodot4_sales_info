import requests
import datetime
import hashlib
import hmac
import json

# Variables (sensitive ones such as access_key, secret_key, and associate_tag are not put to protect my AWS info)
access_key = 'access_key'
secret_key = 'secret_key'
associate_tag = 'associate_tag'

endpoint = 'webservices.amazon.com'
uri = '/paapi5/searchitems'
region = 'us-east-2'

#First step in signing request to aws
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def create_signed_request(params, access_key, secret_key):
    method = 'POST'
    service = 'ProductAdvertisingAPI'
    host = f'{service}.{region}.amazonaws.com'
    content_type = 'application/json; charset=utf-8'
    request_parameters = json.dumps(params)

    #Time series algorithm 
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')  

    #Cannonical request setup 
    canonical_uri = uri
    canonical_querystring = ''
    canonical_headers = f'content-type:{content_type}\nhost:{host}\nx-amz-date:{amz_date}\n'
    signed_headers = 'content-type;host;x-amz-date'
    payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()

    canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{datestamp}/{region}/{service}/aws4_request'
    string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'

    # get signing information 
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

    # add signing ifnormation to aws request
    authorization_header = f'{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'

    headers = {
        'Content-Type': content_type,
        'X-Amz-Date': amz_date,
        'Authorization': authorization_header,
    }

    return headers

def lookup_item(keywords):
    url = f'https://{endpoint}{uri}'
    params = {
        "Keywords": keywords,
        "PartnerTag": associate_tag,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.com"
    }
    headers = create_signed_request(params, access_key, secret_key)
    

    print("Request URL:", url)
    print("Request Headers:", headers)
    print("Request Params:", params)
    response = requests.post(url, headers=headers, json=params)
    
    print("Response Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Response Text:", response.text)
    
    return response.json()

if __name__ == '__main__':
    keywords = "Echo Dot (4th Gen) - Smart speaker with Alexa"
    response = lookup_item(keywords)
    print(response)

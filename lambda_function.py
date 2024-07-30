import json
import boto3
import qrcode
import io
import base64

# Initialize a session using Amazon S3
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parse the URL from the event
    body = json.loads(event['body'])
    url = body['url']
    
    # Generate QR code with specified colors
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="red", back_color="black")
    
    img_bytes = io.BytesIO()
    img.save(img_bytes)
    img_bytes = img_bytes.getvalue()
    
    # Generate a unique filename
    filename = url.split("://")[1].replace("/", "_") + '.png'
    
    # Upload the QR code to the S3 bucket
    s3.put_object(Bucket='qr-code-generator8', Key=filename, Body=img_bytes, ContentType='image/png', ACL='public-read')
    
    # Generate the URL of the uploaded QR code
    location = s3.get_bucket_location(Bucket='qr-code-generator8')['LocationConstraint']
    qr_code_url = f"https://qr-code-generator8.s3.amazonaws.com/{filename}"
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps({'message': 'QR code generated and uploaded to S3 bucket successfully!', 'qr_code_url': qr_code_url})
    }
import json
import boto3
import zipfile
from io import StringIO
from io import BytesIO
import mimetypes
import boto3

def lambda_handler(event, context):
   
    try:
        s3 = boto3.resource("s3")
        portfolio_bucket = s3.Bucket("andrewmtyler-portfolio")
        build_bucket =s3.Bucket('andrewmtyler-portfolio-build')
         
        sns = boto3.resource('sns')
        topic = sns.Topic('arn:aws:sns:us-east-1:822803490390:PortfolioUpdated')
        
        portfolio_zip = BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                
                
        topic.publish(Subject="Portfolio Updated", Message="Your portfolio has been updated")
    
    except:
        topic.publish(Subject="Portfolio Update Failed", Message="The portfolio update has failed")
        raise

    return "completed deploy!"
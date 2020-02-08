import json
import boto3
import zipfile
from io import StringIO
from io import BytesIO
import mimetypes
import boto3

def lambda_handler(event, context):
   
    try:
        location = {
            "bucketName" : 'andrewmtyler-portfolio-build',
            "objectKey" : 'portfoliobuild.zip'
        }
        
        s3 = boto3.resource("s3")
        portfolio_bucket = s3.Bucket("andrewmtyler-portfolio")
        
        
        sns = boto3.resource('sns')
        topic = sns.Topic('arn:aws:sns:us-east-1:822803490390:PortfolioUpdated')
        
        job = event.get("CodePipeline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                print ('Found Artifact')
                print (artifact["name"])
                if artifact["name"] == "BuildArtifact":
                    location = artifact["location"]["s3Location"]
                    
        print ('Building portfolio from location ' + str(location))
                    
        build_bucket =s3.Bucket(location["bucketName"])
        
        portfolio_zip = BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                
                
        topic.publish(Subject="Portfolio Updated", Message="Your portfolio has been updated")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job['id'])
    
    except:
        topic.publish(Subject="Portfolio Update Failed", Message="The portfolio update has failed")
        raise

    return "completed deploy!"
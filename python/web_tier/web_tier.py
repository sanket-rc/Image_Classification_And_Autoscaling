from flask import Flask , request
import boto3
import aws_resources
#from botocore.config import Config
import traceback

app = Flask(__name__)

@app.route('/', methods=['POST'])
def upload_image():

    if 'myfile' not in request.files:
        return { 'message': 'missing required img param' }, 400

    # Get file
    myfile = request.files['myfile']

    
    for myfile in request.files.getlist('myfile'):
        try:
            aws_resources.save_img_to_bucket(myfile.stream, myfile.filename)
            aws_resources.send_img_request_to_sqs(myfile.filename)
            print("Image saved to the Input Bucket and request send to input Queue")
        except:
            traceback.print_exc()
            return { 'message': 'Internal server error' }, 500
    
    return {'message' : 'Images uploaded successfully!'}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

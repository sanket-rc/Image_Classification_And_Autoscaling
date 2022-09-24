from flask import Flask , request
import aws_resources
import datetime
import traceback

app = Flask(__name__)

@app.route('/', methods=['POST'])
def upload_image():

    if 'myfile' not in request.files:
        return { str(datetime.datetime.now()) + ' message': 'missing required img param' }, 400

    # Get file
    myfile = request.files['myfile']

    
    for myfile in request.files.getlist('myfile'):
        try:
            # Save the input image to the Bucket and the Request Queue
            aws_resources.save_img_to_bucket(myfile.stream, myfile.filename)
            aws_resources.send_img_request_to_sqs(myfile.filename)
            print(str(datetime.datetime.now()) + " Image saved to the Input Bucket and request send to input Queue")
            
        except:
            traceback.print_exc()
            return { str(datetime.datetime.now()) + 'message': 'Internal server error' }, 500
    
    return {str(datetime.datetime.now()) + ' message' : 'Images uploaded successfully!'}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

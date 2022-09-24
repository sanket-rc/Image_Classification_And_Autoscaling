from genericpath import isfile
from flask import Flask , request
import aws_resources
import datetime
import time
import traceback
import os

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
            request_id = aws_resources.send_img_request_to_sqs(myfile.filename)
            print(str(datetime.datetime.now()) + " Image saved to the Input Bucket and request send to input Queue")
            max_attempts = 100
            attempt = 0
            response = None
            while attempt<max_attempts:
                if os.path.isfile(f"output/{request_id}.txt"):
                    with open(f"output/{request_id}.txt") as f:
                        response = f.read()
                        break
                attempt += 1
                time.sleep(10)
            if response:
                os.remove(f"output/{request_id}.txt")
                return {str(datetime.datetime.now()) + ' message' : f'Classification result: {response}'}, 200
            else:
                return {str(datetime.datetime.now()) + ' message' : f'Max attempts exceeded. Response not found.'}, 400
        except:
            traceback.print_exc()
            return { str(datetime.datetime.now()) + 'message': 'Internal server error' }, 500
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

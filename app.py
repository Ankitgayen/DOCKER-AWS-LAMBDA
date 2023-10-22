from selenium import webdriver
from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras import layers
from tempfile import mkdtemp
import tensorflow as tf 
import numpy as np
import base64
import warnings
import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
warnings.filterwarnings("ignore")




new = load_model('captcha_recognition_model.h5')

characters =   ['0', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'n', 'p', 'r', 't', 'w', 'x', 'y']
max_length = 6

char_to_num = layers.StringLookup(
    vocabulary=list(characters), mask_token=None
)
num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True
)
img_width = 200
img_height = 50

def decode_batch_predictions(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
        :, :max_length
    ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = tf.strings.reduce_join(num_to_char(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text

def get_demo(img_path):
    img = tf.io.read_file(img_path)
    img = tf.io.decode_png(img, channels=1)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, [img_height, img_width])
    img = tf.transpose(img, perm=[1, 0, 2])
    return img

def lambda_handler(event, context):
    decodedevent = json.loads(event['body'])
    search = decodedevent['gst_no']
    # gst = event['base']
    # TODO implement
    result = GOOGLE(search)
    # TODO implementation
 
    return {
        'headers': {'Content-Type' : 'application/json'},
        'statusCode': 200,
        # 'body': json.dumps({"message": "Lambda Container image invoked!",
                            # "event": event})
        'body':result
    }

def GOOGLE(search):
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=options, service=service)
    # driver.implicitly_wait(30)
    driver.maximize_window()
    path = "https://www.google.com/"
    base_url = path
    driver.get(base_url)
    driver.implicitly_wait(2)
    # gst = "24ablpa0067f1z7"
    driver.find_element(By.XPATH,'//*[@id="APjFqb"]').send_keys(search)
    time.sleep(2)
    def cap():
        #time.sleep(1)
        ## first create a temp file before storing images 
        os.chdir('/tmp')
        if not os.path.exists(os.path.join('mydir')):
            os.makedirs('mydir')
        img_base64 = driver.execute_script("""
            var ele = arguments[0];
            var cnv = document.createElement('canvas');
            cnv.width = ele.width; cnv.height = ele.height;
            cnv.getContext('2d').drawImage(ele, 0, 0);
            return cnv.toDataURL('image/jpeg').substring(22);    
            """, driver.find_element(By.XPATH,"//*[@id=\"imgimage\"]"))
        
        ## use /tmp to save image in aws lambda
        with open(r"/tmp/image.png", 'wb') as f:
            f.write(base64.b64decode(img_base64))

        ## using a trained model to convert images to string.
        path = '/tmp/image.png'
        image1 = get_demo(path)
        image1 = tf.expand_dims(image1, axis=0)
        preds = new.predict(image1)
        pred_texts = decode_batch_predictions(preds)
        result = pred_texts[0]
        driver.find_element(By.XPATH,"//*[@id=\"fo-captcha\"]").send_keys(result)
        time.sleep(2)
        driver.find_element(By.XPATH,"//*[@id=\"lotsearch\"]").click()
        
    cap()
    
   
    data = {

        "result":"SUCCESSFULLY SEARCHED AND DOWNLOADED IMAGE"
        
    }
    

    driver.close()
    return data

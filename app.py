from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import os

# token should be in user_hash otherwise the current user is not allowed to access page
def ahash(path):
    '''
    ahash algorithm to compute hashcode of image
    :param path:
    :return:
    '''
    # 1. convert current image to gray-scale image
    image = cv2.imread(path)
    image = cv2.resize(image, (16, 16), interpolation=cv2.INTER_CUBIC)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # 2. compute average of pixel values
    total = 0
    for i in range(16):
        for j in range(16):
            total = total + image[i, j]
    avg = total / 256
    # 3. compare each pixel and average value
    # if pixel value is not less than average, mark as 1
    # otherwise, mark as 0
    result = ''
    for i in range(16):
        for j in range(16):
            if image[i, j] >= avg:
                result += '1'
            else:
                result += '0'
    return result

def cal_hamming_dist(hash1, hash2):
    '''
    compute hamming distance of two input hashcodes
    :param hash1:
    :param hash2:
    :return:
    '''
    hamming_dist = 0
    if len(hash1) != len(hash2):
        return -1
    for i in range(len(hash1)):
        if hash1[i] != hash2[i]:
            hamming_dist += 1
    return hamming_dist

app = Flask(__name__)
app.config['DEBUG'] = True

user_name = ['John']
user_hash = set()
for name in user_name:
    user_hash.add(str(hash(name)))
print('The available tokens are: {}'.format(user_hash))

# allowed extension for input images
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/compare/<string:token>', methods=['POST', 'GET'])
def compare(token):
    '''
    input two files and calculate similarity between them
    :return:
    '''
    # if user token is not in authorized sheet, it is not allowed to access page
    if token not in user_hash:
        return jsonify({'msg': 'You are not authorized to access this page.'})

    if request.method == 'POST':

        # obtain two input files
        file1, file2 = request.files['file1'], request.files['file2']

        # if file is empty or the extension is not allowed, return json message
        if not file1 or not allowed_file(file1.filename):
            return jsonify({'msg': 'The input file 1 is illegal.'})
        if not file2 or not allowed_file(file2.filename):
            return jsonify({'msg': 'The input file 2 is illegal.'})

        # generate filenames of two files and save them
        cur_path = os.path.dirname(__file__)
        filename1, filename2 = secure_filename(file1.filename), secure_filename(file2.filename)
        path = cur_path + '/static/img/'
        file1_path, file2_path = os.path.join(path, filename1), os.path.join(path, filename2)
        file1.save(file1_path)
        file2.save(file2_path)

        # compute hashcodes of two images and compare them using ahash algorithm
        hash1, hash2 = ahash(file1_path), ahash(file2_path)
        result = cal_hamming_dist(hash1, hash2)
        similarity = 1 - result / 256

        return render_template('compare.html', file1=file1.filename, file2=file2.filename, result=similarity)

    return render_template('compare.html', file1=None, file2=None, result=0)


if __name__ == '__main__':
    app.run()

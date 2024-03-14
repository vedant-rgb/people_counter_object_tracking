from flask import Flask, render_template, jsonify, request
import os

from roboflow import Roboflow

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
allowed_extensions = {'mp4'}
filename=""
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def server():
    return render_template('upload_form.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():

    global filename

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    else:
        return jsonify({"error": "File type not permitted"}), 400

@app.route('/api/predict')
def predict():

    global filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": f"File not found: {filename}"})

    try:
        rf = Roboflow(api_key="2dbsmAHtO3IDId2Qnbj5")
        project = rf.workspace().project("person_detection-b9e6g")
        model = project.version("7").model

        job_id, signed_url, expire_time = model.predict_video(
            file_path,  # Use uploaded file path
            fps=5,
            prediction_type="batch-video",

        )

        results = model.poll_until_video_results(job_id)
        up = 0
        down = 0
        n = len(results)
        for i in range(n):
            m = len(results['person_detection-b9e6g'][i]['predictions'])
            for j in range(m):
                cls = results['person_detection-b9e6g'][i]['predictions'][j]['class']
                if cls == 'Up':
                    up += 1
                else:
                    down += 1

        data={"dataup":up,"datadown":down}
        return render_template("index.html",data=data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)

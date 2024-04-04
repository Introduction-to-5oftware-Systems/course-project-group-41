from flask import Flask, render_template,request,jsonify,make_response, send_file
from flask import url_for
from io import BytesIO
import json
import bcrypt
import psycopg2
from psycopg2 import Binary
from werkzeug.utils import secure_filename
import os
import base64
from flask import redirect
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
     create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from uuid import uuid4
from subprocess import Popen
import cv2
from moviepy.editor import VideoClip, concatenate_videoclips, AudioClip, VideoFileClip, AudioFileClip, CompositeVideoClip
import ast

sql_link = os.environ.get('SQL_LINK')

app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

selected_transition = "crossfadein"
selected_duration = 5
selected_resolution = (1920, 1080)
selected_audio = "audio1.mp3"
selected_dur = "5"


@app.route('/')
def home():
    return render_template('index.html')
@app.route('/loginPage')
def loginPage():
    return render_template('loginPage.html')
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_decoded = hashed_password.decode('utf-8')
        
        email = request.form.get('email')
        # user_details = {
        #     'username': username,
        #     'email': email,
        #     'password': hashed_password_decoded
        # }

        db_connector = psycopg2.connect(sql_link)

        user_db = db_connector.cursor()

        command = "SELECT COUNT(user_id) FROM issproject.user_details;"
        user_db.execute(command)
        count = user_db.fetchone()[0] + 1

        insert_query = "INSERT INTO user_details (user_id, username, email, password, user_images) VALUES (%s, %s, %s, %s, %s);"
        user_data = (count, username, email, hashed_password_decoded, 0)
        user_db.execute(insert_query, user_data)
        db_connector.commit()
        user_db.close()
        db_connector.close()

        # with open('users.txt') as f:
        #     users=json.load(f)
        # users+=[user_details]
        # with open('users.txt', 'w') as f:
        #     json.dump(users, f)
        
        return render_template('loginPage.html')
                
@app.route('/signUpPage', methods=['GET'])
def signUpPage():
    return render_template('signupPage.html')
    

# Setup the Flask-JWT-Extended extension
  # Change this!

@app.route('/api/upload_images', methods=['POST'])
@jwt_required()
def upload_images():
    current_user = get_jwt_identity()
    if 'images' not in request.files:
        return 'No image file part in the request', 400
    files = request.files.getlist('images')
    for file in files:
        if file.filename == '':
            return 'No selected file', 400
        db_connector = psycopg2.connect(sql_link)
        user_db = db_connector.cursor()
        query = "UPDATE user_details SET user_images = user_images + 1 WHERE username = %s"
        user_db.execute(query, (current_user,))
        db_connector.commit()
        query = "SELECT user_id FROM user_details WHERE username = %s"
        user_db.execute(query, (current_user,))
        user_id = user_db.fetchall()[0][0]
        command = "SELECT COUNT(image_id) FROM issproject.images;"
        user_db.execute(command)
        count = user_db.fetchone()[0] + 1
        file_contents = file.read()
        binary_data = BytesIO(file_contents).read()
        # file_path = os.path.join(app.config['/images'], file.filename)
        # file.save(file_path)
        # f = open(file_path, "rb")
        # image_data = f.read()
        insert_query = "INSERT INTO images (image_id, user_id, image_metadata, image) VALUES (%s, %s, %s, %s)"
        image_metadata = file.filename  # Provide the image metadata here
        image_values = (count, user_id, image_metadata, Binary(binary_data))
        user_db.execute(insert_query, image_values)
        db_connector.commit()
        user_db.close()
        db_connector.close()
    return redirect("/api/upload")

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route('/token/auth', methods=['POST'])
def login():
    
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "adminuser" and password == "ishjaiesh":
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            resp = jsonify({'login': True})
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            response= make_response(redirect('/api/admin'))
            response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True)
            return response
        if (username == "test" and password == "test"):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            resp = jsonify({'login': True})
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            response= make_response(redirect('/api/upload'))
            response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True)
            return response
        # data = request.get_json()
        # username = data.get('username')
        # password = data.get('password')
        # password_from_database="test"
        #ask question
        db_connector = psycopg2.connect(sql_link)

        user_db = db_connector.cursor()
        query = "SELECT * FROM user_details WHERE username = %s"
        user_db.execute(query, (username,))
        result = user_db.fetchall()
        user_db.close()
        db_connector.close()
        if len(result) == 0:
            return render_template('wrongCreds.html')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        if (bcrypt.checkpw(password.encode('utf-8'), result[0][3].encode('utf-8'))==False):
            return render_template('wrongCreds.html')
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        response= make_response(redirect('/api/upload'))
        response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True)
        return response

       # return  redirect('/api/upload')

@app.route('/token/refresh', methods=['POST'])
@jwt_required("refresh")
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200
@app.route('/token/remove')#methods=['POST']
def logout():
    # resp = jsonify({'logout': True})
    # unset_jwt_cookies(resp)
    # return redirect('/')
    access_token = create_access_token(identity="romil_is_a _midget")
    response= make_response(redirect('/'))
    response.set_cookie('access_token_cookie', value=access_token, max_age=0, httponly=True)
    return response

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.


@app.route('/api/upload',methods=["GET"])
@jwt_required()
def upload():
    current_user = get_jwt_identity()
    # db_connector = psycopg2.connect(sql_link)
    # user_db = db_connector.cursor()    
    # query = "UPDATE user_details SET user_images = user_images + 1 WHERE username = %s"
    # user_db.execute(query, (current_user,))
    # db_connector.commit()
    return render_template('upload.html')

image_list = []

@app.route('/api/video',methods=["GET"])
@jwt_required()

def video():
    current_user = get_jwt_identity()

    # Clear the images folder
    images_folder = 'images'
    if os.path.exists(images_folder):
        for file in os.listdir(images_folder):
            file_path = os.path.join(images_folder, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(images_folder)

    # Delete the output video file
    output_video_file = 'static/images/output_video.mp4'
    if os.path.exists(output_video_file):
        os.remove(output_video_file)

    # Connect to the database
    db_connector = psycopg2.connect(sql_link)
    user_db = db_connector.cursor()    

    # Fetch user images count
    query = "SELECT user_images FROM user_details WHERE username = %s"
    user_db.execute(query, (current_user,))   
    x = user_db.fetchone()  # Since you are fetching a single value

    if x and int(x[0]) > 0:
        # Fetch image data
        query = "SELECT image, image_metadata FROM images WHERE user_id = (SELECT user_id FROM user_details WHERE username = %s)"
        user_db.execute(query, (current_user,))
        image_data = user_db.fetchall()

        # Create a directory if it doesn't exist
        os.makedirs(images_folder, exist_ok=True)
        
        # Clear the existing image_list
        global image_list
        image_list.clear()
        
        # Save each image to the 'images' folder and add to image_list
        for image, image_metadata in image_data:
            image_base64 = base64.b64encode(image).decode('utf-8')
            filename = f"{uuid4()}.png"  # Generate a unique filename
            image_path = os.path.join(images_folder, filename)
            with open(image_path, 'wb') as img_file:
                img_file.write(base64.b64decode(image_base64))
            image_list.append(image_base64)
        user_db.close()
        db_connector.close()
        print("HEllo", len(image_list))
        return render_template('video_Editor.html', image_list=image_list, duration_var=selected_dur, transition_var=selected_transition, resolution_var=selected_resolution)
    else:
        user_db.close()
        db_connector.close()
        return render_template('upload.html', failure_message="You need to upload images.")
    
@app.route('/api/admin',methods=["GET"])
@jwt_required()
def admin():
    current_user = get_jwt_identity()
    if (current_user == "adminuser"):
        db_connector = psycopg2.connect(sql_link)
        user_db = db_connector.cursor()    
        query = "SELECT user_id, username, email, user_images FROM user_details;"
        user_db.execute(query)
        rows = user_db.fetchall() 
        user_db.close()
        db_connector.close()
        return render_template('admin.html', rows=rows)
    else:
        return render_template('loginPage.html', failure_message="Invalid credentials to enter admin page.")
@app.route('/api/output',methods=["GET"])
@jwt_required()
def output():
    current_user = get_jwt_identity()
    return render_template('output.html')

def images_to_video(image_folder, output_video, audio_file, resolution=(1920, 1080), image_duration=2, transition="crossfadein"):
    width, height = resolution

    available_transitions = {
        "crossfadein": lambda clip, start_time: clip.set_start(start_time).crossfadein(0.5),
        "fadein": lambda clip, start_time: clip.set_start(start_time).fadein(0.5),
        # Add more transitions as needed
    }

    image_files = sorted([img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png")])
    clips = []
    transition_func = available_transitions.get(transition, available_transitions["crossfadein"])  # Default to crossfadein if invalid option provided

    total_video_duration = len(image_files) * image_duration

    # Trim audio to match total video duration
    audio = AudioFileClip(audio_file)
    if audio.duration > total_video_duration:
        audio = audio.subclip(0, total_video_duration)

    for idx, image_file in enumerate(image_files):
        image_path = os.path.join(image_folder, image_file)

        # Load the image
        img = cv2.imread(image_path)

        # Calculate the start and end times for the current image clip
        clip_start_time = idx * image_duration
        clip_end_time = (idx + 1) * image_duration

        # Create a clip for the current image
        img_clip = VideoClip(make_frame=lambda t, img=img: img, duration=image_duration)

        # Apply transition if not the first clip
        if idx > 0:
            img_clip = transition_func(img_clip, clip_start_time)

        # Resize the clip to the specified resolution
        resized_clip = img_clip.resize(width=width, height=height)

        # Set the start and end times for the clip
        resized_clip = resized_clip.set_start(clip_start_time).set_end(clip_end_time)

        # Append the resized clip to the list of clips
        clips.append(resized_clip)

    # Concatenate all clips into the final video
    final_clip = concatenate_videoclips(clips, method="compose")

    # Set the audio for the final video
    final_clip = final_clip.set_audio(audio)

    # Write the final video file
    final_clip.write_videofile(output_video, fps=24)  # Adjust fps as needed


@app.route('/duration_selected', methods=['POST'])
def duration_selected():
    global selected_duration
    global selected_dur
    selected_dur = request.form['image_duration']
    selected_duration = int(selected_dur)
    return render_template('video_Editor.html', show_congratulations_button = False, image_list=image_list, audio_var = selected_audio, duration_var=selected_dur, transition_var=selected_transition, resolution_var=selected_resolution)

@app.route('/transition_selected', methods=['POST'])
def transition_selected():
    global selected_transition
    selected_transition = request.form['transition']
    return render_template('video_Editor.html', show_congratulations_button = False, image_list=image_list, audio_var = selected_audio, duration_var=selected_dur, transition_var=selected_transition, resolution_var=selected_resolution)

@app.route('/audio_selected', methods=['POST'])
def audio_selected():
    global selected_audio
    selected_audio = request.form['audio']
    return render_template('video_Editor.html', show_congratulations_button = False, image_list=image_list, audio_var = selected_audio, duration_var=selected_dur, transition_var=selected_transition, resolution_var=selected_resolution)

@app.route('/generate_video', methods=['POST'])
def generate_video():
    global selected_duration, selected_transition, selected_resolution, selected_audio, selected_dur

    image_folder = "images"
    output_video = 'static/images/output_video.mp4'
    # audio_file = "audio3.mp3"

    selected_resolution = request.form['video_resolution']
    selected_resolution = eval(selected_resolution)

    # print(selected_duration, selected_transition, selected_resolution, sep="  ")
    images_to_video(image_folder, output_video,selected_audio, selected_resolution, selected_duration, selected_transition)
    # add_audio_to_video(output_video, audio_file, output_video)

    
    return render_template('video_Editor.html', show_congratulations_button = True, image_list=image_list, audio_var = selected_audio, duration_var=selected_dur, transition_var=selected_transition, resolution_var=selected_resolution)

@app.route('/congratulations')
def congratulations():
    return render_template('output.html')

@app.route('/download_video')
def download_video():
    video_path = 'static/images/output_video.mp4'
    return send_file(video_path, as_attachment=True)


if __name__ == "__main__":
    app.run()

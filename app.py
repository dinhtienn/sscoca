from flask import *
import mlab
from mongoengine import *
from models.count import Count
from models.feedback import Feedback
from models.video import Video
from datetime import datetime
import youtube_dl
import os
import re

app = Flask(__name__)
app.secret_key = "sscoca"
mlab.connect('sscoca-ytdl')

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET': 
        return render_template('index.html')
    elif request.method == 'POST':
        isRight = False
        form = request.form
        link = form['link_yt']
        dl = youtube_dl.YoutubeDL()

        # Check link
        ies = youtube_dl.extractor.gen_extractors()
        for ie in ies:
            if ie.suitable(link) and ie.IE_NAME != 'generic':
                isRight = True
        
        if isRight == True:
            try:
                data = dl.extract_info(link, download=False)
                title = data['title']
                views = data['view_count']
                likes = data['like_count']
                dislikes = data['dislike_count']
                youtube_id = data['id']

                video = Video(
                    title=title,
                    views=views,
                    likes=likes,
                    dislikes=dislikes,
                    youtube_id=youtube_id,
                    link=link,
                    time=datetime.now()
                )

                video.save()
                return render_template('index.html', video=video, template=1)
            except Exception as e:
                return render_template('link-fail.html')
        elif isRight == False:
            return render_template('link-fail.html')

# Download Video
@app.route('/download_video/<youtube_id>')
def download_video(youtube_id):
    # Count
    all_video=[]
    now = datetime.now()
    count_video = Video.objects()
    for video in count_video:
        if video['time'].day == now.day:
            all_video.append(video)
    
    found_count = Count.objects()
    if (len(found_count) > 0) and (found_count[len(found_count)-1]['time'].day == now.day) and (found_count[len(found_count)-1]['time'].month == now.month) and (found_count[len(found_count)-1]['time'].year == now.year):
        number = len(all_video)
        found_count[len(found_count)-1].update(set__amount=number)
    else:
        new_count = Count(
            amount = 1,
            time = now
        )
        new_count.save()
    
    # Download
    found_video = Video.objects.with_id(youtube_id)
    if found_video is not None:
        # Download
        options = {
            'outtmpl': '%(id)s'
        }

        dl = youtube_dl.YoutubeDL(options)
        result = dl.extract_info(
            found_video.link,
            download = True
        )

        # Send File
        save_file = found_video.title.replace(" ", "")
        save_file = re.sub('[^A-Za-z0-9]+', '', save_file)
        os.rename(result['id'], save_file + '.mp4')
        try:
            # Set Download Type
            found_video.update(set__download_type="Video")
            found_video.update(set__time=datetime.now())

            return send_file(save_file + '.mp4', save_file + '.mp4', as_attachment=True)
        except Exception as e:
            return str(e)

        # Delete Video from Database
        # found_video.delete()
    else:
        return 'Video is not found'

# Download Audio
@app.route('/download_audio/<youtube_id>')
def download_audio(youtube_id):
    # Count
    all_video=[]
    now = datetime.now()
    count_video = Video.objects()
    for video in count_video:
        if video['time'].day == now.day:
            all_video.append(video)
    
    found_count = Count.objects()
    if (len(found_count) > 0) and (found_count[len(found_count)-1]['time'].day == now.day) and (found_count[len(found_count)-1]['time'].month == now.month) and (found_count[len(found_count)-1]['time'].year == now.year):
        number = len(all_video)
        found_count[len(found_count)-1].update(set__amount=number)
    else:
        new_count = Count(
            amount = 1,
            time = now
        )
        new_count.save()
    
    # Download
    found_video = Video.objects.with_id(youtube_id)
    if found_video is not None:
        # Download
        options = {
        'format': 'bestaudio/audio',
        'outtmpl': '%(id)s'
        }

        dl = youtube_dl.YoutubeDL(options)
        result = dl.extract_info(
        found_video.link,
        download = True
        )

        # Send File
        save_file = found_video.title.replace(" ", "")
        save_file = re.sub('[^A-Za-z0-9]+', '', save_file)
        os.rename(result['id'], save_file + '.mp3')
        try:
            # Set Download Type
            found_video.update(set__download_type="Audio")
            found_video.update(set__time=datetime.now())

            return send_file(save_file + '.mp3', save_file + '.mp3', as_attachment=True)
        except Exception as e:
            return str(e)

        # Delete Video from Database
        # found_video.delete()
    else:
        return 'Video is not found'

# Feedback
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET': 
        return render_template('feedback.html')
    elif request.method == 'POST':
        form = request.form
        content = form['content']

        new_feedback = Feedback(
            content=content,
            time=datetime.now()
        )
        new_feedback.save()
        return redirect(url_for("index"))

# Daddy Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        form = request.form 
        username = form['username']
        password = form['password']

        if username == "deadSun" and password == "deadSun":
            session['loggedin'] = True
            return redirect(url_for('daddy'))
        else:
            return render_template('login.html', template=0)

# Daddy LogOut
@app.route('/logout')
def logout():
    if session['loggedin'] == False:
        return redirect(url_for('index'))
    else:
        session['loggedin'] = False
        return redirect(url_for('index'))

# Daddy Main
@app.route('/daddy')
def daddy():
    if "loggedin" in session:
        if session['loggedin'] == True:
            return render_template('daddy.html')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Search Count
@app.route('/count')
def count():
    if "loggedin" in session:
        if session['loggedin'] == True:
            all_count = Count.objects()
            return render_template('count.html', all_count=all_count)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Search Feedback
@app.route('/feedback_result')
def feedback_result():
    if "loggedin" in session:
        if session['loggedin'] == True:
            all_feedback = Feedback.objects()
            return render_template('feedback-result.html', all_feedback=all_feedback)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Search Video Download History
@app.route('/history')
def history():
    if "loggedin" in session:
        if session['loggedin'] == True:
            all_video = Video.objects()
            return render_template('history.html', all_video=all_video)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Main
if __name__ == '__main__':
    app.run(debug=True)
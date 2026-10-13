from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import tempfile
import glob

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    url = data['url']
    
    try:
        temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            # اختيار أعلى جودة صوت متاحة
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, 'audio.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # منع تحميل قوائم التشغيل (لو الرابط فيه قائمة هيحمل الأغنية المقصودة فقط)
            'noplaylist': True,
            # تخطي الأخطاء والمحاولة بكل الطرق
            'ignoreerrors': True, 
            'quiet': True,
            'no_warnings': True,
            # إضافة هيدر متصفح حقيقي لخداع حماية يوتيوب وتجنب الحظر
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        mp3_files = glob.glob(os.path.join(temp_dir, '*.mp3'))
        
        if not mp3_files:
             return jsonify({"error": "Failed to create mp3 file. The video might be unavailable or restricted."}), 500
             
        mp3_filename = mp3_files[0]
        
        return send_file(mp3_filename, as_attachment=True, mimetype='audio/mpeg')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

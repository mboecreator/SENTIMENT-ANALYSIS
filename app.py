from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, session
from transformers import pipeline
import json
import os
import pandas as pd
from utils.sentiment import analyze_sentiment, analyze_emotions
from utils.visualization import create_sentiment_chart, create_emotion_chart
from utils.preprocessing import preprocess_text, extract_emojis
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from models import db, User, Analysis, BatchAnalysis

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
app.config.from_object('config')

db.init_app(app)

# Initialize the sentiment analysis pipeline
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    tokenizer="cardiffnlp/twitter-roberta-base-sentiment"
)

# Dummy user database (replace with real database in production)
users = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'name': 'Admin User'
    }
}

@app.route('/')
def index():
    # If user is already logged in, redirect to dashboard
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        # Authenticate against the database
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            if remember:
                session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('index'))
    # Fetch the current user
    user = User.query.filter_by(username=session['username']).first()
    history = []
    history_for_js = []
    if user:
        # Fetch analysis history for this user, most recent first
        analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).all()
        for a in analyses:
            history.append({
                'id': a.id,
                'date': a.created_at.strftime('%Y-%m-%d %H:%M'),
                'input': a.text,
                'sentiment': a.sentiment,
                'emotions': a.emotions,
                'is_batch': a.is_batch if hasattr(a, 'is_batch') else False
            })
            history_for_js.append({
                'date': a.created_at.strftime('%Y-%m-%d'),
                'sentiment': a.sentiment,
                'emotions': a.emotions,
                'input': a.text,
                'emojis': a.emojis if hasattr(a, 'emojis') else ''
            })
    # Get and clear the sentiment result from session
    sentiment_result = session.pop('sentiment_result', None)
    return render_template(
        'dashboard.html',
        username=session['username'],
        history=history,
        history_json=json.dumps(history_for_js),
        sentiment_result=sentiment_result,
        batch_results=None,
        comparison_result=None
    )

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you would typically send an email
        # For now, we'll just flash a success message
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('register'))

        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            created_at=datetime.utcnow(),
            is_active=True
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if request.is_json:
            text = request.json.get('text', '')
        else:
            text = request.form.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        processed_text = preprocess_text(text)
        emojis = extract_emojis(text)
        sentiment_result = analyze_sentiment(processed_text, sentiment_analyzer)
        emotions = analyze_emotions(processed_text)

        # Store result in session for display
        session['sentiment_result'] = {
            'text': text,
            'sentiment': sentiment_result['sentiment'],
            'confidence': sentiment_result.get('score', ''),
            'emotions': emotions,
            'emojis': emojis
        }

        # Save single analysis to database for history if user is logged in
        user = None
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
        if user:
            analysis = Analysis(
                user_id=user.id,
                text=text,
                sentiment=sentiment_result['sentiment'],
                confidence=sentiment_result.get('score', sentiment_result.get('confidence', None)),
                emotions=','.join(emotions) if isinstance(emotions, list) else str(emotions),
                emojis=','.join([e['emoji'] for e in emojis]) if isinstance(emojis, list) else str(emojis),
                is_batch=False
            )
            db.session.add(analysis)
            db.session.commit()

        if not request.is_json:
            return redirect(url_for('dashboard'))

        return jsonify({
            'sentiment': sentiment_result,
            'emotions': emotions,
            'emojis': emojis,
            'processed_text': processed_text,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_batch', methods=['POST'])
def analyze_batch():
    try:
        if 'file' in request.files:
            file = request.files['file']
            if not file or file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('batch'))
                
            if not file.filename.endswith(('.csv', '.txt')):
                flash('Invalid file type. Please upload a CSV or TXT file.', 'error')
                return redirect(url_for('batch'))
                
            if file.filename.endswith('.csv'):
                try:
                    df = pd.read_csv(file)
                    texts = df.iloc[:, 0].astype(str).tolist()  # Ensure all are strings
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding='latin1')
                    texts = df.iloc[:, 0].astype(str).tolist()
                except Exception as e:
                    flash(f'Error reading CSV file: {str(e)}', 'error')
                    return redirect(url_for('batch'))
            else:  # .txt file
                try:
                    texts = file.read().decode('utf-8').splitlines()
                except UnicodeDecodeError:
                    file.seek(0)
                    texts = file.read().decode('latin1').splitlines()
                except Exception as e:
                    flash(f'Error reading TXT file: {str(e)}', 'error')
                    return redirect(url_for('batch'))
        else:
            texts = request.form.get('text', '').splitlines()
        
        if not texts or all(not text.strip() for text in texts):
            flash('No text provided for analysis', 'error')
            return redirect(url_for('batch'))
        
        results = []
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        emotion_counts = {}
        
        # Get current user
        user = None
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
        import uuid
        batch_id = str(uuid.uuid4())
        
        for text in texts:
            if not text.strip():
                continue
                
            processed_text = preprocess_text(text)
            sentiment_result = analyze_sentiment(processed_text, sentiment_analyzer)
            emotions = analyze_emotions(processed_text)
            emojis = extract_emojis(text)
            confidence = sentiment_result.get('score', sentiment_result.get('confidence', None))
            # Update counts
            sentiment_counts[sentiment_result['sentiment']] += 1
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            results.append({
                'text': text,
                'sentiment': sentiment_result['sentiment'],
                'emotions': emotions,
                'emojis': emojis
            })
            # Save to Analysis table for history
            if user:
                analysis = Analysis(
                    user_id=user.id,
                    text=text,
                    sentiment=sentiment_result['sentiment'],
                    confidence=confidence,
                    emotions=','.join(emotions) if isinstance(emotions, list) else str(emotions),
                    emojis=','.join([e['emoji'] for e in emojis]) if isinstance(emojis, list) else str(emojis),
                    is_batch=True,
                    batch_id=batch_id
                )
                db.session.add(analysis)
        if user:
            db.session.commit()
        # Prepare batch_results for dashboard rendering
        batch_results = {
            'results': results,
            'sentiment_distribution': [
                sentiment_counts['positive'],
                sentiment_counts['neutral'],
                sentiment_counts['negative']
            ],
            'emotion_distribution': emotion_counts
        }
        # Render dashboard with batch_results
        # Fetch the current user and history for dashboard
        history = []
        history_for_js = []
        if user:
            analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).all()
            for a in analyses:
                history.append({
                    'id': a.id,
                    'date': a.created_at.strftime('%Y-%m-%d %H:%M'),
                    'input': a.text,
                    'sentiment': a.sentiment,
                    'emotions': a.emotions,
                    'is_batch': a.is_batch if hasattr(a, 'is_batch') else False
                })
                history_for_js.append({
                    'date': a.created_at.strftime('%Y-%m-%d'),
                    'sentiment': a.sentiment,
                    'emotions': a.emotions,
                    'input': a.text,
                    'emojis': a.emojis if hasattr(a, 'emojis') else ''
                })
        sentiment_result = session.pop('sentiment_result', None)
        return render_template(
            'dashboard.html',
            username=session['username'],
            history=history,
            history_json=json.dumps(history_for_js),
            sentiment_result=sentiment_result,
            batch_results=batch_results,
            comparison_result=None
        )
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred during batch analysis: {str(e)}', 'error')
        return redirect(url_for('batch'))

@app.route('/compare_texts', methods=['POST'])
def compare_texts():
    try:
        text1 = request.form.get('text1', '')
        text2 = request.form.get('text2', '')
        
        if not text1 or not text2:
            flash('Please provide both original and revised texts', 'error')
            return redirect(url_for('dashboard'))
        
        # Process and analyze both texts
        processed_text1 = preprocess_text(text1)
        processed_text2 = preprocess_text(text2)
        
        sentiment_result1 = analyze_sentiment(processed_text1, sentiment_analyzer)
        sentiment_result2 = analyze_sentiment(processed_text2, sentiment_analyzer)
        
        # Determine sentiment shift
        sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
        sentiment_value1 = sentiment_map[sentiment_result1['sentiment']]
        sentiment_value2 = sentiment_map[sentiment_result2['sentiment']]
        
        shift_value = sentiment_value2 - sentiment_value1
        
        if shift_value > 0:
            shift = 'Improved (More Positive)'
        elif shift_value < 0:
            shift = 'Declined (More Negative)'
        else:
            shift = 'No Change'
            
        # Create comparison result
        comparison_result = {
            'original_sentiment': sentiment_result1['sentiment'].capitalize(),
            'revised_sentiment': sentiment_result2['sentiment'].capitalize(),
            'shift': shift
        }
        
        # Get user history for dashboard rendering
        user = None
        history = []
        history_for_js = []
        
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user:
                analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).all()
                for a in analyses:
                    history.append({
                        'id': a.id,
                        'date': a.created_at.strftime('%Y-%m-%d %H:%M'),
                        'input': a.text,
                        'sentiment': a.sentiment,
                        'emotions': a.emotions,
                        'is_batch': a.is_batch if hasattr(a, 'is_batch') else False
                    })
                    history_for_js.append({
                        'date': a.created_at.strftime('%Y-%m-%d'),
                        'sentiment': a.sentiment,
                        'emotions': a.emotions,
                        'input': a.text,
                        'emojis': a.emojis if hasattr(a, 'emojis') else ''
                    })
        
        # Render dashboard with comparison results and redirect to the comparison section
        return render_template(
            'dashboard.html',
            username=session.get('username', ''),
            history=history,
            history_json=json.dumps(history_for_js),
            sentiment_result=None,
            batch_results=None,
            comparison_result=comparison_result,
            scroll_to_section='compare'  # Add this parameter to indicate where to scroll
        )
        
    except Exception as e:
        flash(f'An error occurred during text comparison: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/batch')
def batch():
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('index'))
    return render_template('batch.html')

@app.route('/delete_history/<int:analysis_id>', methods=['POST'])
def delete_history(analysis_id):
    if 'username' not in session:
        return redirect(url_for('index'))
    analysis = Analysis.query.get(analysis_id)
    user = User.query.filter_by(username=session['username']).first()
    if analysis and analysis.user_id == user.id:
        db.session.delete(analysis)
        db.session.commit()
        flash('History item deleted.', 'success')
    else:
        flash('Delete failed or unauthorized.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/visualize')
def visualize():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('index'))
    
    # Get all analyses for the current user
    analyses = Analysis.query.filter_by(user_id=user.id).all()
    
    # Calculate total analyses
    total_analyses = len(analyses)
    
    # Calculate sentiment counts and percentages
    positive_count = sum(1 for a in analyses if a.sentiment == 'positive')
    neutral_count = sum(1 for a in analyses if a.sentiment == 'neutral')
    negative_count = sum(1 for a in analyses if a.sentiment == 'negative')
    
    positive_percentage = round((positive_count / total_analyses * 100) if total_analyses > 0 else 0, 1)
    neutral_percentage = round((neutral_count / total_analyses * 100) if total_analyses > 0 else 0, 1)
    negative_percentage = round((negative_count / total_analyses * 100) if total_analyses > 0 else 0, 1)
    
    # Calculate emotion counts
    emotion_counts = {
        'joy': sum(1 for a in analyses if hasattr(a, 'emotions') and 'joy' in a.emotions),
        'sadness': sum(1 for a in analyses if hasattr(a, 'emotions') and 'sadness' in a.emotions),
        'anger': sum(1 for a in analyses if hasattr(a, 'emotions') and 'anger' in a.emotions),
        'fear': sum(1 for a in analyses if hasattr(a, 'emotions') and 'fear' in a.emotions),
        'surprise': sum(1 for a in analyses if hasattr(a, 'emotions') and 'surprise' in a.emotions)
    }
    
    # Prepare timeline data
    timeline_data = {}
    for analysis in analyses:
        date = analysis.created_at.strftime('%Y-%m-%d')
        if date not in timeline_data:
            timeline_data[date] = {'positive': 0, 'neutral': 0, 'negative': 0}
        timeline_data[date][analysis.sentiment] += 1
    
    # Sort timeline data by date
    timeline_dates = sorted(timeline_data.keys())
    timeline_positive = [timeline_data[date]['positive'] for date in timeline_dates]
    timeline_neutral = [timeline_data[date]['neutral'] for date in timeline_dates]
    timeline_negative = [timeline_data[date]['negative'] for date in timeline_dates]
    
    return render_template('visualize.html',
                         total_analyses=total_analyses,
                         positive_count=positive_count,
                         neutral_count=neutral_count,
                         negative_count=negative_count,
                         positive_percentage=positive_percentage,
                         neutral_percentage=neutral_percentage,
                         negative_percentage=negative_percentage,
                         emotion_counts=emotion_counts,
                         timeline_dates=timeline_dates,
                         timeline_positive=timeline_positive,
                         timeline_neutral=timeline_neutral,
                         timeline_negative=timeline_negative)

if __name__ == '__main__':
    app.run(debug=True)

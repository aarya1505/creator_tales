import os
import io
import json
import base64
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from gemini_helper import (
    generate_linkedin_post,
    rewrite_content,
    generate_carousel,
    optimize_profile,
    generate_networking_message,
    generate_content_calendar,
    generate_analytics_recommendations
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
DB_USER = "root"        
DB_PASS = "chaukul%4015D"
DB_HOST = "localhost"
DB_NAME = "creatortalesdb"

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

UPLOAD_FOLDER = 'uploads'
CHARTS_FOLDER = 'static/charts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHARTS_FOLDER, exist_ok=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    drafts = db.relationship('Draft', backref='user', lazy=True, cascade='all, delete-orphan')
    calendars = db.relationship('ContentCalendar', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContentCalendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([name, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('signup.html')

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Welcome back!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    recent_drafts = Draft.query.filter_by(user_id=current_user.id).order_by(Draft.updated_at.desc()).limit(5).all()
    saved_calendars = ContentCalendar.query.filter_by(user_id=current_user.id).order_by(ContentCalendar.created_at.desc()).limit(3).all()
    total_drafts = Draft.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', recent_drafts=recent_drafts, saved_calendars=saved_calendars, total_drafts=total_drafts)


@app.route('/post-generator', methods=['GET', 'POST'])
@login_required
def post_generator():
    result = None
    if request.method == 'POST':
        topic = request.form.get('topic', '')
        niche = request.form.get('niche', '')
        tone = request.form.get('tone', 'professional')
        length = request.form.get('length', 'medium')
        include_carousel = request.form.get('include_carousel') == 'on'

        if topic:
            result = generate_linkedin_post(topic, niche, tone, length, include_carousel)

    return render_template('post_generator.html', result=result)


@app.route('/content-rewriter', methods=['GET', 'POST'])
@login_required
def content_rewriter():
    result = None
    if request.method == 'POST':
        original_content = request.form.get('original_content', '')
        target_tone = request.form.get('target_tone', 'professional')

        if original_content:
            result = rewrite_content(original_content, target_tone)

    return render_template('content_rewriter.html', result=result)


@app.route('/carousel-generator', methods=['GET', 'POST'])
@login_required
def carousel_generator():
    result = None
    if request.method == 'POST':
        topic = request.form.get('topic', '')
        niche = request.form.get('niche', '')

        if topic:
            result = generate_carousel(topic, niche)

    return render_template('carousel_generator.html', result=result)


@app.route('/profile-optimizer', methods=['GET', 'POST'])
@login_required
def profile_optimizer():
    result = None
    if request.method == 'POST':
        about = request.form.get('about', '')
        headline = request.form.get('headline', '')
        experience = request.form.get('experience', '')
        skills = request.form.get('skills', '')

        if any([about, headline, experience, skills]):
            result = optimize_profile(about, headline, experience, skills)

    return render_template('profile_optimizer.html', result=result)


@app.route('/message-generator', methods=['GET', 'POST'])
@login_required
def message_generator():
    result = None
    if request.method == 'POST':
        message_type = request.form.get('message_type', 'recruiter_outreach')
        tone = request.form.get('tone', 'professional')
        context = request.form.get('context', '')
        recipient_info = request.form.get('recipient_info', '')

        result = generate_networking_message(message_type, tone, context, recipient_info)

    return render_template('message_generator.html', result=result)


@app.route('/calendar-generator', methods=['GET', 'POST'])
@login_required
def calendar_generator():
    result = None
    if request.method == 'POST':
        niche = request.form.get('niche', '')
        duration = request.form.get('duration', 'weekly')
        goals = request.form.get('goals', '')

        if niche:
            result = generate_content_calendar(niche, duration, goals)

    return render_template('calendar_generator.html', result=result)


@app.route('/save-calendar', methods=['POST'])
@login_required
def save_calendar():
    data = request.get_json()
    title = data.get('title', 'Untitled Calendar')
    niche = data.get('niche', '')
    duration = data.get('duration', 'weekly')
    content = data.get('content', '')

    calendar = ContentCalendar(
        user_id=current_user.id,
        title=title,
        niche=niche,
        duration=duration,
        content=content
    )
    db.session.add(calendar)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Calendar saved successfully!'})


@app.route('/drafts')
@login_required
def drafts():
    category = request.args.get('category', 'all')
    if category == 'all':
        user_drafts = Draft.query.filter_by(user_id=current_user.id).order_by(Draft.updated_at.desc()).all()
    else:
        user_drafts = Draft.query.filter_by(user_id=current_user.id, category=category).order_by(Draft.updated_at.desc()).all()
    return render_template('drafts.html', drafts=user_drafts, current_category=category)


@app.route('/save-draft', methods=['POST'])
@login_required
def save_draft():
    data = request.get_json()
    title = data.get('title', 'Untitled Draft')
    content = data.get('content', '')
    category = data.get('category', 'post')

    draft = Draft(
        user_id=current_user.id,
        title=title,
        content=content,
        category=category
    )
    db.session.add(draft)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Draft saved successfully!', 'draft_id': draft.id})


@app.route('/edit-draft/<int:draft_id>', methods=['GET', 'POST'])
@login_required
def edit_draft(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    if draft.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('drafts'))

    if request.method == 'POST':
        draft.title = request.form.get('title', draft.title)
        draft.content = request.form.get('content', draft.content)
        draft.category = request.form.get('category', draft.category)
        db.session.commit()
        flash('Draft updated successfully!', 'success')
        return redirect(url_for('drafts'))

    return render_template('edit_draft.html', draft=draft)


@app.route('/delete-draft/<int:draft_id>', methods=['POST'])
@login_required
def delete_draft(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    if draft.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied.'})

    db.session.delete(draft)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Draft deleted successfully!'})


@app.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    analysis_result = None
    charts = []
    ai_recommendations = None

    if request.method == 'POST':
        if 'analytics_file' not in request.files:
            flash('No file uploaded.', 'error')
            return render_template('analytics.html')

        file = request.files['analytics_file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return render_template('analytics.html')

        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                analysis_result, charts = analyze_linkedin_data(df, current_user.id)
                
                if analysis_result:
                    ai_recommendations = generate_analytics_recommendations(analysis_result)

            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
        else:
            flash('Please upload a CSV or Excel file.', 'error')

    return render_template('analytics.html', analysis=analysis_result, charts=charts, recommendations=ai_recommendations)


def analyze_linkedin_data(df, user_id):
    df.columns = df.columns.str.lower().str.strip()
    
    possible_columns = {
        'impressions': ['impressions', 'views', 'impression', 'view'],
        'reactions': ['reactions', 'likes', 'reaction', 'like'],
        'comments': ['comments', 'comment'],
        'shares': ['shares', 'share', 'reposts', 'repost'],
        'date': ['date', 'publish date', 'published', 'post date', 'created'],
        'title': ['title', 'post title', 'content', 'post', 'text'],
        'type': ['type', 'post type', 'content type', 'format']
    }
    
    column_mapping = {}
    for standard_name, alternatives in possible_columns.items():
        for alt in alternatives:
            if alt in df.columns:
                column_mapping[standard_name] = alt
                break
    
    analysis = {
        'total_posts': len(df),
        'date_range': 'N/A',
        'avg_impressions': 0,
        'avg_reactions': 0,
        'avg_comments': 0,
        'avg_shares': 0,
        'total_impressions': 0,
        'total_reactions': 0,
        'total_comments': 0,
        'total_shares': 0,
        'engagement_rate': 0,
        'top_posts': [],
        'best_day': 'N/A',
        'best_content_type': 'N/A',
        'posting_frequency': 'N/A'
    }
    
    charts = []
    
    if 'impressions' in column_mapping:
        imp_col = column_mapping['impressions']
        df[imp_col] = pd.to_numeric(df[imp_col], errors='coerce').fillna(0)
        analysis['total_impressions'] = int(df[imp_col].sum())
        analysis['avg_impressions'] = round(df[imp_col].mean(), 2)
    
    if 'reactions' in column_mapping:
        react_col = column_mapping['reactions']
        df[react_col] = pd.to_numeric(df[react_col], errors='coerce').fillna(0)
        analysis['total_reactions'] = int(df[react_col].sum())
        analysis['avg_reactions'] = round(df[react_col].mean(), 2)
    
    if 'comments' in column_mapping:
        comm_col = column_mapping['comments']
        df[comm_col] = pd.to_numeric(df[comm_col], errors='coerce').fillna(0)
        analysis['total_comments'] = int(df[comm_col].sum())
        analysis['avg_comments'] = round(df[comm_col].mean(), 2)
    
    if 'shares' in column_mapping:
        share_col = column_mapping['shares']
        df[share_col] = pd.to_numeric(df[share_col], errors='coerce').fillna(0)
        analysis['total_shares'] = int(df[share_col].sum())
        analysis['avg_shares'] = round(df[share_col].mean(), 2)
    
    if analysis['total_impressions'] > 0:
        total_engagement = analysis['total_reactions'] + analysis['total_comments'] + analysis['total_shares']
        analysis['engagement_rate'] = round((total_engagement / analysis['total_impressions']) * 100, 2)
    
    if 'date' in column_mapping:
        date_col = column_mapping['date']
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        valid_dates = df[date_col].dropna()
        if len(valid_dates) > 0:
            analysis['date_range'] = f"{valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}"
            
            df['day_of_week'] = df[date_col].dt.day_name()
            if 'impressions' in column_mapping:
                day_performance = df.groupby('day_of_week')[column_mapping['impressions']].mean()
                if len(day_performance) > 0:
                    analysis['best_day'] = day_performance.idxmax()
    
    if 'type' in column_mapping:
        type_col = column_mapping['type']
        if 'impressions' in column_mapping:
            type_performance = df.groupby(type_col)[column_mapping['impressions']].mean()
            if len(type_performance) > 0:
                analysis['best_content_type'] = type_performance.idxmax()
    
    if 'impressions' in column_mapping and 'title' in column_mapping:
        top_df = df.nlargest(5, column_mapping['impressions'])
        for _, row in top_df.iterrows():
            title = str(row[column_mapping['title']])[:100] if pd.notna(row[column_mapping['title']]) else 'Untitled'
            analysis['top_posts'].append({
                'title': title,
                'impressions': int(row[column_mapping['impressions']]),
                'reactions': int(row[column_mapping.get('reactions', column_mapping['impressions'])]) if 'reactions' in column_mapping else 0
            })
    
    charts = generate_analytics_charts(df, column_mapping, user_id)
    
    return analysis, charts


def generate_analytics_charts(df, column_mapping, user_id):
    charts = []
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    if 'impressions' in column_mapping and 'date' in column_mapping:
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            date_col = column_mapping['date']
            imp_col = column_mapping['impressions']
            
            df_sorted = df.sort_values(date_col)
            ax.plot(df_sorted[date_col], df_sorted[imp_col], marker='o', linewidth=2, markersize=4, color='#0077B5')
            ax.fill_between(df_sorted[date_col], df_sorted[imp_col], alpha=0.3, color='#0077B5')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Impressions', fontsize=12)
            ax.set_title('Impression Trends Over Time', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = f'static/charts/impressions_{user_id}_{timestamp}.png'
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append({'name': 'Impression Trends', 'path': chart_path})
        except Exception as e:
            print(f"Error creating impression chart: {e}")
    
    if 'day_of_week' in df.columns and 'impressions' in column_mapping:
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_performance = df.groupby('day_of_week')[column_mapping['impressions']].mean().reindex(day_order)
            
            colors = ['#0077B5' if v == day_performance.max() else '#86C5E5' for v in day_performance.values]
            bars = ax.bar(day_performance.index, day_performance.values, color=colors)
            ax.set_xlabel('Day of Week', fontsize=12)
            ax.set_ylabel('Average Impressions', fontsize=12)
            ax.set_title('Performance by Day of Week', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = f'static/charts/day_performance_{user_id}_{timestamp}.png'
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append({'name': 'Day of Week Performance', 'path': chart_path})
        except Exception as e:
            print(f"Error creating day chart: {e}")
    
    engagement_data = []
    engagement_labels = []
    if 'reactions' in column_mapping:
        engagement_data.append(df[column_mapping['reactions']].sum())
        engagement_labels.append('Reactions')
    if 'comments' in column_mapping:
        engagement_data.append(df[column_mapping['comments']].sum())
        engagement_labels.append('Comments')
    if 'shares' in column_mapping:
        engagement_data.append(df[column_mapping['shares']].sum())
        engagement_labels.append('Shares')
    
    if engagement_data:
        try:
            fig, ax = plt.subplots(figsize=(8, 8))
            colors = ['#0077B5', '#00A0DC', '#86C5E5']
            explode = [0.05] * len(engagement_data)
            ax.pie(engagement_data, labels=engagement_labels, autopct='%1.1f%%', 
                   colors=colors[:len(engagement_data)], explode=explode, shadow=True)
            ax.set_title('Engagement Distribution', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            chart_path = f'static/charts/engagement_{user_id}_{timestamp}.png'
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append({'name': 'Engagement Distribution', 'path': chart_path})
        except Exception as e:
            print(f"Error creating engagement chart: {e}")
    
    if 'type' in column_mapping and 'impressions' in column_mapping:
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            type_col = column_mapping['type']
            type_performance = df.groupby(type_col)[column_mapping['impressions']].mean().sort_values(ascending=True)
            
            colors = ['#0077B5' if v == type_performance.max() else '#86C5E5' for v in type_performance.values]
            ax.barh(type_performance.index, type_performance.values, color=colors)
            ax.set_xlabel('Average Impressions', fontsize=12)
            ax.set_ylabel('Content Type', fontsize=12)
            ax.set_title('Performance by Content Type', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            chart_path = f'static/charts/content_type_{user_id}_{timestamp}.png'
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append({'name': 'Content Type Performance', 'path': chart_path})
        except Exception as e:
            print(f"Error creating content type chart: {e}")
    
    if 'date' in column_mapping:
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            date_col = column_mapping['date']
            df['month'] = df[date_col].dt.to_period('M')
            monthly_posts = df.groupby('month').size()
            
            ax.bar(monthly_posts.index.astype(str), monthly_posts.values, color='#0077B5')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Number of Posts', fontsize=12)
            ax.set_title('Posting Frequency by Month', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = f'static/charts/frequency_{user_id}_{timestamp}.png'
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            charts.append({'name': 'Posting Frequency', 'path': chart_path})
        except Exception as e:
            print(f"Error creating frequency chart: {e}")
    
    return charts


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
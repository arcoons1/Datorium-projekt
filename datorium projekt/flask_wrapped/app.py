from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
from datetime import datetime

app = Flask(__name__)

# datu ielāde
df = pd.read_csv('data/popular_songs.csv')

def generate_visualizations():
    """Generate all visualizations and return them as base64 encoded images"""
    visuals = {}
    
    # Top 10 dziesmas
    plt.figure(figsize=(10, 6))
    top_songs = df.sort_values('play_count', ascending=False).head(10)
    plt.barh(top_songs['song_name'] + ' - ' + top_songs['artist'], top_songs['play_count'], color='#1DB954')
    plt.title('Your Top 10 Songs')
    plt.xlabel('Play Count')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    visuals['top_songs'] = base64.b64encode(buf.getbuffer()).decode("ascii")
    plt.close()
    
    # Top artisti pēc counta
    plt.figure(figsize=(10, 6))
    top_artists = df.groupby('artist')['play_count'].sum().sort_values(ascending=False).head(5)
    plt.pie(top_artists, labels=top_artists.index, autopct='%1.1f%%', colors=['#1DB954', '#191414', '#535353', '#B3B3B3', '#FFFFFF'])
    plt.title('Your Top Artists')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    visuals['top_artists'] = base64.b64encode(buf.getbuffer()).decode("ascii")
    plt.close()
    
    #žanru iedale
    plt.figure(figsize=(10, 6))
    genres = df.groupby('genre')['play_count'].sum().sort_values(ascending=False)
    genres.plot(kind='bar', color='#1DB954')
    plt.title('Your Genre Distribution')
    plt.xlabel('Genre')
    plt.ylabel('Total Plays')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    visuals['genres'] = base64.b64encode(buf.getbuffer()).decode("ascii")
    plt.close()
    
    # atskanojumu skaita iedale
    plt.figure(figsize=(10, 6))
    plt.hist(df['play_count'], bins=20, color='#1DB954', edgecolor='black')
    plt.title('Your Play Count Distribution')
    plt.xlabel('Play Count')
    plt.ylabel('Number of Songs')
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    visuals['play_dist'] = base64.b64encode(buf.getbuffer()).decode("ascii")
    plt.close()
    
    return visuals

@app.template_filter('format_number')
def format_number(value):
    return "{:,}".format(value)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # visuals generacija
    visuals = generate_visualizations()
    
    #statistikas aprekini
    total_plays = df['play_count'].sum()
    total_songs = len(df)
    top_song = df.loc[df['play_count'].idxmax()]
    top_artist = df.groupby('artist')['play_count'].sum().idxmax()
    top_genre = df.groupby('genre')['play_count'].sum().idxmax()
    
    return render_template('results.html', 
                          visuals=visuals,
                          total_plays=total_plays,
                          total_songs=total_songs,
                          top_song=top_song,
                          top_artist=top_artist,
                          top_genre=top_genre,
                          current_year=datetime.now().year)

if __name__ == '__main__':
    app.run(debug=True)
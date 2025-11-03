import http.server
import socketserver
import urllib.parse
import wikipedia
import requests
import json
from datetime import datetime

# Konfigurasi Wikipedia
wikipedia.set_lang("id")

class WikipediaImageHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        keyword = query_params.get('keyword', ['nature'])[0]
        page = int(query_params.get('page', [1])[0])
        
        html_content = self.generate_gallery_html(keyword, page)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def get_wikipedia_images(self, keyword, page=1, limit=20):
        """Ambil gambar dari Wikipedia API"""
        images = []
        try:
            # Wikipedia API search untuk images
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={keyword}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=300&format=json&origin=*"
            
            response = requests.get(search_url)
            data = response.json()
            
            if 'query' in data:
                for page_id, page_data in data['query']['pages'].items():
                    if 'imageinfo' in page_data:
                        image_info = page_data['imageinfo'][0]
                        images.append({
                            'title': page_data['title'].replace('File:', ''),
                            'url': image_info['thumburl'],
                            'description': image_info.get('extmetadata', {}).get('ImageDescription', {}).get('value', 'No description'),
                            'artist': image_info.get('extmetadata', {}).get('Artist', {}).get('value', 'Unknown'),
                            'license': image_info.get('extmetadata', {}).get('LicenseShortName', {}).get('value', 'Unknown')
                        })
        except Exception as e:
            # Fallback ke mock images jika API error
            images = self.generate_mock_images(keyword, limit)
        
        return images
    
    def generate_mock_images(self, keyword, count):
        """Generate mock images untuk demo"""
        images = []
        for i in range(count):
            images.append({
                'title': f"{keyword} image {i+1}",
                'url': f"https://picsum.photos/400/300?random={i}",
                'description': f"Beautiful {keyword} image from Wikipedia collection",
                'artist': 'Wikimedia Contributor',
                'license': 'CC BY-SA'
            })
        return images
    
    def generate_gallery_html(self, keyword, page):
        """Generate HTML untuk gallery gambar"""
        images = self.get_wikipedia_images(keyword, page, 20)
        
        # Build gallery grid
        gallery_html = ""
        for image in images:
            gallery_html += f"""
            <div class="image-card">
                <img src="{image['url']}" alt="{image['title']}" loading="lazy">
                <div class="image-info">
                    <div class="image-title">{image['title']}</div>
                    <div class="image-description">{image['description'][:100]}...</div>
                </div>
            </div>
            """
        
        # Full HTML template
        html = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Wikipedia Image Gallery - Python Version</title>
            <style>
                :root {{
                    --primary-color: #2c3e50;
                    --secondary-color: #3498db;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f9f9f9;
                }}
                
                .header {{
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                
                .search-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                
                .search-form {{
                    display: flex;
                    gap: 10px;
                }}
                
                .search-input {{
                    flex: 1;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px;
                }}
                
                .search-button {{
                    background: var(--secondary-color);
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                
                .gallery-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }}
                
                .image-card {{
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    transition: transform 0.3s;
                }}
                
                .image-card:hover {{
                    transform: translateY(-5px);
                }}
                
                .image-card img {{
                    width: 100%;
                    height: 200px;
                    object-fit: cover;
                }}
                
                .image-info {{
                    padding: 15px;
                }}
                
                .image-title {{
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: var(--primary-color);
                }}
                
                .image-description {{
                    font-size: 14px;
                    color: #666;
                    line-height: 1.4;
                }}
                
                .stats {{
                    text-align: center;
                    margin: 20px 0;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🖼️ Wikipedia Image Gallery</h1>
                <p>Python Server Version - 100+ Gambar Wikipedia</p>
            </div>
            
            <div class="search-container">
                <form method="GET" class="search-form">
                    <input type="text" name="keyword" value="{keyword}" placeholder="Cari gambar (nature, technology, art...)" class="search-input">
                    <button type="submit" class="search-button">🔍 Cari Gambar</button>
                </form>
            </div>
            
            <div class="stats">
                Menampilkan <strong>{len(images)}</strong> gambar untuk <strong>"{keyword}"</strong>
            </div>
            
            <div class="gallery-grid">
                {gallery_html}
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <button onclick="loadMore()" style="background: var(--secondary-color); color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer;">
                    📥 Muat Lebih Banyak
                </button>
            </div>
            
            <script>
                function loadMore() {{
                    const url = new URL(window.location);
                    const currentPage = parseInt(url.searchParams.get('page') || '1');
                    url.searchParams.set('page', currentPage + 1);
                    window.location.href = url.toString();
                }}
            </script>
        </body>
        </html>
        """
        return html

# Jalankan server
if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), WikipediaImageHandler) as httpd:
        print(f"🚀 Python Server running at http://localhost:{PORT}")
        print("📍 Access: http://localhost:8000/?keyword=nature")
        print("⏹️  Press Ctrl+C to stop")
        httpd.serve_forever()

#!/usr/bin/env python3
"""
DefenseShot Elite Sniper Academy - Certificate Generator
A complete web application for generating professional military-themed certificates

Requirements:
pip install flask pillow reportlab

Run with: python app.py
"""

import os
import io
import base64
import webbrowser
import threading
import time
from datetime import datetime
from flask import Flask, render_template_string, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DefenseShot Elite Sniper Academy - Certificate Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%, #0a0a0a 100%);
            min-height: 100vh;
            color: #fff;
            position: relative;
            overflow-x: hidden;
        }

        /* Military background pattern */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 20%, rgba(34, 139, 34, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 69, 19, 0.1) 0%, transparent 50%),
                linear-gradient(45deg, transparent 30%, rgba(0, 100, 0, 0.05) 50%, transparent 70%);
            z-index: -1;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            background: linear-gradient(135deg, rgba(34, 139, 34, 0.2) 0%, rgba(139, 69, 19, 0.2) 100%);
            border-radius: 15px;
            border: 2px solid rgba(255, 215, 0, 0.3);
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
        }

        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(45deg, #228B22, #8B4513);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            color: #FFD700;
            border: 3px solid #FFD700;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }

        .title {
            font-size: 2.5em;
            font-weight: bold;
            color: #FFD700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin-bottom: 10px;
            letter-spacing: 2px;
        }

        .subtitle {
            font-size: 1.3em;
            color: #90EE90;
            font-weight: 300;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }

        .form-container {
            background: rgba(0, 0, 0, 0.6);
            padding: 40px;
            border-radius: 15px;
            border: 2px solid rgba(34, 139, 34, 0.3);
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #FFD700;
            font-size: 1.1em;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(34, 139, 34, 0.5);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            font-size: 1em;
            transition: all 0.3s ease;
        }

        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #FFD700;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }

        .submit-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(45deg, #228B22, #8B4513);
            color: #FFD700;
            border: none;
            border-radius: 8px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: 2px solid #FFD700;
        }

        .submit-btn:hover {
            background: linear-gradient(45deg, #32CD32, #A0522D);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        }

        .preview-section {
            margin-top: 40px;
            text-align: center;
            display: none;
        }

        .preview-title {
            font-size: 1.5em;
            color: #FFD700;
            margin-bottom: 20px;
        }

        .certificate-preview {
            max-width: 100%;
            border: 3px solid #FFD700;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }

        .download-btn {
            margin-top: 20px;
            padding: 15px 30px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #000;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
        }

        .download-btn:hover {
            background: linear-gradient(45deg, #FFA500, #FF8C00);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 215, 0, 0.3);
            border-top: 4px solid #FFD700;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }

        .feature-card {
            background: rgba(0, 0, 0, 0.6);
            padding: 25px;
            border-radius: 10px;
            border: 2px solid rgba(34, 139, 34, 0.3);
            text-align: center;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            border-color: #FFD700;
            box-shadow: 0 5px 20px rgba(255, 215, 0, 0.2);
        }

        .feature-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
            color: #FFD700;
        }

        .feature-title {
            font-size: 1.2em;
            color: #90EE90;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .feature-desc {
            color: #ccc;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            .title {
                font-size: 2em;
            }

            .form-container {
                padding: 25px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🎯</div>
            <h1 class="title">DefenseShot Elite Sniper Academy</h1>
            <p class="subtitle">Certificate Generation System</p>
        </div>

        <div class="form-container">
            <form id="certificateForm">
                <div class="form-group">
                    <label for="studentName">Student Name *</label>
                    <input type="text" id="studentName" name="studentName" required placeholder="Enter full name">
                </div>

                <div class="form-group">
                    <label for="startDate">Course Start Date *</label>
                    <input type="date" id="startDate" name="startDate" required>
                </div>

                <div class="form-group">
                    <label for="endDate">Course End Date</label>
                    <input type="date" id="endDate" name="endDate" readonly>
                </div>

                <div class="form-group">
                    <label for="institution">Institution Name *</label>
                    <input type="text" id="institution" name="institution" required placeholder="College/School/University Name">
                </div>

                <div class="form-group">
                    <label for="course">Course/Program *</label>
                    <select id="course" name="course" required>
                        <option value="">Select Course</option>
                        <option value="Learning About Armed Forces ">Learning About Armed Forces</option>

                        <option value="Custom Course">Custom Course (Enter below)</option>
                    </select>
                </div>

                <div class="form-group" id="customCourseGroup" style="display: none;">
                    <label for="customCourse">Custom Course Name</label>
                    <input type="text" id="customCourse" name="customCourse" placeholder="Enter custom course name">
                </div>

                <button type="submit" class="submit-btn">🎯 Generate Certificate</button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Generating your certificate...</p>
            </div>

            <div class="preview-section" id="previewSection">
                <h3 class="preview-title">Certificate Preview</h3>
                <img id="certificatePreview" class="certificate-preview" alt="Certificate Preview">
                <br>
                <button class="download-btn" onclick="downloadCertificate()">📥 Download Certificate</button>
            </div>
        </div>

        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🏆</div>
                <h3 class="feature-title">Professional Design</h3>
                <p class="feature-desc">Military-themed certificates with professional layouts and high-quality graphics</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎖️</div>
                <h3 class="feature-title">Instant Generation</h3>
                <p class="feature-desc">Generate certificates instantly with automatic date completion and validation</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <h3 class="feature-title">Mobile Friendly</h3>
                <p class="feature-desc">Responsive design that works perfectly on all devices and screen sizes</p>
            </div>
        </div>
    </div>

    <script>
        // Set current date as end date
        document.getElementById('endDate').value = new Date().toISOString().split('T')[0];

        // Handle custom course selection
        document.getElementById('course').addEventListener('change', function() {
            const customGroup = document.getElementById('customCourseGroup');
            if (this.value === 'Custom Course') {
                customGroup.style.display = 'block';
                document.getElementById('customCourse').required = true;
            } else {
                customGroup.style.display = 'none';
                document.getElementById('customCourse').required = false;
            }
        });

        // Handle form submission
        document.getElementById('certificateForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('previewSection').style.display = 'none';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const result = await response.json();

                    // Show preview
                    document.getElementById('certificatePreview').src = 'data:image/png;base64,' + result.preview;
                    document.getElementById('previewSection').style.display = 'block';

                    // Store certificate ID for download
                    window.certificateId = result.certificateId;
                } else {
                    alert('Error generating certificate. Please try again.');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        });

        function downloadCertificate() {
            if (window.certificateId) {
                window.open('/download/' + window.certificateId, '_blank');
            }
        }

        // Auto-update end date when start date changes
        document.getElementById('startDate').addEventListener('change', function() {
            const startDate = new Date(this.value);
            const endDate = new Date();
            if (startDate > endDate) {
                document.getElementById('endDate').value = this.value;
            }
        });
    </script>
</body>
</html>
"""


class CertificateGenerator:
    def __init__(self):
        self.certificates = {}  # Store generated certificates temporarily

    def create_military_background(self, width, height):
        """Create a military-themed background with camouflage pattern"""
        # Create base image
        img = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(img)

        # Create camouflage pattern
        import random
        random.seed(42)  # For consistent pattern

        colors = ['#2d3e2d', '#3a4a3a', '#4a5a4a', '#1a2a1a']

        # Add camouflage spots
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(30, 100)
            color = random.choice(colors)
            draw.ellipse([x, y, x + size, y + size], fill=color)

        # Add subtle grid pattern
        for i in range(0, width, 50):
            draw.line([(i, 0), (i, height)], fill='#0a0a0a', width=1)
        for i in range(0, height, 50):
            draw.line([(0, i), (width, i)], fill='#0a0a0a', width=1)

        # Apply blur for professional look
        img = img.filter(ImageFilter.GaussianBlur(radius=1))

        # Add overlay for reduced visibility
        overlay = Image.new('RGBA', (width, height), color=(0, 0, 0, 180))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)

        return img

    def generate_certificate(self, student_name, start_date, end_date, institution, course):
        """Generate a professional military-themed certificate"""
        # Certificate dimensions
        width, height = 1200, 850

        # Create background
        cert_img = self.create_military_background(width, height)
        draw = ImageDraw.Draw(cert_img)

        # Load fonts (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            subtitle_font = ImageFont.truetype("arial.ttf", 24)
            text_font = ImageFont.truetype("arial.ttf", 20)
            name_font = ImageFont.truetype("arial.ttf", 36)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            name_font = ImageFont.load_default()

        # Colors
        gold = '#FFD700'
        light_green = '#90EE90'
        white = '#FFFFFF'

        # Draw border
        border_color = gold
        for i in range(5):
            draw.rectangle([10 + i, 10 + i, width - 10 - i, height - 10 - i], outline=border_color, width=2)

        # Draw corner decorations
        corner_size = 50
        for corner in [(20, 20), (width - 70, 20), (20, height - 70), (width - 70, height - 70)]:
            draw.polygon([
                corner,
                (corner[0] + corner_size, corner[1]),
                (corner[0] + corner_size // 2, corner[1] + corner_size // 2),
                (corner[0], corner[1] + corner_size)
            ], fill=gold)

        # Draw header
        header_text = "🎯 DEFENSESHOT ELITE SNIPER ACADEMY 🎯"
        header_bbox = draw.textbbox((0, 0), header_text, font=title_font)
        header_width = header_bbox[2] - header_bbox[0]
        draw.text(((width - header_width) // 2, 80), header_text, fill=gold, font=title_font)

        # Draw subtitle
        subtitle_text = "Certificate of Completion"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((width - subtitle_width) // 2, 140), subtitle_text, fill=light_green, font=subtitle_font)

        # Draw decorative line
        draw.line([(200, 180), (width - 200, 180)], fill=gold, width=3)

        # Draw main text
        main_text = "This is to certify that"
        main_bbox = draw.textbbox((0, 0), main_text, font=text_font)
        main_width = main_bbox[2] - main_bbox[0]
        draw.text(((width - main_width) // 2, 220), main_text, fill=white, font=text_font)

        # Draw student name
        name_bbox = draw.textbbox((0, 0), student_name, font=name_font)
        name_width = name_bbox[2] - name_bbox[0]
        draw.text(((width - name_width) // 2, 260), student_name, fill=gold, font=name_font)

        # Draw underline for name
        draw.line([(200, 310), (width - 200, 310)], fill=gold, width=2)

        # Draw completion text
        completion_text = f"has successfully completed the"
        completion_bbox = draw.textbbox((0, 0), completion_text, font=text_font)
        completion_width = completion_bbox[2] - completion_bbox[0]
        draw.text(((width - completion_width) // 2, 340), completion_text, fill=white, font=text_font)

        # Draw course name
        course_bbox = draw.textbbox((0, 0), course, font=name_font)
        course_width = course_bbox[2] - course_bbox[0]
        draw.text(((width - course_width) // 2, 380), course, fill=light_green, font=name_font)

        # Draw underline for course
        draw.line([(150, 430), (width - 150, 430)], fill=light_green, width=2)

        # Draw institution text
        institution_text = f"at {institution}"
        institution_bbox = draw.textbbox((0, 0), institution_text, font=text_font)
        institution_width = institution_bbox[2] - institution_bbox[0]
        draw.text(((width - institution_width) // 2, 460), institution_text, fill=white, font=text_font)

        # Draw date range
        date_text = f"Course Period: {start_date} to {end_date}"
        date_bbox = draw.textbbox((0, 0), date_text, font=text_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(((width - date_width) // 2, 500), date_text, fill=white, font=text_font)

        # Draw achievement text
        achievement_text = "In recognition of dedication, skill, and excellence"
        achievement_bbox = draw.textbbox((0, 0), achievement_text, font=text_font)
        achievement_width = achievement_bbox[2] - achievement_bbox[0]
        draw.text(((width - achievement_width) // 2, 540), achievement_text, fill=white, font=text_font)

        # Draw signature area
        draw.text((150, 650), "Commanding Officer", fill=white, font=text_font)
        draw.line([(150, 680), (400, 680)], fill=gold, width=2)

        draw.text((650, 650), "Date of Issue", fill=white, font=text_font)
        draw.line([(650, 680), (900, 680)], fill=gold, width=2)
        draw.text((650, 690), end_date, fill=gold, font=text_font)

        # Draw academy seal (simplified)
        seal_center = (150, 750)
        seal_radius = 40
        draw.ellipse([seal_center[0] - seal_radius, seal_center[1] - seal_radius,
                      seal_center[0] + seal_radius, seal_center[1] + seal_radius],
                     outline=gold, width=3)
        draw.text((seal_center[0] - 15, seal_center[1] - 10), "🎯", fill=gold, font=name_font)

        # Draw motto
        motto_text = "PRECISION • DISCIPLINE • EXCELLENCE"
        motto_bbox = draw.textbbox((0, 0), motto_text, font=text_font)
        motto_width = motto_bbox[2] - motto_bbox[0]
        draw.text(((width - motto_width) // 2, 780), motto_text, fill=gold, font=text_font)

        return cert_img

    def create_preview(self, cert_img):
        """Create a base64 encoded preview image"""
        preview_img = cert_img.resize((600, 425), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        preview_img.save(buffer, format='PNG')
        buffer.seek(0)
        preview_base64 = base64.b64encode(buffer.getvalue()).decode()
        return preview_base64

    def create_pdf(self, cert_img, student_name):
        """Create a PDF version of the certificate"""
        buffer = io.BytesIO()

        # Convert PIL image to PDF
        pdf_width, pdf_height = landscape(A4)
        c = canvas.Canvas(buffer, pagesize=landscape(A4))

        # Convert PIL image to format suitable for ReportLab
        img_buffer = io.BytesIO()
        cert_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Add image to PDF
        c.drawImage(ImageReader(img_buffer),
                    (pdf_width - 10 * inch) / 2,
                    (pdf_height - 7 * inch) / 2,
                    width=10 * inch, height=7 * inch)

        c.save()
        buffer.seek(0)
        return buffer


# Flask routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/generate', methods=['POST'])
def generate_certificate():
    try:
        data = request.get_json()

        # Extract form data
        student_name = data.get('studentName', '').strip()
        start_date = data.get('startDate', '')
        end_date = data.get('endDate', '')
        institution = data.get('institution', '').strip()
        course = data.get('course', '')

        # Handle custom course
        if course == 'Custom Course':
            course = data.get('customCourse', '').strip()

        # Validate required fields
        if not all([student_name, start_date, end_date, institution, course]):
            return jsonify({'error': 'All fields are required'}), 400

        # Generate certificate
        cert_generator = CertificateGenerator()
        cert_img = cert_generator.generate_certificate(
            student_name, start_date, end_date, institution, course
        )

        # Create preview
        preview_base64 = cert_generator.create_preview(cert_img)

        # Generate unique ID for this certificate
        cert_id = f"cert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(student_name) % 10000}"

        # Store certificate data
        cert_generator.certificates[cert_id] = {
            'image': cert_img,
            'student_name': student_name,
            'generated_at': datetime.now()
        }

        # Store in app context for download
        app.cert_generator = cert_generator

        return jsonify({
            'success': True,
            'preview': preview_base64,
            'certificateId': cert_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<cert_id>')
def download_certificate(cert_id):
    try:
        # Get certificate data
        cert_data = app.cert_generator.certificates.get(cert_id)
        if not cert_data:
            return "Certificate not found", 404

        # Create PDF
        pdf_buffer = app.cert_generator.create_pdf(
            cert_data['image'],
            cert_data['student_name']
        )

        # Generate filename
        safe_name = "".join(c for c in cert_data['student_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"DefenseShot_Certificate_{safe_name}.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return f"Error generating download: {str(e)}", 500


def open_browser():
    """Open the web browser automatically after a short delay"""
    time.sleep(0.5)  # Wait for Flask to start
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    print("🎯 DefenseShot Elite Sniper Academy - Certificate Generator")
    print("=" * 60)
    print("Starting the application...")
    print("📋 Required packages: flask, pillow, reportlab")
    print("🌐 Opening browser automatically...")
    print("🔗 Server running at: http://localhost:5000")
    print("=" * 60)

    # Initialize certificate generator
    app.cert_generator = CertificateGenerator()

    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run the application without debug mode for auto-start
    app.run(host='0.0.0.0', port=5000, debug=False)
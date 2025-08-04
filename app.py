from flask import Flask, render_template, request, jsonify, send_file
import pdfkit
import tempfile
import os
from datetime import datetime
import logging
import subprocess
# Application version
__version__ = "1.0.2"

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configure temp directory - handle both local and container environments
if os.path.exists('/app'):
    # Running in container
    TEMP_DIR = '/app/temp'
else:
    # Running locally
    TEMP_DIR = os.path.join(os.getcwd(), 'temp')

# Ensure temp directory exists with proper permissions
os.makedirs(TEMP_DIR, exist_ok=True)
try:
    # Test write permissions
    test_file = os.path.join(TEMP_DIR, 'test_write.tmp')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print(f"✓ Temp directory configured: {TEMP_DIR}")
except Exception as e:
    print(f"✗ Warning: Temp directory may not be writable: {e}")
    # Fallback to system temp
    TEMP_DIR = tempfile.gettempdir()

# Auto-initialize container environment if needed
def init_container_environment():
    """Initialize container environment for PDF generation"""
    if os.path.exists('/app'):  # Running in container
        # Set up display environment
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':99'
            print("✓ Display environment set to :99")
        
        # Test if Xvfb is running, start if needed
        try:
            result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, text=True)
            if result.returncode != 0:  # Xvfb not running
                print("Starting Xvfb virtual display...")
                subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24', '-ac', '+extension', 'GLX', '+render', '-noreset'], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import time
                time.sleep(2)  # Give Xvfb time to start
                print("✓ Xvfb virtual display started")
            else:
                print("✓ Xvfb already running")
        except Exception as e:
            print(f"⚠ Could not manage Xvfb: {e}")

# Initialize container environment
init_container_environment()

# Check if wkhtmltopdf is available
def check_wkhtmltopdf():
    """Check if wkhtmltopdf is installed and accessible"""
    try:
        result = subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, check=True, text=True)
        print(f"✓ wkhtmltopdf found: {result.stdout.split()[1] if len(result.stdout.split()) > 1 else 'version unknown'}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"✗ wkhtmltopdf not found: {e}")
        return False

def test_wkhtmltopdf_functionality():
    """Test if wkhtmltopdf can actually generate PDFs"""
    if not WKHTMLTOPDF_INSTALLED:
        return False
    
    try:
        # Simple test HTML
        test_html = "<html><body><h1>Test</h1></body></html>"
        test_pdf = os.path.join(TEMP_DIR, 'wkhtmltopdf_test.pdf')
        
        # Basic test options - only use supported options
        test_options = {'quiet': None, 'page-size': 'A4'}
        if os.path.exists('/app'):  # Container mode
            # Just ensure DISPLAY is set for container
            if 'DISPLAY' not in os.environ:
                os.environ['DISPLAY'] = ':99'
        
        # Test PDF generation
        if pdfkit_config:
            pdfkit.from_string(test_html, test_pdf, options=test_options, configuration=pdfkit_config)
        else:
            pdfkit.from_string(test_html, test_pdf, options=test_options)
        
        # Check if file was created and has content
        if os.path.exists(test_pdf) and os.path.getsize(test_pdf) > 0:
            os.remove(test_pdf)  # Clean up
            print("✓ wkhtmltopdf functionality test passed")
            return True
        else:
            print("✗ wkhtmltopdf created empty or no file")
            return False
            
    except Exception as e:
        print(f"✗ wkhtmltopdf functionality test failed: {e}")
        return False

def _check_xvfb_running():
    """Check if Xvfb is running"""
    try:
        result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def _count_fonts():
    """Count available fonts"""
    try:
        result = subprocess.run(['fc-list'], capture_output=True, text=True)
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except:
        return 0

# Set wkhtmltopdf path for Windows if needed
WKHTMLTOPDF_INSTALLED = check_wkhtmltopdf()
pdfkit_config = None

if not WKHTMLTOPDF_INSTALLED:
    # Try common Windows installation paths
    possible_paths = [
        r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
        r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pdfkit_config = pdfkit.configuration(wkhtmltopdf=path)
            WKHTMLTOPDF_INSTALLED = True
            print(f"✓ Found wkhtmltopdf at: {path}")
            break
    
    if not WKHTMLTOPDF_INSTALLED:
        print("✗ wkhtmltopdf not found in common Windows locations")

# Test functionality after finding wkhtmltopdf
if WKHTMLTOPDF_INSTALLED:
    # Wait a moment for container environment to be ready
    if os.path.exists('/app'):
        import time
        time.sleep(1)
    
    # Test actual PDF generation capability
    WKHTMLTOPDF_FUNCTIONAL = test_wkhtmltopdf_functionality()
    if not WKHTMLTOPDF_FUNCTIONAL:
        print("⚠ wkhtmltopdf found but not functional - PDF generation may fail")
else:
    WKHTMLTOPDF_FUNCTIONAL = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Serve the main form page"""
    # Load logo as base64 for embedding
    import base64
    import os
    logo_base64 = None
    try:
        logo_path = os.path.join(app.static_folder, 'logo.png')
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode()
            logo_base64 = f"data:image/png;base64,{logo_data}"
    except Exception as e:
        logger.error(f"Error loading logo: {e}")
    
    return render_template('fuel_form.html', logo_base64=logo_base64, version=__version__)


@app.route('/version')
def version():
    """Return application version information"""
    return jsonify({
        'version': __version__,
        'app': 'FuelTime',
        'organization': 'Obion County Schools'
    })

@app.route('/debug/temp')
def debug_temp():
    """Debug endpoint to check temp directory status"""
    try:
        # Test wkhtmltopdf functionality
        wkhtmltopdf_test = False
        wkhtmltopdf_error = None
        
        if WKHTMLTOPDF_INSTALLED:
            try:
                # Test with simple HTML
                test_html = "<html><body><h1>Test PDF Generation</h1><p>This is a test.</p></body></html>"
                test_pdf_path = os.path.join(TEMP_DIR, 'test_pdf_generation.pdf')
                
                # Configure basic options for test
                test_options = {
                    'page-size': 'Letter',
                    'quiet': None,
                    'encoding': 'UTF-8'
                }
                
                # Add container-specific options
                if os.path.exists('/app'):
                    if 'DISPLAY' not in os.environ:
                        os.environ['DISPLAY'] = ':99'
                
                if pdfkit_config:
                    pdfkit.from_string(test_html, test_pdf_path, options=test_options, configuration=pdfkit_config)
                else:
                    pdfkit.from_string(test_html, test_pdf_path, options=test_options)
                
                wkhtmltopdf_test = os.path.exists(test_pdf_path)
                if wkhtmltopdf_test:
                    os.remove(test_pdf_path)  # Clean up test file
                    
            except Exception as e:
                wkhtmltopdf_error = str(e)
        
        temp_info = {
            'temp_dir': TEMP_DIR,
            'exists': os.path.exists(TEMP_DIR),
            'writable': os.access(TEMP_DIR, os.W_OK) if os.path.exists(TEMP_DIR) else False,
            'files': os.listdir(TEMP_DIR) if os.path.exists(TEMP_DIR) else [],
            'wkhtmltopdf_installed': WKHTMLTOPDF_INSTALLED,
            'wkhtmltopdf_functional': getattr(globals(), 'WKHTMLTOPDF_FUNCTIONAL', False),
            'wkhtmltopdf_error': wkhtmltopdf_error,
            'display_env': os.environ.get('DISPLAY', 'Not set'),
            'container_mode': os.path.exists('/app'),
            'xvfb_running': _check_xvfb_running(),
            'fonts_available': _count_fonts()
        }
        return jsonify(temp_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/submit', methods=['POST'])
def submit_form():
    """Process form submission and generate PDF"""
    try:
        # Get form data
        form_data = request.json
        logger.info(f"Received form data for {form_data.get('name', 'Unknown')}")
        
        # Generate PDF
        pdf_path = generate_pdf(form_data)
        
        # Move PDF to a permanent location for download
        download_filename = f"FuelReport_{form_data.get('name', 'Unknown')}_{form_data.get('month', '')}_{form_data.get('year', '')}.pdf"
        download_path = os.path.join(TEMP_DIR, download_filename)
        
        # Copy the file instead of renaming to avoid cross-device issues
        import shutil
        shutil.copy2(pdf_path, download_path)
        os.unlink(pdf_path)  # Remove original temp file
        
        return jsonify({
            'success': True,
            'message': 'Fuel report generated successfully! Click below to download.',
            'download_url': f'/download/{download_filename}'
        })
        
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating report: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve generated PDF files"""
    try:
        # Sanitize filename to prevent directory traversal
        import re
        if not re.match(r'^[\w\-_\. ]+$', filename) or '..' in filename:
            logger.error(f"Invalid filename attempted: {filename}")
            return jsonify({'error': 'Invalid filename'}), 400
            
        # Use the configured temp directory
        file_path = os.path.join(TEMP_DIR, filename)
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            # List available files for debugging
            try:
                available_files = os.listdir(TEMP_DIR) if os.path.exists(TEMP_DIR) else []
                logger.error(f"Available files in {TEMP_DIR}: {available_files}")
            except Exception as list_error:
                logger.error(f"Could not list temp directory: {list_error}")
            return jsonify({'error': 'File not found', 'requested': filename}), 404
            
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            logger.error(f"File not readable: {file_path}")
            return jsonify({'error': 'File not accessible'}), 403
            
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Error serving download: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_pdf(form_data):
    """Generate PDF from form data"""
    try:
        # Check if wkhtmltopdf is available and functional
        if not WKHTMLTOPDF_INSTALLED:
            raise Exception("wkhtmltopdf is not installed. Please check Docker image setup.")
        
        if not getattr(globals(), 'WKHTMLTOPDF_FUNCTIONAL', True):
            # Try to re-test functionality
            if not test_wkhtmltopdf_functionality():
                raise Exception("wkhtmltopdf is installed but not functional. Check container environment.")
        
        # Render the filled form as HTML
        filled_html = render_template('pdf_template.html', form_data=form_data)
        
        # Use the configured temp directory
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        pdf_filename = f"temp_fuel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(TEMP_DIR, pdf_filename)
        
        # Configure PDF options - using only supported options for patched wkhtmltopdf
        options = {
            'page-size': 'Letter',
            'orientation': 'Portrait',
            'margin-top': '0.2in',
            'margin-right': '0.2in',
            'margin-bottom': '0.2in',
            'margin-left': '0.2in',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'quiet': None
        }
        
        # Add container-specific options if running in container
        if os.path.exists('/app'):  # Running in container
            # Set DISPLAY environment variable if not set
            if 'DISPLAY' not in os.environ:
                os.environ['DISPLAY'] = ':99'
        
        # Generate PDF with proper configuration
        if pdfkit_config:
            pdfkit.from_string(filled_html, pdf_path, options=options, configuration=pdfkit_config)
        else:
            pdfkit.from_string(filled_html, pdf_path, options=options)
            
        logger.info(f"PDF generated successfully at {pdf_path}")
        
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise

@app.route('/preview-pdf', methods=['POST'])
def preview_pdf():
    """Generate and return PDF for preview/download"""
    try:
        form_data = request.json
        pdf_path = generate_pdf(form_data)
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"FuelReport_{form_data.get('name', 'Unknown')}_{form_data.get('month', '')}_{form_data.get('year', '')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF preview: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating PDF: {str(e)}'
        }), 500

@app.route('/logo')
def serve_logo():
    """Serve the logo file directly"""
    from flask import make_response
    response = make_response(send_file('static/logo.png', mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logo-data')
def serve_logo_data():
    """Serve the logo as base64 data URL"""
    import base64
    import os
    try:
        logo_path = os.path.join(app.static_folder, 'logo.png')
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{logo_data}"
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/test-logo')
def test_logo():
    """Test route to check if logo file exists"""
    import os
    logo_path = os.path.join(app.static_folder, 'logo.png')
    exists = os.path.exists(logo_path)
    return {
        'logo_path': logo_path,
        'exists': exists,
        'static_folder': app.static_folder,
        'static_url_path': app.static_url_path
    }

@app.route('/debug-logo')
def debug_logo():
    """Debug route to check logo loading"""
    import base64
    import os
    
    logo_path = os.path.join(app.static_folder, 'logo.png')
    file_exists = os.path.exists(logo_path)
    
    if file_exists:
        file_size = os.path.getsize(logo_path)
        try:
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode()
            data_url = f"data:image/png;base64,{logo_data}"
            
            return f"""
            <h1>Logo Debug Info</h1>
            <p>File exists: {file_exists}</p>
            <p>File size: {file_size} bytes</p>
            <p>Base64 length: {len(logo_data)} characters</p>
            <p>Data URL length: {len(data_url)} characters</p>
            <p>First 100 chars: {data_url[:100]}...</p>
            <h2>Test Image:</h2>
            <img src="{data_url}" alt="Test Logo" width="400" height="150" style="border: 2px solid red;">
            """
        except Exception as e:
            return f"Error reading file: {e}"
    else:
        return f"Logo file does not exist at: {logo_path}"

@app.route('/test-simple-image')
def test_simple_image():
    """Test with a tiny base64 image"""
    # This is a tiny 1x1 red pixel PNG
    tiny_red_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    return f"""
    <h1>Simple Image Test</h1>
    <h2>Tiny Red Pixel (should show a 1x1 red dot):</h2>
    <img src="data:image/png;base64,{tiny_red_pixel}" alt="Red Pixel" width="100" height="100" style="border: 2px solid blue; image-rendering: pixelated;">
    
    <h2>Blue Square (inline SVG for comparison):</h2>
    <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iYmx1ZSIvPjwvc3ZnPg==" alt="Blue Square" width="100" height="100" style="border: 2px solid green;">
    """

@app.route('/submit-timesheet', methods=['POST'])
def submit_timesheet():
    """Process timesheet form submission and generate PDF"""
    try:
        # Get form data
        form_data = request.json
        logger.info(f"Received timesheet data for {form_data.get('emp_name', 'Unknown')}")
        
        # Add date fields from the form (extract from date fields in the table)
        timesheet_data = {}
        
        # Copy all the form data
        for key, value in form_data.items():
            timesheet_data[key] = value
        
        # Extract dates from the date fields and add them to the data
        for week in range(1, 6):  # 5 weeks
            for day in ['m', 't', 'w', 'th', 'f']:
                date_key = f'date_{day}{week}'
                if date_key in form_data:
                    timesheet_data[date_key] = form_data[date_key]
        
        # Calculate total days worked
        total_days = 0
        for key, value in form_data.items():
            if key.startswith('total_hours_') and value and value.strip():
                try:
                    hours = float(value)
                    if hours > 0:
                        total_days += 1
                except (ValueError, TypeError):
                    pass
        
        timesheet_data['total_days'] = str(total_days)
        
        # Generate PDF
        pdf_path = generate_timesheet_pdf(timesheet_data)
        
        # Move PDF to a permanent location for download
        download_filename = f"Timesheet_{timesheet_data.get('emp_name', 'Unknown')}_{timesheet_data.get('time_period', '').replace('/', '_').replace(' ', '_')}.pdf"
        download_path = os.path.join(TEMP_DIR, download_filename)
        
        # Copy the file instead of renaming to avoid cross-device issues
        import shutil
        shutil.copy2(pdf_path, download_path)
        os.unlink(pdf_path)  # Remove original temp file
        
        return jsonify({
            'success': True,
            'message': 'Timesheet generated successfully! Click below to download.',
            'download_url': f'/download/{download_filename}'
        })
        
    except Exception as e:
        logger.error(f"Error processing timesheet submission: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating timesheet: {str(e)}'
        }), 500

def generate_timesheet_pdf(form_data):
    """Generate PDF from timesheet form data"""
    try:
        # Check if wkhtmltopdf is available and functional
        if not WKHTMLTOPDF_INSTALLED:
            raise Exception("wkhtmltopdf is not installed. Please check Docker image setup.")
            
        if not getattr(globals(), 'WKHTMLTOPDF_FUNCTIONAL', True):
            # Try to re-test functionality
            if not test_wkhtmltopdf_functionality():
                raise Exception("wkhtmltopdf is installed but not functional. Check container environment.")
        
        # Render the filled timesheet as HTML
        filled_html = render_template('timesheet_pdf_template.html', form_data=form_data)
        
        # Use the configured temp directory
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        pdf_filename = f"temp_timesheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(TEMP_DIR, pdf_filename)
        
        # Configure PDF options - using only supported options for patched wkhtmltopdf
        options = {
            'page-size': 'Letter',
            'orientation': 'Portrait',
            'margin-top': '0.3in',
            'margin-right': '0.3in',
            'margin-bottom': '0.3in',
            'margin-left': '0.3in',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'quiet': None
        }
        
        # Add container-specific options if running in container
        if os.path.exists('/app'):  # Running in container
            # Set DISPLAY environment variable if not set
            if 'DISPLAY' not in os.environ:
                os.environ['DISPLAY'] = ':99'
        
        # Generate PDF with proper configuration
        if pdfkit_config:
            pdfkit.from_string(filled_html, pdf_path, options=options, configuration=pdfkit_config)
        else:
            pdfkit.from_string(filled_html, pdf_path, options=options)
            
        logger.info(f"Timesheet PDF generated successfully at {pdf_path}")
        
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generating timesheet PDF: {str(e)}")
        raise

@app.route('/preview-timesheet-pdf', methods=['POST'])
def preview_timesheet_pdf():
    """Generate and return timesheet PDF for preview/download"""
    try:
        form_data = request.json
        
        # Process the form data similarly to submit_timesheet
        timesheet_data = {}
        
        # Copy all the form data
        for key, value in form_data.items():
            timesheet_data[key] = value
        
        # Calculate total days worked and total hours
        total_days = 0
        total_hours = 0.0
        
        # Debug logging
        print(f"Debug: Processing timesheet data for total hours calculation")
        
        for key, value in form_data.items():
            if key.startswith('total_hours_') and value and value.strip():
                try:
                    hours = float(value)
                    if hours > 0:
                        total_days += 1
                        total_hours += hours
                        print(f"Debug: Found hours for {key}: {hours}")
                except (ValueError, TypeError):
                    print(f"Debug: Invalid hours value for {key}: {value}")
                    pass
        
        print(f"Debug: Total calculated - Days: {total_days}, Hours: {total_hours}")
        
        timesheet_data['total_days'] = str(total_days)
        timesheet_data['total_hours_all'] = f"{total_hours:.2f}"
        
        print(f"Debug: Final timesheet data total_hours_all: {timesheet_data['total_hours_all']}")
        
        pdf_path = generate_timesheet_pdf(timesheet_data)
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Timesheet_{timesheet_data.get('emp_name', 'Unknown')}_{timesheet_data.get('time_period', '').replace('/', '_').replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating timesheet PDF preview: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating timesheet PDF: {str(e)}'
        }), 500

@app.route('/debug/environment')
def debug_environment():
    """Debug endpoint to check environment and JavaScript execution"""
    import os
    import platform
    import sys
    
    debug_info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'container_mode': os.path.exists('/app'),
        'display_env': os.environ.get('DISPLAY', 'Not set'),
        'temp_dir': TEMP_DIR,
        'wkhtmltopdf_installed': WKHTMLTOPDF_INSTALLED,
        'timezone': os.environ.get('TZ', 'Not set'),
    }
    
    # Test JavaScript execution capability
    try:
        import subprocess
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        debug_info['node_available'] = result.stdout.strip() if result.returncode == 0 else False
    except:
        debug_info['node_available'] = False
    
    return f"""
    <h1>Environment Debug Info</h1>
    <pre>{chr(10).join(f"{k}: {v}" for k, v in debug_info.items())}</pre>
    
    <h2>Test Form with JavaScript</h2>
    <div style="border: 1px solid #ccc; padding: 20px; margin: 20px 0;">
        <label>Time In: <input type="time" id="time_in" onchange="testCalculateHours()"></label><br><br>
        <label>Time Out: <input type="time" id="time_out" onchange="testCalculateHours()"></label><br><br>
        <label>Total Hours: <input type="text" id="total_hours" readonly></label><br><br>
        <label>Code: <input type="text" id="code" oninput="testClearTimes()"></label>
    </div>
    
    <script>
    function testCalculateHours() {{
        const timeIn = document.getElementById('time_in').value;
        const timeOut = document.getElementById('time_out').value;
        const totalHours = document.getElementById('total_hours');
        
        if (timeIn && timeOut) {{
            try {{
                const start = new Date(`2000-01-01 ${{timeIn}}`);
                const end = new Date(`2000-01-01 ${{timeOut}}`);
                const hours = (end - start) / (1000 * 60 * 60);
                totalHours.value = hours > 0 ? hours.toFixed(2) : '';
                console.log('Debug: Calculated hours:', hours);
            }} catch (error) {{
                console.error('Debug: Error calculating hours:', error);
                totalHours.value = 'ERROR';
            }}
        }}
    }}
    
    function testClearTimes() {{
        const code = document.getElementById('code').value;
        const timeIn = document.getElementById('time_in');
        const timeOut = document.getElementById('time_out');
        const totalHours = document.getElementById('total_hours');
        
        if (code.trim() !== '') {{
            const currentHours = totalHours.value;
            timeIn.value = '';
            timeOut.value = '';
            
            // Preserve hours or set default
            if (!currentHours && ['H', 'V', 'S'].includes(code.trim().toUpperCase())) {{
                totalHours.value = '8.00';
            }}
            console.log('Debug: Code entered:', code, 'Hours preserved/set:', totalHours.value);
        }}
    }}
    </script>
    """

@app.route('/debug/test-timesheet-data', methods=['POST'])
def debug_test_timesheet_data():
    """Debug endpoint to test timesheet data processing"""
    try:
        form_data = request.json or {}
        
        # Process the data the same way as the main endpoint
        total_days = 0
        total_hours = 0.0
        hours_breakdown = {}
        
        print(f"Debug: Received form data keys: {list(form_data.keys())}")
        
        for key, value in form_data.items():
            if key.startswith('total_hours_') and value and value.strip():
                try:
                    hours = float(value)
                    if hours > 0:
                        total_days += 1
                        total_hours += hours
                        hours_breakdown[key] = hours
                        print(f"Debug: Valid hours for {key}: {hours}")
                except (ValueError, TypeError) as e:
                    print(f"Debug: Invalid hours value for {key}: {value} - Error: {e}")
                    hours_breakdown[key] = f"INVALID: {value}"
        
        result = {
            'success': True,
            'total_days': total_days,
            'total_hours': total_hours,
            'hours_breakdown': hours_breakdown,
            'form_data_sample': {k: v for k, v in list(form_data.items())[:10]},  # First 10 items
            'total_form_fields': len(form_data)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

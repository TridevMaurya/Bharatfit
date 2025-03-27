import os
import logging
import shutil
from flask import Flask, request, render_template, jsonify, redirect, url_for, send_from_directory, send_file
from werkzeug.utils import secure_filename
import base64
from PIL import Image
from rembg import remove

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import custom functions
from verify import overlay_cloth_on_model
from verify2 import overlay_lower_body_garment

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_testing")

# Directory setup
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = os.path.join('static', 'results')
COLLECTION_FOLDER = os.path.join('static', 'images', 'collection')

# Ensure directories exist
for folder in [UPLOAD_FOLDER, STATIC_FOLDER, COLLECTION_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
        logger.info(f"Created directory: {folder}")

# Copy images from attached_assets to collection folder (if available)
ASSETS_FOLDER = 'attached_assets'
if os.path.exists(ASSETS_FOLDER):
    try:
        image_files = [f for f in os.listdir(ASSETS_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]
        for image_file in image_files:
            src = os.path.join(ASSETS_FOLDER, image_file)
            dst = os.path.join(COLLECTION_FOLDER, image_file)
            if not os.path.exists(dst) and os.path.exists(src):
                shutil.copy2(src, dst)
                logger.info(f"Copied {image_file} to collection folder")
    except Exception as e:
        logger.warning(f"Could not copy from attached_assets: {str(e)}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# Updated product catalog with actual images
PRODUCTS = {
    'women': [
        {
            'id': 1,
            'brand': 'BharatFit',
            'name': 'Navy Polka Dot Top',
            'price': 1299,
            'original_price': 1999,
            'discount': 35,
            'image': '06802_00.jpg',
            'type': 'upper_body'
        },
        {
            'id': 2,
            'brand': 'BharatFit',
            'name': 'Black Lace Sleeve Top',
            'price': 1499,
            'original_price': 2499,
            'discount': 40,
            'image': '07429_00.jpg',
            'type': 'upper_body'
        },
        {
            'id': 3,
            'brand': 'BharatFit',
            'name': 'Floral Print Cami',
            'price': 999,
            'original_price': 1499,
            'discount': 33,
            'image': '08348_00.jpg',
            'type': 'upper_body'
        },
        {
            'id': 4,
            'brand': 'BharatFit',
            'name': 'Grey Lace Trim Cami',
            'price': 899,
            'original_price': 1299,
            'discount': 30,
            'image': '09933_00.jpg',
            'type': 'upper_body'
        },
        {
            'id': 5,
            'brand': 'BharatFit',
            'name': 'Burgundy Velvet Top',
            'price': 1699,
            'original_price': 2499,
            'discount': 32,
            'image': '11028_00.jpg',
            'type': 'upper_body'
        }
    ],
    'men': [
        {
            'id': 6,
            'brand': 'BharatFit',
            'name': 'Classic Blue Blazer',
            'price': 3999,
            'original_price': 5999,
            'discount': 33,
            'image': 'steptodown.com828109.jpg',
            'type': 'upper_body'
        }
    ]
}

@app.route('/')
def index():
    logger.debug("Accessing index route, redirecting to women's page")
    return redirect(url_for('women'))

@app.route('/men')
def men():
    logger.debug("Accessing men's products route")
    return render_template('product_listing.html', products=PRODUCTS['men'], category='Men\'s Fashion')

@app.route('/women')
def women():
    logger.debug("Accessing women's products route")
    return render_template('product_listing.html', products=PRODUCTS['women'], category='Women\'s Fashion')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    logger.debug(f"Accessing product detail route for product ID: {product_id}")
    product = next(
        (item for sublist in PRODUCTS.values() for item in sublist if item['id'] == product_id),
        None
    )
    if product:
        logger.debug(f"Found product for ID {product_id}: {product['name']}")
        return render_template('product_detail.html', product=product)
    logger.debug(f"Product with ID {product_id} not found, redirecting to women's page")
    return redirect(url_for('women'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    logger.debug(f"Accessing upload route with method: {request.method}")
    
    # Handle product_id parameter if provided
    product_id = request.args.get('product_id')
    product = None
    
    if product_id:
        try:
            product_id = int(product_id)
            product = next(
                (item for sublist in PRODUCTS.values() for item in sublist if item['id'] == product_id),
                None
            )
            logger.debug(f"Found product for ID {product_id}: {product['name'] if product else 'None'}")
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid product_id: {str(e)}")
    
    if request.method == 'POST':
        try:
            model_image = request.files.get('model_image')
            clothes_image = request.files.get('clothes_image') 
            product_id_from_form = request.form.get('product_id')
            
            # If model_image is None, return an error
            if model_image is None:
                logger.error("No model image provided")
                return jsonify({'error': 'Please upload your photo to try on clothes'}), 400
            
            # If product_id is provided in the form, use it to get the clothing image
            if product_id_from_form and (clothes_image is None or not hasattr(clothes_image, 'filename') or not clothes_image.filename):
                try:
                    product_id_from_form = int(product_id_from_form)
                    logger.debug(f"Looking for product with ID: {product_id_from_form}")
                    
                    # Find the product in our catalog
                    selected_product = None
                    for category, products in PRODUCTS.items():
                        for product in products:
                            if product['id'] == product_id_from_form:
                                selected_product = product
                                logger.debug(f"Found product in '{category}' category: {product['name']}")
                                break
                        if selected_product:
                            break
                    
                    if selected_product:
                        product_image_path = os.path.join(COLLECTION_FOLDER, selected_product['image'])
                        logger.debug(f"Looking for product image at: {product_image_path}")
                        
                        # Set the clothes_filename first, so it's always available
                        clothes_filename = selected_product['image']
                        logger.debug(f"Set clothes_filename to: {clothes_filename}")
                        
                        if os.path.exists(product_image_path):
                            logger.debug(f"Found product image: {selected_product['image']}")
                            with open(product_image_path, 'rb') as f:
                                clothes_image_content = f.read()
                                logger.debug(f"Read {len(clothes_image_content)} bytes from product image")
                        else:
                            logger.error(f"Product image not found: {product_image_path}")
                            # Check if the file exists in the attached_assets folder
                            alt_image_path = os.path.join(ASSETS_FOLDER, selected_product['image'])
                            logger.debug(f"Checking alternative location: {alt_image_path}")
                            
                            if os.path.exists(alt_image_path):
                                logger.debug(f"Found product image in assets folder: {alt_image_path}")
                                # Copy the file to the collection folder
                                shutil.copy2(alt_image_path, product_image_path)
                                logger.info(f"Copied {selected_product['image']} to collection folder")
                                
                                with open(product_image_path, 'rb') as f:
                                    clothes_image_content = f.read()
                                    logger.debug(f"Read {len(clothes_image_content)} bytes from product image (alt location)")
                            else:
                                return jsonify({'error': f"Product image '{selected_product['image']}' not found"}), 400
                    else:
                        logger.error(f"Product with ID {product_id_from_form} not found")
                        return jsonify({'error': f"Product with ID {product_id_from_form} not found"}), 400
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid product_id in form: {str(e)}")
                    return jsonify({'error': f"Invalid product ID: {str(e)}"}), 400
            
            garment_type = request.form.get('garment_type')

            if not all([model_image, garment_type]):
                logger.error("Missing required files or garment type")
                return jsonify({'error': 'Missing required files or garment type'}), 400

            # Ensure model image has a filename
            if not hasattr(model_image, 'filename') or not model_image.filename:
                logger.error("Model image has no filename")
                return jsonify({'error': 'The uploaded image appears to be invalid. Please try a different photo.'}), 400
                
            model_filename = secure_filename(model_image.filename)
            
            # Only initialize clothes_filename if it doesn't already exist
            # This prevents overwriting the value we set earlier
            if 'clothes_filename' not in locals() or clothes_filename is None:
                clothes_filename = None
                clothes_image_content = None
            else:
                logger.debug(f"Keeping existing clothes_filename: {clothes_filename}")
            
            # At this point, if we have product_id_from_form, we should already have clothes_filename and clothes_image_content set
            # Just do a final check in case something went wrong
            
            if product_id_from_form:
                if 'clothes_filename' not in locals() or not clothes_filename:
                    logger.error("No clothes image found for the selected product ID")
                    return jsonify({'error': 'Something went wrong finding the product image. Please try again or choose a different product.'}), 400
                logger.debug(f"Using product image: {clothes_filename}")
            elif clothes_image and hasattr(clothes_image, 'filename') and clothes_image.filename:
                clothes_filename = secure_filename(clothes_image.filename)
                logger.debug(f"Using uploaded clothes image: {clothes_filename}")
            else:
                logger.error("No clothes image provided")
                return jsonify({'error': 'Please upload a clothing item or select a product'}), 400
            
            model_image_path = os.path.join(app.config['UPLOAD_FOLDER'], model_filename)
            clothes_image_path = os.path.join(app.config['UPLOAD_FOLDER'], clothes_filename)
            clothes_no_bg_path = os.path.join(app.config['UPLOAD_FOLDER'], 'no_bg_' + clothes_filename)
            output_filename = 'output_' + model_filename
            output_image_path = os.path.join(app.config['STATIC_FOLDER'], output_filename)

            model_image.save(model_image_path)
            
            if clothes_image and hasattr(clothes_image, 'filename') and clothes_image.filename:
                clothes_image.save(clothes_image_path)
                logger.debug(f"Saved uploaded clothes image to: {clothes_image_path}")
            elif clothes_image_content:
                with open(clothes_image_path, 'wb') as f:
                    f.write(clothes_image_content)
                logger.debug(f"Saved product clothes image to: {clothes_image_path}")

            logger.info("Removing background from clothes image")
            try:
                with open(clothes_image_path, 'rb') as input_file:
                    input_bytes = input_file.read()
                output_bytes = remove(input_bytes)
                with open(clothes_no_bg_path, 'wb') as output_file:
                    output_file.write(output_bytes)
            except Exception as e:
                logger.error(f"Background removal failed: {str(e)}")
                return jsonify({'error': f'Background removal failed: {str(e)}'}), 500

            logger.info("Processing garment overlay")
            try:
                if garment_type == 'lower_body':
                    output_path, message = overlay_lower_body_garment(
                        model_image_path, clothes_no_bg_path, output_image_path
                    )
                else:
                    output_path, message = overlay_cloth_on_model(
                        model_image_path, clothes_no_bg_path, output_image_path
                    )

                if not output_path:
                    logger.error(f"Overlay failed: {message}")
                    return jsonify({'error': message}), 400

                # Make sure the results directory exists
                results_dir = os.path.join(app.config['STATIC_FOLDER'], 'results')
                if not os.path.exists(results_dir):
                    os.makedirs(results_dir)
                    
                # Save paths for adjustment sliders to use
                original_model_path = os.path.join(results_dir, 'model_' + model_filename)
                original_clothes_path = os.path.join(results_dir, 'clothes_' + clothes_filename)
                
                # Copy the original files for the adjustment feature
                shutil.copy(model_image_path, original_model_path)
                shutil.copy(clothes_no_bg_path, original_clothes_path)
                
                with open(output_image_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Get the relative paths for the front-end
                original_model_rel = 'results/model_' + model_filename
                original_clothes_rel = 'results/clothes_' + clothes_filename
                output_rel = 'results/output_' + model_filename
                
                # If we have a product, pass it to the result template
                if product_id_from_form:
                    selected_product = next(
                        (item for sublist in PRODUCTS.values() for item in sublist if item['id'] == product_id_from_form),
                        None
                    )
                    return render_template('result.html', 
                                          img_data=img_data, 
                                          product=selected_product,
                                          model_img=original_model_rel,
                                          clothes_img=original_clothes_rel,
                                          output_img=output_rel,
                                          garment_type=garment_type)
                else:
                    return render_template('result.html', 
                                          img_data=img_data,
                                          model_img=original_model_rel,
                                          clothes_img=original_clothes_rel,
                                          output_img=output_rel,
                                          garment_type=garment_type)

            except Exception as e:
                logger.error(f"Try-on processing failed: {str(e)}")
                return jsonify({'error': f'Try-on processing failed: {str(e)}'}), 500

            finally:
                # Cleanup temporary files
                for path in [model_image_path, clothes_image_path, clothes_no_bg_path]:
                    if os.path.exists(path):
                        os.remove(path)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

    return render_template('upload.html', product=product)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return redirect(url_for('women'))

    results = []
    for category in PRODUCTS.values():
        results.extend([p for p in category if query in p['name'].lower() or query in p['brand'].lower()])

    return render_template('product_listing.html', products=results, category='Search Results')

@app.route('/download')
def download():
    """Route to download the website as a ZIP file for local installation"""
    try:
        # Run the script to create a fresh zip file
        import create_archive
        create_archive.create_zip_for_local_deployment()
        
        # Send the file to the user
        return send_file('virtual_tryon_website.zip', 
                        mimetype='application/zip',
                        as_attachment=True, 
                        download_name='virtual_tryon_website.zip')
    except Exception as e:
        logger.error(f"Error creating or downloading ZIP file: {str(e)}")
        return jsonify({'error': f'Failed to create download: {str(e)}'}), 500
        
@app.route('/adjust_overlay', methods=['POST'])
def adjust_overlay():
    """Route to adjust the position and size of the clothing overlay"""
    try:
        data = request.json
        # Ensure the results directory exists
        results_dir = os.path.join(app.config['STATIC_FOLDER'], 'results')
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        model_path = os.path.join(app.config['STATIC_FOLDER'], data['model_img'])
        clothes_path = os.path.join(app.config['STATIC_FOLDER'], data['clothes_img'])
        output_path = os.path.join(app.config['STATIC_FOLDER'], data['output_img'])
        
        x_offset = data.get('x_offset', 0)
        y_offset = data.get('y_offset', 0)
        size_factor = data.get('size_factor', 1.0)
        garment_type = data.get('garment_type', 'upper')
        
        # Load the images
        import cv2
        model_img = cv2.imread(model_path)
        clothes_img = cv2.imread(clothes_path, cv2.IMREAD_UNCHANGED)
        
        if garment_type == 'upper':
            # Apply adjustments for upper body garments
            from verify import adjust_cloth_overlay
            success, output_img = adjust_cloth_overlay(
                model_img, clothes_img, x_offset, y_offset, size_factor
            )
        else:
            # Apply adjustments for lower body garments
            from verify2 import adjust_lower_garment_overlay
            success, output_img = adjust_lower_garment_overlay(
                model_img, clothes_img, x_offset, y_offset, size_factor
            )
            
        if not success:
            return jsonify({'error': 'Failed to adjust overlay'}), 400
            
        # Save the adjusted output
        cv2.imwrite(output_path, output_img)
        
        # Convert the image to base64 for direct display
        _, buffer = cv2.imencode('.jpg', output_img)
        img_data = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({'success': True, 'img_data': img_data})
        
    except Exception as e:
        logger.error(f"Error adjusting overlay: {str(e)}")
        return jsonify({'error': f'Adjustment failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Route for Databricks App health checks"""
    return jsonify({
        'status': 'healthy',
        'app': 'BharatFit Virtual Try-On',
        'version': '1.0'
    })
    
if __name__ == '__main__':
    logger.info("Starting Flask application on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
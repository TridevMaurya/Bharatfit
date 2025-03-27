import os
import logging
import shutil
import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import tempfile
from rembg import remove

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import custom functions
from verify import overlay_cloth_on_model
from verify2 import overlay_lower_body_garment

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

# Set page config
st.set_page_config(
    page_title="BharatFit - Virtual Try-On Fashion Store",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define CSS
st.markdown("""
<style>
:root {
    --primary-color: #F13AB1;
    --primary-color-light: #FF66C4;
    --accent-color-1: #F05524;
    --accent-color-2: #FD913C;
    --text-color: #333333;
    --light-bg: #F8F9FA;
}

/* Card styling */
.product-card {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    transition: transform 0.3s;
    display: flex;
    flex-direction: column;
}

.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

.product-img-container {
    height: 250px;
    overflow: hidden;
    position: relative;
}

.product-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.product-img:hover {
    transform: scale(1.05);
}

.product-details {
    padding: 15px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.product-brand {
    font-size: 0.9rem;
    color: #888;
    margin-bottom: 5px;
}

.product-name {
    font-weight: 600;
    margin-bottom: 10px;
    font-size: 1.1rem;
}

.price-container {
    display: flex;
    align-items: center;
    margin-top: auto;
}

.product-price {
    font-weight: 700;
    color: #111;
    font-size: 1.1rem;
}

.product-original-price {
    text-decoration: line-through;
    color: #999;
    margin-left: 8px;
    font-size: 0.9rem;
}

.product-discount {
    background-color: var(--accent-color-2);
    color: white;
    padding: 3px 8px;
    border-radius: 3px;
    margin-left: auto;
    font-size: 0.8rem;
    font-weight: 600;
}

.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    transition: background-color 0.3s;
}

.btn-primary:hover {
    background-color: var(--primary-color-light);
    border-color: var(--primary-color-light);
}

.btn-secondary {
    background-color: var(--accent-color-1);
    border-color: var(--accent-color-1);
    transition: background-color 0.3s;
}

.btn-secondary:hover {
    background-color: var(--accent-color-2);
    border-color: var(--accent-color-2);
}

.logo {
    font-weight: bold;
    background: linear-gradient(45deg, var(--primary-color), var(--accent-color-1), var(--accent-color-2));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
    font-size: 1.8rem;
    margin-bottom: 1rem;
}

/* Streamlit specific overrides */
.stButton>button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}

.stButton>button:hover {
    background-color: var(--primary-color-light);
}

.try-on-btn {
    background-color: var(--accent-color-1) !important;
}

.try-on-btn:hover {
    background-color: var(--accent-color-2) !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 20px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: #f1f1f1;
    border-radius: 4px 4px 0 0;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}

.stTabs [aria-selected="true"] {
    background-color: var(--primary-color-light);
    color: white;
}

footer {
    text-align: center;
    padding: 20px 0;
    font-size: 0.8rem;
    color: gray;
    margin-top: 50px;
    border-top: 1px solid #eee;
}

.result-image {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Add more responsive styles */
@media (max-width: 768px) {
    .product-img-container {
        height: 200px;
    }
}
</style>
""", unsafe_allow_html=True)

# Function to get image as base64
def get_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Function to display a product card
def display_product_card(product):
    image_path = os.path.join(COLLECTION_FOLDER, product['image'])
    if os.path.exists(image_path):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image_path, use_column_width=True)
        with col2:
            st.markdown(f"<p class='product-brand'>{product['brand']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h3 class='product-name'>{product['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='price-container'>
                <span class='product-price'>₹{product['price']}</span>
                <span class='product-original-price'>₹{product['original_price']}</span>
                <span class='product-discount'>{product['discount']}% OFF</span>
            </div>
            """, unsafe_allow_html=True)
            st.button("Try this on", key=f"try_{product['id']}", on_click=lambda: st.session_state.update({'selected_product': product, 'page': 'upload'}))
    else:
        st.error(f"Image not found: {image_path}")

# Function to display product catalog
def display_products(category):
    st.markdown(f"<h2>{category.title()} Fashion</h2>", unsafe_allow_html=True)
    
    if category == 'women':
        products = PRODUCTS['women']
    else:
        products = PRODUCTS['men']
    
    # Display products in a grid
    cols = st.columns(3)
    for i, product in enumerate(products):
        with cols[i % 3]:
            image_path = os.path.join(COLLECTION_FOLDER, product['image'])
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
                st.markdown(f"<p class='product-brand'>{product['brand']}</p>", unsafe_allow_html=True)
                st.markdown(f"<h3 class='product-name'>{product['name']}</h3>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class='price-container'>
                    <span class='product-price'>₹{product['price']}</span>
                    <span class='product-original-price'>₹{product['original_price']}</span>
                    <span class='product-discount'>{product['discount']}% OFF</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Create a unique key for each button
                if st.button("View Details", key=f"view_{product['id']}"):
                    st.session_state.page = 'product_detail'
                    st.session_state.product_id = product['id']
                
                if st.button("Try On", key=f"try_{product['id']}", type="primary"):
                    st.session_state.page = 'upload'
                    st.session_state.selected_product = product

# Function to display product detail
def product_detail_page(product_id):
    product = next(
        (item for sublist in PRODUCTS.values() for item in sublist if item['id'] == product_id),
        None
    )
    
    if product:
        st.markdown(f"<h1>{product['name']}</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            image_path = os.path.join(COLLECTION_FOLDER, product['image'])
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            else:
                st.error(f"Image not found: {image_path}")
        
        with col2:
            st.markdown(f"<p class='product-brand'>{product['brand']}</p>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='price-container'>
                <span class='product-price'>₹{product['price']}</span>
                <span class='product-original-price'>₹{product['original_price']}</span>
                <span class='product-discount'>{product['discount']}% OFF</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Product Details")
            st.markdown("- Premium quality fabric")
            st.markdown("- Comfortable fit")
            st.markdown("- Machine washable")
            st.markdown("- Suitable for casual and formal occasions")
            
            if st.button("Try this On", key="try_detail", type="primary"):
                st.session_state.page = 'upload'
                st.session_state.selected_product = product
                st.experimental_rerun()
            
            if st.button("Back to Products", key="back_to_products"):
                if product['id'] <= 5:  # Women's products
                    st.session_state.page = 'women'
                else:  # Men's products
                    st.session_state.page = 'men'
                st.experimental_rerun()
    else:
        st.error("Product not found")
        if st.button("Back to Women's Fashion"):
            st.session_state.page = 'women'
            st.experimental_rerun()

# Function for virtual try-on page
def upload_page():
    st.markdown("<h1>Virtual Try-On Studio</h1>", unsafe_allow_html=True)
    
    selected_product = st.session_state.get('selected_product', None)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload Your Photo")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        garment_type = "upper_body"  # Default value
        st.markdown("### Select Garment Type")
        garment_options = ["upper_body", "lower_body"]
        garment_type = st.radio("", garment_options, index=0, horizontal=True)
        
        if selected_product:
            st.markdown("### Selected Product")
            image_path = os.path.join(COLLECTION_FOLDER, selected_product['image'])
            if os.path.exists(image_path):
                st.image(image_path, width=200)
                st.markdown(f"**{selected_product['name']}**")
                st.markdown(f"₹{selected_product['price']}")
    
    with col2:
        if selected_product is None:
            st.markdown("### Choose a Product")
            st.markdown("Please select a product from our catalog first.")
            
            if st.button("Browse Women's Fashion"):
                st.session_state.page = 'women'
                st.experimental_rerun()
                
            if st.button("Browse Men's Fashion"):
                st.session_state.page = 'men'
                st.experimental_rerun()
        else:
            st.markdown("### Try On Instructions")
            st.markdown("1. Upload a clear, front-facing photo")
            st.markdown("2. Make sure you're standing straight")
            st.markdown("3. The photo should show your full upper body")
            st.markdown("4. Avoid busy backgrounds for best results")
            
            # Process button
            process_btn = st.button("Process Virtual Try-On", type="primary", disabled=uploaded_file is None)
            
            if process_btn and uploaded_file is not None:
                with st.spinner("Processing your image..."):
                    try:
                        # Create temp files
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as model_temp:
                            model_temp.write(uploaded_file.getvalue())
                            model_image_path = model_temp.name
                        
                        # Get product image path
                        product_image_path = os.path.join(COLLECTION_FOLDER, selected_product['image'])
                        if not os.path.exists(product_image_path):
                            st.error(f"Product image not found: {product_image_path}")
                            return
                        
                        # Create temp file for product without background
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as clothes_no_bg_temp:
                            clothes_no_bg_path = clothes_no_bg_temp.name
                        
                        # Create output temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as output_temp:
                            output_image_path = output_temp.name
                        
                        # Remove background from clothes image
                        st.info("Removing background from clothes image...")
                        with open(product_image_path, 'rb') as input_file:
                            input_bytes = input_file.read()
                        output_bytes = remove(input_bytes)
                        with open(clothes_no_bg_path, 'wb') as output_file:
                            output_file.write(output_bytes)
                        
                        # Process garment overlay
                        st.info("Processing garment overlay...")
                        if garment_type == 'lower_body':
                            output_path, message = overlay_lower_body_garment(
                                model_image_path, clothes_no_bg_path, output_image_path
                            )
                        else:
                            output_path, message = overlay_cloth_on_model(
                                model_image_path, clothes_no_bg_path, output_image_path
                            )
                        
                        if not output_path:
                            st.error(f"Overlay failed: {message}")
                            return
                        
                        # Store result in session state
                        st.session_state.result_image_path = output_path
                        st.session_state.page = 'result'
                        st.experimental_rerun()
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                    finally:
                        # Cleanup temp files (commented out for debugging)
                        # for path in [model_image_path, clothes_no_bg_path]:
                        #     if os.path.exists(path):
                        #         os.remove(path)
                        pass

# Function to display try-on results
def result_page():
    st.markdown("<h1>Virtual Try-On Result</h1>", unsafe_allow_html=True)
    
    result_image_path = st.session_state.get('result_image_path')
    selected_product = st.session_state.get('selected_product')
    
    if result_image_path and os.path.exists(result_image_path):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(result_image_path, use_column_width=True, caption="Your Virtual Try-On")
            
            # Save a copy to the static results folder for reference
            output_filename = f"output_{os.path.basename(result_image_path)}"
            output_saved_path = os.path.join(STATIC_FOLDER, output_filename)
            shutil.copy2(result_image_path, output_saved_path)
            logger.info(f"Saved result image to: {output_saved_path}")
        
        with col2:
            if selected_product:
                st.markdown("<h3>Product Details</h3>", unsafe_allow_html=True)
                image_path = os.path.join(COLLECTION_FOLDER, selected_product['image'])
                if os.path.exists(image_path):
                    st.image(image_path, width=200)
                st.markdown(f"**{selected_product['name']}**")
                st.markdown(f"₹{selected_product['price']}")
                st.markdown(f"<span class='product-original-price'>₹{selected_product['original_price']}</span> <span class='product-discount'>{selected_product['discount']}% OFF</span>", unsafe_allow_html=True)
                
                st.markdown("### How does it look?")
                st.markdown("- The AI has matched the garment to your body")
                st.markdown("- Consider the fit, color, and style")
                st.markdown("- Try on more items to compare")
            
            # Action buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Try Another", key="try_another"):
                    st.session_state.page = 'upload'
                    st.experimental_rerun()
            with col_b:
                if st.button("Browse More", key="browse_more"):
                    st.session_state.page = 'women'  # Default to women's page
                    st.experimental_rerun()
    else:
        st.error("Result image not found. Please try again.")
        if st.button("Back to Try-On"):
            st.session_state.page = 'upload'
            st.experimental_rerun()

# Navigation sidebar
def sidebar_navigation():
    st.sidebar.markdown("<div class='logo'>BHARATFIT</div>", unsafe_allow_html=True)
    
    # Main navigation
    if st.sidebar.button("Women's Fashion", key="nav_women"):
        st.session_state.page = 'women'
        st.experimental_rerun()
    
    if st.sidebar.button("Men's Fashion", key="nav_men"):
        st.session_state.page = 'men'
        st.experimental_rerun()
    
    if st.sidebar.button("Virtual Try-On Studio", key="nav_tryon"):
        st.session_state.page = 'upload'
        st.experimental_rerun()
    
    # Search function
    st.sidebar.markdown("### Search")
    search_query = st.sidebar.text_input("Search products...", key="search_box")
    search_button = st.sidebar.button("Search")
    
    if search_button and search_query:
        results = []
        query = search_query.lower()
        for category in PRODUCTS.values():
            results.extend([p for p in category if query in p['name'].lower() or query in p['brand'].lower()])
        
        st.session_state.search_results = results
        st.session_state.search_query = search_query
        st.session_state.page = 'search_results'
        st.experimental_rerun()

# Display search results
def search_results_page():
    query = st.session_state.search_query
    results = st.session_state.search_results
    
    st.markdown(f"<h2>Search Results for '{query}'</h2>", unsafe_allow_html=True)
    
    if not results:
        st.info("No products found matching your search.")
        if st.button("Browse Women's Fashion"):
            st.session_state.page = 'women'
            st.experimental_rerun()
    else:
        st.markdown(f"Found {len(results)} products")
        
        # Display products in a grid
        cols = st.columns(3)
        for i, product in enumerate(results):
            with cols[i % 3]:
                image_path = os.path.join(COLLECTION_FOLDER, product['image'])
                if os.path.exists(image_path):
                    st.image(image_path, use_column_width=True)
                    st.markdown(f"<p class='product-brand'>{product['brand']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<h3 class='product-name'>{product['name']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class='price-container'>
                        <span class='product-price'>₹{product['price']}</span>
                        <span class='product-original-price'>₹{product['original_price']}</span>
                        <span class='product-discount'>{product['discount']}% OFF</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a unique key for each button
                    if st.button("View Details", key=f"search_view_{product['id']}"):
                        st.session_state.page = 'product_detail'
                        st.session_state.product_id = product['id']
                    
                    if st.button("Try On", key=f"search_try_{product['id']}", type="primary"):
                        st.session_state.page = 'upload'
                        st.session_state.selected_product = product

# Main application
def main():
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'women'  # Default landing page
    
    # Display sidebar navigation
    sidebar_navigation()
    
    # Main content based on current page
    current_page = st.session_state.page
    
    if current_page == 'women':
        display_products('women')
    elif current_page == 'men':
        display_products('men')
    elif current_page == 'product_detail':
        product_detail_page(st.session_state.product_id)
    elif current_page == 'upload':
        upload_page()
    elif current_page == 'result':
        result_page()
    elif current_page == 'search_results':
        search_results_page()
    
    # Footer
    st.markdown("""
    <footer>
        <p>© 2025 BharatFit - Virtual Try-On Fashion Store. All rights reserved.</p>
    </footer>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
# Virtual Try-On E-Commerce Website Setup Guide

This guide will help you set up and run the Virtual Try-On E-Commerce website on your local machine. The application is available in two versions: a traditional Flask web application and a Streamlit application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Download the Project

Download the ZIP file of the project and extract it to your desired location.

### 2. Create a Virtual Environment (Recommended)

Open a terminal/command prompt and navigate to the project folder, then run:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Packages

Run the following command to install all required packages:

```bash
pip install -r my_requirements.txt
```

This will install all necessary packages including Flask, Streamlit, OpenCV, MediaPipe, and other dependencies.

**Note**: If you're on an M1/M2 Mac, you may need to install specific versions of certain packages. Please refer to the official documentation for those packages.

### 4. Create Required Directories

Make sure the following directories exist in your project folder:

```bash
mkdir -p uploads
mkdir -p static/images/collection
mkdir -p static/results
```

### 5. Run the Application

#### Option A: Run the Flask Web Application

Start the Flask application:

```bash
# Windows/macOS/Linux
python main.py
```

The server will start, and you should see output indicating it's running on http://0.0.0.0:5000/.

#### Option B: Run the Streamlit Application

Start the Streamlit application:

```bash
# Windows/macOS/Linux
streamlit run streamlit_app.py
```

The Streamlit server will start, and you should see output indicating it's running on http://localhost:8501/.

### 6. Access the Website

For the Flask version:
```
http://localhost:5000/
```

For the Streamlit version:
```
http://localhost:8501/
```

You should now see the women's clothing page (the main landing page).

## Project Structure

- `main.py` - The main Flask application file
- `streamlit_app.py` - The Streamlit application version
- `verify.py` - Contains functions for upper body virtual try-on
- `verify2.py` - Contains functions for lower body virtual try-on
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates for the Flask website
- `uploads/` - Temporary folder for uploaded images
- `.streamlit/` - Configuration for the Streamlit application

## Features

1. **Virtual Try-On**: Upload your photo and try on clothes virtually
2. **Product Browsing**: View men's and women's fashion collections
3. **Product Details**: See detailed information about each product
4. **Search**: Find products by name or brand

## Differences Between Flask and Streamlit Versions

### Flask Version:
- Traditional web interface with standard HTML/CSS
- Multiple pages with standard navigation
- Requires separate template files
- Familiar web-app experience

### Streamlit Version:
- Modern, interactive, single-page application
- Built-in components and widgets
- Easier to modify and extend
- More reactive interface

## Troubleshooting

### Common Issues and Solutions

1. **Missing Modules**: If you get an error about missing modules, make sure you've installed all required packages.

   ```bash
   pip install -r my_requirements.txt
   ```

2. **Port Already in Use**: 
   - For Flask: If port 5000 is already in use, you can change the port number in `main.py`
   - For Streamlit: If port 8501 is already in use, run with a different port: `streamlit run streamlit_app.py --server.port=8502`

3. **Image Processing Issues**: If you encounter problems with the virtual try-on feature:
   - Ensure opencv-python and mediapipe are installed correctly
   - Try using a different image for the model photo
   - Check if the uploads folder exists and is writable

4. **Model Loading Issues**: If you see errors related to mediapipe or model loading, you may need to install specific versions compatible with your operating system.

## Contact

If you encounter any issues not covered in this guide, please report them by creating an issue in the project repository.

---

Happy shopping and virtual try-on!
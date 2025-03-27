# BharatFit - Virtual Try-On Fashion Website

BharatFit is an advanced e-commerce platform leveraging AI to transform online fashion shopping through intelligent virtual try-on technology and user-friendly error management.

## Features

- **Virtual Try-On Technology**: Upload your photo and see how clothes would look on you
- **Dual Implementation**: Available as both Flask and Streamlit applications
- **AI-Powered Image Processing**: Mediapipe pose estimation for accurate garment placement
- **User-Friendly Interface**: Professional design with responsive layouts
- **Background Removal**: Clean try-on results with automatic background removal
- **Product Catalog**: Browse men's and women's clothing collections
- **Search Functionality**: Find products by name or brand

## Technology Stack

- **Backend**: 
  - Flask web framework (main application)
  - Streamlit (alternative modern interface)
  
- **AI & Computer Vision**:
  - MediaPipe for pose detection
  - OpenCV for image processing
  - REMBG for background removal
  
- **Frontend**:
  - Responsive CSS with custom styling
  - Interactive user interfaces in both implementations

## Setup Guide

For complete setup instructions, please refer to the [SETUP_GUIDE.md](SETUP_GUIDE.md) file.

### Quick Start

1. Download and extract the ZIP file from the download link
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment and install dependencies: `pip install -r requirements.txt`
4. Run either:
   - Flask version: `python main.py`
   - Streamlit version: `streamlit run streamlit_app.py`
5. Access the application in your browser

## Project Structure

```
├── main.py                  # Flask application entry point
├── streamlit_app.py         # Streamlit application entry point
├── verify.py                # Upper body garment try-on functions
├── verify2.py               # Lower body garment try-on functions
├── static/                  # Static assets (CSS, JS, images)
├── templates/               # HTML templates for Flask app
├── .streamlit/              # Streamlit configuration
├── uploads/                 # Temporary folder for user uploads
└── requirements.txt         # Python dependencies
```

## Notes on Virtual Try-On Technology

The virtual try-on system works by:

1. Analyzing the user's photo to detect body landmarks
2. Processing the selected garment image to remove background
3. Calculating the positioning based on shoulder/hip positions
4. Overlaying the garment on the user's photo with proper sizing and placement

Error handling has been enhanced to provide clear feedback when issues occur with image processing.

## Design Principles

- **Professional appearance**: Clean, modern interface with balanced color scheme
- **Primary colors**: Pink (#F13AB1, #FF66C4) with orange accents (#F05524, #FD913C)
- **Responsive layout**: Adapts to different screen sizes
- **User-centric feedback**: Clear error messages and guidance

## License

This project is available for educational and personal use.

---

For questions or issues, please refer to the troubleshooting section in the setup guide.
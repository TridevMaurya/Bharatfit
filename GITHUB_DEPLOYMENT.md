# GitHub & Streamlit Deployment Guide

This guide explains how to deploy the Virtual Try-On E-Commerce application to GitHub and host it on Streamlit Cloud.

## Part 1: GitHub Deployment

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "virtual-tryon-ecommerce")
4. Add a description (optional)
5. Choose public or private visibility
6. Click "Create repository"

### 2. Prepare Your Local Files

1. Unzip the `virtual_tryon_website.zip` file to a folder on your computer
2. Open a terminal/command prompt and navigate to that folder

### 3. Initialize and Push to GitHub

```bash
# Initialize a local Git repository
git init

# Add all files to the repository
git add .

# Commit the files
git commit -m "Initial commit"

# Add your GitHub repository as the remote
git remote add origin https://github.com/YOUR_USERNAME/virtual-tryon-ecommerce.git

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username and `virtual-tryon-ecommerce` with your repository name.

## Part 2: Streamlit Cloud Deployment

Streamlit Cloud allows you to easily deploy Streamlit applications directly from GitHub repositories.

### 1. Sign Up for Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign up for an account
2. Sign in with your GitHub account or create a new Streamlit account

### 2. Deploy Your App

1. Once logged in, click on "New app"
2. Connect your GitHub account if you haven't already
3. Select your repository, branch, and the main file to run (`streamlit_app.py`)
4. Advanced settings:
   - Python version: 3.9 or higher
   - Packages: You can use the `requirements.txt` file in your repository
5. Click "Deploy"

### 3. App Configuration

1. Once deployed, your app will be assigned a URL like `https://your-app-name.streamlit.app`
2. You can customize the app's settings from the Streamlit Cloud dashboard
3. Configure environment variables if needed (though this app doesn't require any)

## Important Notes for Streamlit Deployment

### File Structure Requirements

Make sure your repository includes:
- `streamlit_app.py` - Main Streamlit application file
- `requirements.txt` - Lists all necessary Python packages
- `verify.py` and `verify2.py` - Essential for the virtual try-on functionality
- All required static files (images, CSS, etc.)

### Directory Management

Streamlit Cloud will automatically create required directories during deployment. 
The app has been designed to check and create any necessary directories at runtime.

### Image Processing Compatibility

The app uses OpenCV, MediaPipe, and other image processing libraries that have been
tested for compatibility with Streamlit Cloud's environment.

## Troubleshooting

### Common Deployment Issues

1. **Memory Limits**: If your app exceeds Streamlit Cloud's memory limits, you may need to optimize image processing operations
2. **Missing Dependencies**: Ensure all dependencies are listed in `requirements.txt`
3. **Path Issues**: Make sure all file paths use relative paths compatible with both local and deployed environments
4. **Processing Time**: Image processing can take longer in the deployed environment compared to local machines

### Resources and Support

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [GitHub Documentation](https://docs.github.com/en)

## Local Development After GitHub Deployment

If you want to continue development after deploying to GitHub:

1. Clone your repository locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/virtual-tryon-ecommerce.git
   ```

2. Make changes to your files

3. Commit and push changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

4. Streamlit Cloud will automatically detect changes to your main branch and update the deployed application

---

Happy deploying! Your virtual try-on e-commerce application is now ready for the world to see.
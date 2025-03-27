import cv2
import mediapipe as mp
import numpy as np

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def is_suitable_for_try_on(image):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if not results.pose_landmarks:
        return False, "No pose landmarks detected. Please ensure you are in a well-lit area and fully visible in the frame."

    # Extract shoulder landmarks
    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

    # Check if shoulders and hips are visible
    if not (left_shoulder.visibility > 0.8 and right_shoulder.visibility > 0.8):
        return False, "Shoulders not clearly visible. Please stand with a clear view of both shoulders and hips."

    # Calculate the distance between shoulders and hips
    shoulder_distance_pixels = np.sqrt(
        (left_shoulder.x - right_shoulder.x) ** 2 +
        (left_shoulder.y - right_shoulder.y) ** 2
    ) * image.shape[1]

    hip_distance_pixels = np.sqrt(
        (left_hip.x - right_hip.x) ** 2 +
        (left_hip.y - right_hip.y) ** 2
    ) * image.shape[1]

    upper_body_height = shoulder_distance_pixels + hip_distance_pixels
    total_image_height = image.shape[0]
    shoulder_hip_vector = np.array([right_shoulder.x - left_shoulder.x, right_shoulder.y - left_shoulder.y])
    hip_vector = np.array([right_hip.x - left_hip.x, right_hip.y - left_hip.y])

    # Calculate the cosine similarity to check alignment
    cosine_similarity = np.dot(shoulder_hip_vector, hip_vector) / (np.linalg.norm(shoulder_hip_vector) * np.linalg.norm(hip_vector))
    cosine_similarity = round(cosine_similarity, 3)

    cos_theta = 0.995
    r1 = 0.6
    if (upper_body_height / total_image_height < r1 and total_image_height < 600) or (cosine_similarity < cos_theta):
        return False, "Not suitable.....try again with proper pose and body visibility 😭❌"
        
    return True, "Image is suitable for virtual try-on. 😁✅"

def overlay_cloth_on_model(model_image_path, cloth_image_path, output_image_path):
    try:
        img = cv2.imread(model_image_path)
        if img is None:
            return None, "Failed to load model image"
            
        img_shirt = cv2.imread(cloth_image_path, cv2.IMREAD_UNCHANGED)
        if img_shirt is None:
            return None, "Failed to load clothes image"

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        if not results.pose_landmarks:
            return None, "No pose landmarks detected in the image"

        left_shoulder = (
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * img.shape[1]),
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * img.shape[0]),
        )
        right_shoulder = (
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * img.shape[1]),
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * img.shape[0]),
        )

        center_shoulder_x = int((left_shoulder[0] + right_shoulder[0]) / 2)
        upper_body_length = np.mean([left_shoulder[1], right_shoulder[1]])
        shirt_width = int(abs(right_shoulder[0] - left_shoulder[0]) * 1.9)
        shirt_height = int(upper_body_length * 1.2)
        
        offset_x_percent = 2
        offset_y_percent = 18
        offset_x = int(shirt_width * (offset_x_percent / 100))
        offset_y = int(upper_body_length * (offset_y_percent / 100))
        top_left_x = center_shoulder_x - int(shirt_width / 2)
        top_left_y = min(left_shoulder[1], right_shoulder[1]) - offset_y

        if shirt_width > 0 and shirt_height > 0:
            img_shirt = cv2.resize(img_shirt, (shirt_width, shirt_height))
            
            for y in range(shirt_height):
                for x in range(shirt_width):
                    if (top_left_y + y >= img.shape[0] or 
                        top_left_x + x >= img.shape[1] or 
                        y >= img_shirt.shape[0] or 
                        x >= img_shirt.shape[1]):
                        continue
                    
                    if len(img_shirt[y, x]) < 4:  # Check if alpha channel exists
                        continue
                        
                    alpha = img_shirt[y, x][3] / 255.0
                    if alpha == 0:  # Skip fully transparent pixels
                        continue
                        
                    img[top_left_y + y, top_left_x + x] = (
                        img_shirt[y, x][:3] * alpha + img[top_left_y + y, top_left_x + x] * (1 - alpha)
                    )

            cv2.imwrite(output_image_path, img)
            return output_image_path, "Cloth overlay successful."
        else:
            return None, "Invalid shirt dimensions calculated"
            
    except Exception as e:
        return None, f"Error in overlay process: {str(e)}"

def adjust_cloth_overlay(model_img, clothes_img, x_offset, y_offset, size_factor):
    """
    Adjust the clothing overlay with custom position and size
    
    Args:
        model_img: The model image as numpy array
        clothes_img: The clothes image as numpy array with alpha channel
        x_offset: Horizontal offset adjustment (positive is right, negative is left)
        y_offset: Vertical offset adjustment (positive is down, negative is up)
        size_factor: Scaling factor for the clothes size (1.0 is original size)
    
    Returns:
        success: Boolean indicating success or failure
        output_img: The resulting image as numpy array
    """
    try:
        img_rgb = cv2.cvtColor(model_img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        if not results.pose_landmarks:
            return False, model_img

        left_shoulder = (
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * model_img.shape[1]),
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * model_img.shape[0]),
        )
        right_shoulder = (
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * model_img.shape[1]),
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * model_img.shape[0]),
        )

        center_shoulder_x = int((left_shoulder[0] + right_shoulder[0]) / 2)
        upper_body_length = np.mean([left_shoulder[1], right_shoulder[1]])
        
        # Apply size adjustment
        shirt_width = int(abs(right_shoulder[0] - left_shoulder[0]) * 1.9 * size_factor)
        shirt_height = int(upper_body_length * 1.2 * size_factor)
        
        # Apply position adjustments (base offsets plus user adjustments)
        offset_x_percent = 2
        offset_y_percent = 18
        base_offset_x = int(shirt_width * (offset_x_percent / 100))
        base_offset_y = int(upper_body_length * (offset_y_percent / 100))
        
        # Calculate final position with user adjustments
        top_left_x = center_shoulder_x - int(shirt_width / 2) + x_offset
        top_left_y = min(left_shoulder[1], right_shoulder[1]) - base_offset_y + y_offset

        # Create a copy of the model image to avoid modifying the original
        output_img = model_img.copy()
        
        if shirt_width > 0 and shirt_height > 0:
            # Resize clothing image based on size factor
            resized_clothes = cv2.resize(clothes_img, (shirt_width, shirt_height))
            
            # Apply the overlay with alpha blending
            for y in range(shirt_height):
                for x in range(shirt_width):
                    if (top_left_y + y >= output_img.shape[0] or 
                        top_left_x + x >= output_img.shape[1] or 
                        y >= resized_clothes.shape[0] or 
                        x >= resized_clothes.shape[1]):
                        continue
                    
                    if len(resized_clothes[y, x]) < 4:  # Check if alpha channel exists
                        continue
                        
                    alpha = resized_clothes[y, x][3] / 255.0
                    if alpha == 0:  # Skip fully transparent pixels
                        continue
                        
                    output_img[top_left_y + y, top_left_x + x] = (
                        resized_clothes[y, x][:3] * alpha + output_img[top_left_y + y, top_left_x + x] * (1 - alpha)
                    )

            return True, output_img
        else:
            return False, model_img
            
    except Exception as e:
        print(f"Error in adjusting overlay: {str(e)}")
        return False, model_img

if __name__ == "__main__":
    model_image_path = 'path/to/model/image.jpg'
    cloth_image_path = 'path/to/cloth/image.png'
    output_image_path = 'path/to/output/image.jpg'
    output_path, message = overlay_cloth_on_model(model_image_path, cloth_image_path, output_image_path)
    print(message)

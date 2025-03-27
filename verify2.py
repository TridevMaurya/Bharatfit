import cv2
import mediapipe as mp
import numpy as np

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose

def is_lower_body_suitable(image):
    with mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.5) as pose:
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

    if not results.pose_landmarks:
        return False, "No pose landmarks detected. Please ensure you are in a well-lit area and fully visible in the frame."

    # Extract leg landmarks
    landmarks = results.pose_landmarks.landmark
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    
    # Check if legs are visible
    if not (left_knee.visibility > 0.8 and right_knee.visibility > 0.8 and
            left_ankle.visibility > 0.8 and right_ankle.visibility > 0.8):
        return False, "Legs not clearly visible. Please stand with a clear view of both knees and ankles."

    # Calculate the separation between legs
    leg_separation = abs(right_knee.x - left_knee.x) * image.shape[1]

    # Check if legs are not too wide apart
    threshold_leg_sep = image.shape[1] * 0.25
    if leg_separation > threshold_leg_sep:
        return False, "Legs are too far apart. Please stand with your legs closer together."

    # Check if legs are straight and not twisted
    if not (left_knee.y < left_ankle.y and right_knee.y < right_ankle.y and
            abs(left_ankle.x - right_ankle.x) < image.shape[1] * 0.1):
        return False, "Legs are not straight or may be twisted. Please stand with your legs straight and untwisted."

    return True, "Lower body pose is suitable for virtual try-on."

def overlay_lower_body_garment(model_image_path, garment_image_path, output_image_path):
    try:
        img = cv2.imread(model_image_path)
        if img is None:
            return None, "Failed to load model image"

        with mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.7) as pose:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose.process(img_rgb)
            
            if not results.pose_landmarks:
                return None, "No pose landmarks detected."

            # Load and check garment image
            garment_img = cv2.imread(garment_image_path, cv2.IMREAD_UNCHANGED)
            if garment_img is None:
                return None, "Failed to load garment image"

            landmarks = results.pose_landmarks.landmark
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

            # Calculate dimensions
            left_hip_x = int(left_hip.x * img.shape[1])
            left_hip_y = int(left_hip.y * img.shape[0])
            right_hip_x = int(right_hip.x * img.shape[1])
            right_hip_y = int(right_hip.y * img.shape[0])

            center_hip_x = (left_hip_x + right_hip_x) // 2
            lower_body_height = np.mean([left_hip_y, right_hip_y])

            garment_width = int(abs(right_hip_x - left_hip_x) * 4.5)
            garment_height = int((img.shape[0] - lower_body_height) * 0.95)

            if garment_width <= 0 or garment_height <= 0:
                return None, "Invalid garment dimensions calculated"

            # Resize garment
            garment_img = cv2.resize(garment_img, (garment_width, garment_height))

            # Calculate offsets
            offset_x = int(garment_width * 0.01)
            offset_y = int(lower_body_height * 0.15)

            # Overlay the garment
            for y in range(garment_height):
                for x in range(garment_width):
                    top_left_x = center_hip_x - garment_width // 2 + offset_x
                    top_left_y = int(lower_body_height) - offset_y

                    if (top_left_y + y >= img.shape[0] or 
                        top_left_x + x >= img.shape[1] or
                        y >= garment_img.shape[0] or 
                        x >= garment_img.shape[1]):
                        continue

                    if len(garment_img[y, x]) < 4:  # Check if alpha channel exists
                        continue

                    alpha = garment_img[y, x][3] / 255.0
                    if alpha == 0:  # Skip fully transparent pixels
                        continue

                    img[top_left_y + y, top_left_x + x] = (
                        alpha * garment_img[y, x][:3] + 
                        (1 - alpha) * img[top_left_y + y, top_left_x + x]
                    )

            cv2.imwrite(output_image_path, img)
            return output_image_path, "Lower body try-on successful."

    except Exception as e:
        return None, f"Error in overlay process: {str(e)}"

def adjust_lower_garment_overlay(model_img, garment_img, x_offset, y_offset, size_factor):
    """
    Adjust the lower body garment overlay with custom position and size
    
    Args:
        model_img: The model image as numpy array
        garment_img: The garment image as numpy array with alpha channel
        x_offset: Horizontal offset adjustment (positive is right, negative is left)
        y_offset: Vertical offset adjustment (positive is down, negative is up)
        size_factor: Scaling factor for the garment size (1.0 is original size)
    
    Returns:
        success: Boolean indicating success or failure
        output_img: The resulting image as numpy array
    """
    try:
        with mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.7) as pose:
            img_rgb = cv2.cvtColor(model_img, cv2.COLOR_BGR2RGB)
            results = pose.process(img_rgb)
            
            if not results.pose_landmarks:
                return False, model_img

            # Create a copy of the model image to avoid modifying the original
            output_img = model_img.copy()
            
            landmarks = results.pose_landmarks.landmark
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

            # Calculate dimensions
            left_hip_x = int(left_hip.x * output_img.shape[1])
            left_hip_y = int(left_hip.y * output_img.shape[0])
            right_hip_x = int(right_hip.x * output_img.shape[1])
            right_hip_y = int(right_hip.y * output_img.shape[0])

            center_hip_x = (left_hip_x + right_hip_x) // 2
            lower_body_height = np.mean([left_hip_y, right_hip_y])

            # Apply size adjustment
            garment_width = int(abs(right_hip_x - left_hip_x) * 4.5 * size_factor)
            garment_height = int((output_img.shape[0] - lower_body_height) * 0.95 * size_factor)

            if garment_width <= 0 or garment_height <= 0:
                return False, model_img

            # Resize garment
            resized_garment = cv2.resize(garment_img, (garment_width, garment_height))

            # Calculate base offsets
            base_offset_x = int(garment_width * 0.01)
            base_offset_y = int(lower_body_height * 0.15)

            # Apply user adjustments to position
            top_left_x = center_hip_x - garment_width // 2 + base_offset_x + x_offset
            top_left_y = int(lower_body_height) - base_offset_y + y_offset
            
            # Overlay the garment with adjusted position and size
            for y in range(garment_height):
                for x in range(garment_width):
                    if (top_left_y + y >= output_img.shape[0] or 
                        top_left_x + x >= output_img.shape[1] or
                        y >= resized_garment.shape[0] or 
                        x >= resized_garment.shape[1]):
                        continue

                    if len(resized_garment[y, x]) < 4:  # Check if alpha channel exists
                        continue

                    alpha = resized_garment[y, x][3] / 255.0
                    if alpha == 0:  # Skip fully transparent pixels
                        continue

                    output_img[top_left_y + y, top_left_x + x] = (
                        alpha * resized_garment[y, x][:3] + 
                        (1 - alpha) * output_img[top_left_y + y, top_left_x + x]
                    )

            return True, output_img

    except Exception as e:
        print(f"Error in adjusting lower garment overlay: {str(e)}")
        return False, model_img

if __name__ == "__main__":
    model_image_path = 'path/to/model/image.jpg'
    garment_image_path = 'path/to/cloth/image.png'
    output_image_path = 'path/to/output/image.jpg'
    output_path, message = overlay_lower_body_garment(model_image_path, garment_image_path, output_image_path)
    print(message)

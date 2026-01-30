"""
Sample video generator for testing the patient monitoring system.
This creates a simple test video with pose movements.
"""
import cv2
import numpy as np

def create_test_video(filename="test_patient.mp4", duration=10, fps=30):
    """
    Create a test video with a moving stick figure
    """
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    
    for frame_num in range(total_frames):
        # Create black background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Simulate different movements
        t = frame_num / total_frames
        
        if t < 0.3:
            # Normal standing
            draw_standing_person(frame, width//2, height//3)
            cv2.putText(frame, "Normal Activity", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        elif t < 0.5:
            # Rapid movement (walking quickly)
            x_pos = int(width//4 + (width//2) * ((t - 0.3) / 0.2))
            draw_standing_person(frame, x_pos, height//3)
            cv2.putText(frame, "Rapid Movement", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        elif t < 0.7:
            # Falling motion
            fall_progress = (t - 0.5) / 0.2
            y_pos = int(height//3 + (height//2) * fall_progress)
            draw_falling_person(frame, width//2, y_pos, fall_progress)
            cv2.putText(frame, "Fall Detected!", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        else:
            # On ground
            draw_person_on_ground(frame, width//2, int(height * 0.7))
            cv2.putText(frame, "Person Down", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_num}/{total_frames}", (10, height-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        out.write(frame)
    
    out.release()
    print(f"Test video created: {filename}")

def draw_standing_person(frame, x, y):
    """Draw a simple stick figure standing"""
    # Head
    cv2.circle(frame, (x, y), 20, (255, 255, 255), 2)
    
    # Body
    cv2.line(frame, (x, y+20), (x, y+100), (255, 255, 255), 2)
    
    # Arms
    cv2.line(frame, (x, y+40), (x-30, y+70), (255, 255, 255), 2)
    cv2.line(frame, (x, y+40), (x+30, y+70), (255, 255, 255), 2)
    
    # Legs
    cv2.line(frame, (x, y+100), (x-20, y+160), (255, 255, 255), 2)
    cv2.line(frame, (x, y+100), (x+20, y+160), (255, 255, 255), 2)

def draw_falling_person(frame, x, y, progress):
    """Draw a person in falling motion"""
    angle = progress * 90  # Rotate from 0 to 90 degrees
    
    # Simplified falling figure
    cv2.circle(frame, (x, y), 20, (255, 200, 200), 2)
    
    # Tilted body
    end_x = int(x + 80 * np.cos(np.radians(angle)))
    end_y = int(y + 80 * np.sin(np.radians(angle)))
    cv2.line(frame, (x, y), (end_x, end_y), (255, 200, 200), 2)

def draw_person_on_ground(frame, x, y):
    """Draw a person lying on the ground"""
    # Head
    cv2.circle(frame, (x-40, y), 20, (255, 150, 150), 2)
    
    # Body (horizontal)
    cv2.line(frame, (x-40, y), (x+40, y), (255, 150, 150), 2)
    
    # Arms
    cv2.line(frame, (x-20, y), (x-30, y+20), (255, 150, 150), 2)
    cv2.line(frame, (x+20, y), (x+30, y+20), (255, 150, 150), 2)
    
    # Legs
    cv2.line(frame, (x+40, y), (x+50, y+15), (255, 150, 150), 2)
    cv2.line(frame, (x+40, y), (x+50, y-15), (255, 150, 150), 2)

if __name__ == "__main__":
    create_test_video("uploads/test_patient.mp4", duration=15, fps=30)
    print("Test video generation complete!")
    print("You can now upload this video through the dashboard.")

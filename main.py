import cv2
from ultralytics import YOLO
import pygame
import time
import os
import tkinter as tk
from tkinter import messagebox

AUDIO_FILE = "audio.mp3"
CONFIDENCE_LEVEL = 0.5
COOLDOWN_SECONDS = 11
FRAME_SKIP = 3

def center_window(root, width=700, height=380):
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

def start_detector(root):
    if not os.path.exists(AUDIO_FILE):
        messagebox.showerror("Error", f"ERROR: '{AUDIO_FILE}' file not found!")
        return

    pygame.mixer.init()
    try:
        pygame.mixer.music.load(AUDIO_FILE)
    except Exception as e:
        messagebox.showerror("Audio Error", f"Audio Error: {e}")
        return

    model = YOLO('yolov8n.pt')

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

    last_alert_time = 0
    frame_count = 0
    phone_detected = False
    boxes_to_draw = []

    root.withdraw()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % FRAME_SKIP == 0:
            results = model(frame, stream=True, verbose=False, conf=CONFIDENCE_LEVEL, imgsz=640)

            phone_detected = False
            boxes_to_draw = []

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]

                    if class_name == 'cell phone':
                        phone_detected = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        boxes_to_draw.append((x1, y1, x2, y2))

        if phone_detected:
            for (x1, y1, x2, y2) in boxes_to_draw:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, "PHONE RAKHHHH NEECHE!", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            current_time = time.time()
            if current_time - last_alert_time > COOLDOWN_SECONDS:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play()
                last_alert_time = current_time

        cv2.imshow('No Phone Zone', frame)

        if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q')):
            break

    cap.release()
    cv2.destroyAllWindows()
    root.deiconify()

def on_close(root):
    root.destroy()

root = tk.Tk()
root.title("No Phone Zone")
root.configure(bg="white")
center_window(root, 700, 380)

tk.Label(root, text="NO PHONE ZONE",
         font=("Arial", 28, "bold"),
         fg="#e74c3c", bg="white").pack(pady=(50, 10))

tk.Label(root, text="by AMIT DAS",
         font=("Arial", 14, "bold"),
         fg="#00a8ff", bg="white").pack(pady=(0, 20))

tk.Label(root, text="Click START to begin monitoring",
         font=("Arial", 11), fg="#666", bg="white").pack()

tk.Label(root, text="Camera preview will open. Press Q to quit detection window.",
         font=("Arial", 10), fg="#777", bg="white").pack(pady=(4, 20))

tk.Button(root, text="START",
          font=("Arial", 12, "bold"),
          width=14, height=2,
          bg="#f1f2f6",
          command=lambda: start_detector(root)).pack()

root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
root.mainloop()

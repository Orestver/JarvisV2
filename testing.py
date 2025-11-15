import cv2
import threading
import time

# Глобальний флаг для контролю камери
camera_running = False
cap = None

def turn_the_camera():
    global camera_running, cap
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Камеру не знайдено!")

    camera_running = True
    print("Camera is running...")

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_camera()

    cap.release()
    cv2.destroyAllWindows()
    camera_running = False
    print("Camera stopped.")

def stop_camera():
    global camera_running
    camera_running = False

# Запуск камери в окремому потоці
camera_thread = threading.Thread(target=turn_the_camera)
camera_thread.start()

# Імітуємо роботу програми
time.sleep(10)  # наприклад, через 10 секунд хочемо зупинити камеру
stop_camera()
camera_thread.join()
print("Камера була зупинена з іншої функції")

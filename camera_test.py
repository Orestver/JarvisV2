import cv2
import google.generativeai as genai
import pyttsx3
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")



# Camera capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Камеру не знайдено!")

print("🎥 Камера запущена. Натисни 'q', щоб зробити знімок і отримати опис.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera", frame)

    # Натисни Q — зробити кадр
    if cv2.waitKey(1) & 0xFF == ord('q'):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
            cv2.imwrite(tmpfile.name, frame)

            # 📤 Надсилаємо зображення до Gemini
            response = model.generate_content([
                "Опиши людину на цьому фото: як вона виглядає, який одяг, настрій тощо.",
                {"mime_type": "image/jpeg", "data": open(tmpfile.name, "rb").read()}
            ])

            description = response.text
            print("\nAnalizyng...:", description)

            

cap.release()
cv2.destroyAllWindows()

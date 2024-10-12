import os
from cvzone.HandTrackingModule import HandDetector  # type: ignore
import cv2  # type: ignore
import pyttsx3  # For Text-to-Speech

# Constants
WEBCAM_WIDTH = 1020
WEBCAM_HEIGHT = 480
DESIRED_MODE_WIDTH = 400
DESIRED_MODE_HEIGHT = 590
MODE_IMAGE_X = 75
MODE_IMAGE_Y = 122
ICON_SIZE = (65, 65)  # Define the size for the icons

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to speak a given text
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# Function to initialize webcam
def initialize_webcam(width, height): 
    cap = cv2.VideoCapture(1)
    cap.set(3, width)
    cap.set(4, height)
    return cap

# Function to load images from a folder with resizing
def load_images(folder_path, resize_dim=(65, 65)):
    img_paths = os.listdir(folder_path)
    images = []
    for img_path in img_paths:
        img = cv2.imread(os.path.join(folder_path, img_path))
        if img is not None:
            img = cv2.resize(img, resize_dim, interpolation=cv2.INTER_AREA)
        images.append(img)
    return images

# Function to calculate the total bill
def calculate_bill(selectionList, confirmedSelections, cup_size):
    coffee_prices = {
        1: 288,  # Caffe Americano
        2: 299,  # Cold Coffee
        3: 239   # Cappuccino
    }
    sugar_prices = {
        1: 0,    # No Sugar
        2: 0,    # 1 Cube Sugar
        3: 0     # 2 Cube Sugar
    }
    cup_size_prices = {
        'Small': 0,
        'Medium': 10.0,
        'Large': 20.0
    }

    total = 0
    
    # Calculate total for coffee selection
    if confirmedSelections[0] and selectionList[0] != -1:
        total += coffee_prices[selectionList[0]]
    
    # Calculate total for sugar selection (sugar has no cost, but keeping it for completeness)
    if confirmedSelections[1] and selectionList[1] != -1:
        total += sugar_prices[selectionList[1]]
    
    # Add cost for cup size
    total += cup_size_prices[cup_size]
    
    return total

# Function to display the bill on the interface
def display_bill(imgBackground, selectionList, cup_size, total):
    bill_text = f"Your Order:\n"
    if selectionList[0] != -1:
        bill_text += f"Coffee: {['Caffe Americano', 'Cold Coffee', 'Cappuccino'][selectionList[0] - 1]} - {288 if selectionList[0] == 1 else 299 if selectionList[0] == 2 else 239} Rs\n"
    if selectionList[1] != -1:
        bill_text += f"Sugar: {['No Sugar', '1 Cube Sugar', '2 Cube Sugar'][selectionList[1] - 1]}\n"
    if selectionList[2] != -1:
        bill_text += f"Cup Size: {cup_size}\n"
    bill_text += f"Total: {total} Rs"

    # Set initial Y position for bill display
    y0, dy = 155, 52  # Adjust y0 for vertical position and dy for line spacing

    for i, line in enumerate(bill_text.split('\n')):
        # Adjust font scale and position for better display
        cv2.putText(imgBackground, line, (50, y0 + i * dy), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

def main():
    cap = initialize_webcam(WEBCAM_WIDTH, WEBCAM_HEIGHT)
    imgBackground = cv2.imread("Interface/Background.png")
    if imgBackground is None:
        print("Failed to load background image")
        return

    listImgModes = load_images("Interface/Modes", (DESIRED_MODE_WIDTH, DESIRED_MODE_HEIGHT))
    listImgIcons = load_images("Interface/Icons")
    listImgIcons = [cv2.resize(icon, ICON_SIZE, interpolation=cv2.INTER_AREA) for icon in listImgIcons]

    modeType = 0
    selection = -1
    counter = 0
    selectionSpeed = 10
    detector = HandDetector(maxHands=1, detectionCon=0.5)
    modePositions = [(136, 290), (136, 397), (136, 505)]
    counterPause = 0
    selectionList = [-1, -1, -1]
    confirmedSelections = [False, False, False]  # Track confirmed selections

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image")
            break

        hands, img = detector.findHands(img, draw=True, flipType=True)
        img = cv2.resize(img, (570, 440))
        imgBackground[145:145 + 440, 739:739 + 570] = img
        imgBackground[MODE_IMAGE_Y:MODE_IMAGE_Y + DESIRED_MODE_HEIGHT, MODE_IMAGE_X:MODE_IMAGE_X + DESIRED_MODE_WIDTH] = listImgModes[modeType]

        if hands and counterPause == 0 and modeType < 3:
            hand1 = hands[0]
            fingers1 = detector.fingersUp(hand1)
            print(fingers1)

            if fingers1 == [0, 1, 0, 0, 0]:
                if selection != 1:
                    counter = 1
                    selection = 1

            elif fingers1 == [0, 1, 1, 0, 0]:
                if selection != 2:
                    counter = 1
                    selection = 2

            elif fingers1 == [0, 1, 1, 1, 0]:
                if selection != 3:
                    counter = 1
                    selection = 3

            else:
                selection = -1
                counter = 0

            if counter > 0:
                counter += 1
                print(counter)
                cv2.ellipse(imgBackground, modePositions[selection - 1], (38, 38), 0, 0,   
                            counter * selectionSpeed, (255, 255, 255), 5)

            if counter * selectionSpeed > 360:
                selectionList[modeType] = selection
                confirmedSelections[modeType] = True  # Mark as confirmed
                
                # Text-to-Speech for each mode
                if modeType == 0:  # Coffee selection
                    coffee_name = ['Caffe Americano', 'Cold Coffee', 'Cappuccino'][selection - 1]
                    speak_text(f"You selected {coffee_name} as your coffee")

                elif modeType == 1:  # Sugar selection
                    sugar_level = ['No Sugar', '1 Cube Sugar', '2 Cube Sugar'][selection - 1]
                    speak_text(f"You selected {sugar_level}")

                elif modeType == 2:  # Cup size selection
                    cup_size = ['Small', 'Medium', 'Large'][selection - 1]
                    speak_text(f"You selected {cup_size} cup")

                modeType += 1
                counter = 0
                selection = -1
                counterPause = 1

        if counterPause > 0:
            counterPause += 1
            if counterPause > 60:
                counterPause = 0

        if modeType == 3 and counterPause == 0:
            print("Entering reorder mode")
            imgBackground[MODE_IMAGE_Y:MODE_IMAGE_Y + DESIRED_MODE_HEIGHT, MODE_IMAGE_X:MODE_IMAGE_X + DESIRED_MODE_WIDTH] = listImgModes[3]

            if hands:
                hand1 = hands[0]
                fingers1 = detector.fingersUp(hand1)
                print("Reorder gesture:", fingers1)

                if fingers1 == [1, 0, 0, 0, 0]:
                    print("Restarting order")
                    modeType = 0
                    selectionList = [-1, -1, -1]
                    confirmedSelections = [False, False, False]  # Reset confirmed selections
                    imgBackground[620:620 + 65, 750:750 + 65] = (0, 0, 0)
                    imgBackground[620:620 + 65, 1000:1000 + 65] = (0, 0, 0)
                    imgBackground[620:620 + 65, 1250:1250 + 65] = (0, 0, 0)

                elif fingers1 == [0, 0, 0, 0, 0]:
                    print("Proceeding to final mode")
                    modeType += 1

            counterPause = 1

        if selectionList[0] != -1:
            imgBackground[620:620 + 65, 750:750 + 65] = listImgIcons[selectionList[0] - 1]
        if selectionList[1] != -1:
            imgBackground[620:620 + 65, 1000:1000 + 65] = listImgIcons[2 + selectionList[1]]
        if selectionList[2] != -1:
            imgBackground[620:620 + 65, 1250:1250 + 65] = listImgIcons[5 + selectionList[2]]

        if modeType == 4:  # Final mode for bill
            cup_size = ['Small', 'Medium', 'Large'][selectionList[2] - 1]  # Get cup size from selection
            total = calculate_bill(selectionList, confirmedSelections, cup_size)
            display_bill(imgBackground, selectionList, cup_size, total)

        cv2.imshow("Background", imgBackground)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

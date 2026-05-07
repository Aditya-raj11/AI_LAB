

import pyautogui
import time
from pynput import mouse

# -------- USER CONFIG --------
cycles = 5
scroll_amount = -10000        # very large negative scroll
delay_a_to_b_sec = 10         # seconds (A -> B)
delay_b_to_c_min = 40         # minutes (B -> C)
delay_between_cycles_sec = 10 # seconds between cycles
delay_before_a_click = 3      # seconds before clicking A
# --------------------------------

positions = []
print("Middle-click (scroll button) to save positions A, B, and C")

# Save original mouse position
original_position = pyautogui.position()

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.middle:
        positions.append((x, y))
        print(f"Position {len(positions)} saved at ({x}, {y})")
        if len(positions) == 3:
            return False  # stop listener

# Capture A, B, C
with mouse.Listener(on_click=on_click) as listener:
    listener.join()

pos_a, pos_b, pos_c = positions

print("\nAll positions saved.")
print("Automation will start in 3 seconds...")
time.sleep(3)

# -------- AUTOMATION LOOP --------
for i in range(cycles):
    print(f"\n--- Cycle {i+1}/{cycles} ---")

    # 1. Move to A
    pyautogui.moveTo(pos_a)
    print("Moved to A")

    # 2. Wait 3 seconds
    time.sleep(delay_before_a_click)

    # 3. Left click A
    pyautogui.click(button='left')
    print("Left clicked A")

    # 4. Wait A -> B
    time.sleep(delay_a_to_b_sec)

    # 5. Click B
    pyautogui.click(pos_b)
    print("Clicked B")

    # 6. Scroll down
    pyautogui.scroll(scroll_amount)
    print("Scrolled down")

    # 7. Wait B -> C
    time.sleep(delay_b_to_c_min * 60)

    # 8. Click C
    pyautogui.click(pos_c)
    print("Clicked C")

    # 9. Wait between cycles
    if i < cycles - 1:
        print(f"Waiting {delay_between_cycles_sec} seconds before next cycle...")
        time.sleep(delay_between_cycles_sec)

# Restore mouse position
pyautogui.moveTo(original_position)
print("\nDone. Mouse position restored.")

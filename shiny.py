import pyautogui
import keyboard
import time
import numpy as np
import sys
import os
from scipy.stats import binom
from scipy.optimize import brentq
import winsound

from webhook import DiscordBot
from timer import Timer
from screenshotter import Screenshotter

EMULATOR = "DeSmuME"
RESET_COMBINATION = "d+f+c+v"
ODDS = 1/8192

def detect_shiny(screenshot, target):
    """
    Detect if a shiny Pokemon appears based on the pink hex color.
    Using updated color values based on actual sample data.
    """
    # Convert the target pink color to RGB
    match (target):
        case "celebi":
            target_color = np.array([255, 123, 123])
        case "darkrai":
            target_color = np.array([57, 24, 123])
        case "shaymin":
            target_color = np.array([99, 222, 189])
        case "arceus":
            target_color = np.array([255, 247, 140])
        case "groudon":
            target_color = np.array([198, 206, 49])
        case "rayquaza":
            target_color = np.array([115, 123, 115])
        
        case default:
            print(f"make a target color")
            return False

    # Add more targets here if you want to hunt them.
    
    # Convert screenshot to numpy array
    img_array = np.array(screenshot)
    
    # Create a mask for pixels close to the target color
    color_distances = np.sqrt(np.sum((img_array - target_color) ** 2, axis=2))
    
    # Count pixels with distance less than threshold
    close_pixels = np.sum(color_distances < 5)  # Adjust this threshold based on testing
    
    # Debug information
    # print(f"Target color: {target_color}")
    # print(f"Minimum distance: {np.min(color_distances)}")
    # print(f"Close pixels found: {close_pixels}")
    
    # Adjust this logic based on your findings
    return close_pixels > 1000  # Adjust this threshold based on testing

def encounter(pokemon):
    match (pokemon):
        case "celebi":
            for i in range(15):
                keyboard.press('x')
                time.sleep(0.02)  
                keyboard.release('x')
                time.sleep(0.02)
            time.sleep(0.1)

        case "darkrai" | "shaymin" | "groudon" | "rayquaza":
            for i in range(12):
                keyboard.press('x')
                time.sleep(0.15)  
                keyboard.release('x')
                time.sleep(0.15)
            time.sleep(1.2)
        
        case "arceus":
            for i in range(6):
                keyboard.press('x')
                time.sleep(0.16)
                keyboard.release('x')
                time.sleep(0.16)
            time.sleep(1)

            # move up for encounter
            keyboard.press('up')
            time.sleep(0.05)
            keyboard.release('up')
            
            # wait for walking
            time.sleep(2.5)

            # last message boxqq
            keyboard.press('x')
            time.sleep(0.16)
            keyboard.release('x')

            # wait for encounter
            time.sleep(2)

def get_count(target) -> int:
    try:
        with open('count.txt', 'r') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    parts = line.strip().split(':')
                    if len(parts) == 2 and parts[0] == target:
                        return int(parts[1])
    except FileNotFoundError:
        create_file()
    
    new_target(target)
    return 0

def update_count(target, count):
    lines = []
    updated = False

    # Read existing lines
    try:
        with open('count.txt', 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        pass

    # Update or add the target count
    for i, line in enumerate(lines):
        parts = line.strip().split(':')
        if len(parts) == 2 and parts[0] == target:
            lines[i] = f"{target}:{count}\n"
            updated = True
            break
    
    # If not found, append new target
    if not updated:
        lines.append(f"{target}:{count}\n")

    # Write back to file
    with open('count.txt', 'w') as file:
        file.writelines(lines)

def new_target(target):
    with open('count.txt', 'a') as file:
        file.write(f"{target}:0\n")

def create_file():
    open('count.txt', 'a')

def reset():
    keyboard.press(RESET_COMBINATION)
    time.sleep(0.1)
    keyboard.release(RESET_COMBINATION)

def print_info(count, encounter_rate_hour):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("No shiny found, soft resetting...")

    psp = calc_psp(count)
    certainty = 0.75 if psp < 75 else 0.95
    time = time_until_certain(count, encounter_rate_hour, certainty)

    print(f"Reset: {count}\n")
    print(f"Encounter rate: {int(encounter_rate_hour)}/h")
    print(f"Probability: {psp:.2f}%")
    print(f"Time until {int(certainty*100)}%: {time}")

def calc_rate(time):
    """
    Takes seconds, returns per hour
    """

    return 60 / time * 60

def calc_psp(count) -> float:
    return binom.sf(0, count, ODDS) * 100 # *100 so its 70.xx% instead of 0.70xx%

def time_until_certain(count, encounter_rate_hour, certainty) -> str:
    def psp_func(x):
        return binom.sf(0, int(x), ODDS) * 100 - (certainty * 100)
    
    encounter_number = int(brentq(psp_func, count, 1000000))
    target = encounter_number - count

    # early(ish) exit
    if (count >= encounter_number):
        return "Reached!"
    
    # take target and take the encounter rate hour and reverse it to per encounter time, then target * per encounter time
    per_encounter = 60 / (encounter_rate_hour / 60)
    time_minutes = (target * per_encounter) / 60

    return f"{int(time_minutes)} minutes ({encounter_number})" if time_minutes < 60 else f"{time_minutes/60:.1f} hours ({encounter_number})"

def main():
    create_file()

    ss = Screenshotter()
    timer = Timer()
    dBot = DiscordBot()

    target = sys.argv[1]
    count = get_count(target) if len(sys.argv) < 3 else int(sys.argv[2])

    # Find Emulator window
    ss._get_window_rect(EMULATOR)
    
    while not keyboard.is_pressed('q'):
        # start timer
        timer._start()

        # Press X to get to the Celebi encounter
        encounter(target)
        count += 1 # persists through file
        
        # update count
        update_count(target, count)

        # Now take the screenshot after the encounter starts
        screenshot = ss._poke_screenshot()
        
        # Check for shiny
        if detect_shiny(screenshot, target):
            args = [ss._emu_screenshot(target, count), count, target, timer._calc_total(count)]
            dBot._send_message(args)
            break
        
        # If no shiny, soft reset
        reset()

        # end timer
        timer._end()
        # add time to total time
        
        # print info for user
        print_info(count, calc_rate(timer._diff()))


if __name__ == "__main__":
    # Give user time to switch to the game window
    print("Starting in 2 seconds... Switch to Emulator window!")
    time.sleep(2)

    main()
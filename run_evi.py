import asyncio
import os
from dotenv import load_dotenv 
from helper_functions import print_ascii_art
from hume import HumeVoiceClient, MicrophoneInterface, VoiceSocket, VoiceConfig


# Import pygame module and initialize
import pygame
pygame.init()

# Initialize Game Variables
text_font = pygame.font.SysFont("Comic Sans", 30)
text_col = "Black"
def draw_text(text, x, y):
    img = text_font.render(text,True, text_col)
    screen.blit(img, (x, y))

title = 1
running = True
screen = pygame.display.set_mode((1280, 720))


# Hume EVI API Init
load_dotenv()
message_counter = 0


 
def on_open():
    print_ascii_art("Say hello to WellBot, Well-Co's assistant powered by Hume AI's Empathic Voice Interface!")

# Handler for incoming messages
def on_message(message):
    global message_counter
    # Increment the message counter for each received message
    message_counter += 1
    msg_type = message["type"]

    # Start the message box with the common header
    message_box = (
        f"\n{'='*60}\n"
        f"Message {message_counter}\n"
        f"{'-'*60}\n"
    )


    # Add role and content for user and assistant messages
    if msg_type in {"user_message", "assistant_message"}:
        
        role = message["message"]["role"]
        content = message["message"]["content"]
        message_box += (
            f"role: {role}\n"
            f"content: {content}\n"
            f"type: {msg_type}\n"
        )


        emotion1 = ["","",""]
        index = 0
        # Add top emotions if available
        if "models" in message and "prosody" in message["models"]:
            scores = message["models"]["prosody"]["scores"]
            num = 3
            # Get the top N emotions based on the scores
            top_emotions = get_top_n_emotions(prosody_inferences=scores, number=num)

            message_box += f"{'-'*60}\nTop {num} Emotions:\n"
            for emotion, score in top_emotions:
                message_box += f"{emotion}: {score:.4f}\n"
                emotion1[index] = emotion
                index += 1
                

        if role == "user":
            title_screen = pygame.image.load("FirstTime.png")
            title_screen = pygame.transform.scale(title_screen, (1280,720))
            screen.blit(title_screen, (0,0))
            pygame.display.update()

        elif role == "assistant":
            title_screen = pygame.image.load("SecondTime.png")
            title_screen = pygame.transform.scale(title_screen, (1280,720))
            screen.blit(title_screen, (0,0))


            draw_text(emotion1[0], 340, 220)
            draw_text(emotion1[1], 685, 220)
            draw_text(emotion1[2], 1035, 220)


            total_length = len(content)
            i = 0
            j = 51
            current_y = 370
            # Max length per line is 51
            while total_length > 52:
                draw_text(content[i:j], 320, current_y)
                total_length -= 51
                i += 51
                j += 51
                current_y += 45
            draw_text(content[i:], 320, current_y)

            pygame.display.update()




    # Add all key-value pairs for other message types, excluding audio_output
    elif msg_type != "audio_output":
        for key, value in message.items():
            message_box += f"{key}: {value}\n"
    else:
        message_box += (
            f"type: {msg_type}\n"
        )

    message_box += f"{'='*60}\n"
    # Print the constructed message box
    print(message_box)

# Function to get the top N emotions based on their scores
def get_top_n_emotions(prosody_inferences, number):
 
    sorted_inferences = sorted(prosody_inferences.items(), key=lambda item: item[1], reverse=True)
    return sorted_inferences[:number]

# Handler for when an error occurs
def on_error(error):
    # Print the error message
    print(f"Error: {error}")

# Handler for when the connection is closed
def on_close():
    # Print a closing message using ASCII art
    print_ascii_art("Thank you for using WellBot, take care!!!")


async def user_input_handler(socket: VoiceSocket):
    global running
    while True:
        # Asynchronously get user input to prevent blocking other operations
        user_input = await asyncio.to_thread(input, "Type a message to send or 'Q' to quit: ")
        if user_input.strip().upper() == "Q":
            # If user wants to quit, close the connection
            print("Closing the connection...")
            await socket.close()
            running = False
            break
        else:
            # Send the user input as text to the socket
            await socket.send_text_input(user_input)



# Asynchronous main function to set up and run the client
async def main() -> None:
    try:
    
        # Retrieve the Hume API key from the environment variables
        HUME_API_KEY = os.getenv("HUME_API_KEY")
        HUME_SECRET_KEY = os.getenv("HUME_SECRET_KEY")

        # Connect and authenticate with Hume
        client = HumeVoiceClient(HUME_API_KEY, HUME_SECRET_KEY)

        # Start streaming EVI over your device's microphone and speakers
        async with client.connect_with_handlers(
            #insert your own configID for the bot you want"
            config_id="5eeee856-2fc9-4407-a1ec-95ac3ddcde7d",
            on_open=on_open,                # Handler for when the connection is opened
            on_message=on_message,          # Handler for when a message is received
            on_error=on_error,              # Handler for when an error occurs
            on_close=on_close,              # Handler for when the connection is closed
            enable_audio=True,              # Flag to enable audio playback (True by default)
        ) as socket:
            # Start the microphone interface in the background; add "device=NUMBER" to specify device
            microphone_task = asyncio.create_task(MicrophoneInterface.start(socket))

            # Start the user input handler
            user_input_task = asyncio.create_task(user_input_handler(socket))

            # The gather function is used to run both async tasks simultaneously
            await asyncio.gather(microphone_task, user_input_task)
    except Exception as e:
        # Catch and print any exceptions that occur
        print(f"Exception occurred: {e}")


# Game Logic
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Title Scene
    if title == 1:

        # Load Title Screen
        title_screen = pygame.image.load("title.png")
        title_screen = pygame.transform.scale(title_screen, (1280,720))
        screen.blit(title_screen, (0,0))
        pygame.display.update()
        
        # If Return Key is Pressed, Switch Scene
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Load FirstTime Screen
            title_screen = pygame.image.load("FirstTime.png")
            title_screen = pygame.transform.scale(title_screen, (1280,720))
            screen.blit(title_screen, (0,0))
            pygame.display.update()
            title += 1
    
    if title == 2:
    
        asyncio.run(main())


pygame.quit()

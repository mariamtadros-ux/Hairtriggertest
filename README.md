Hair Trigger

An interactive 2D game created with Python and Pygame, where players use different tools to interact with a character and influence their mood.

About the Project

Hair Trigger is a small interactive game developed as part of a university coding project. The idea behind the game was to create a character that responds to the player's actions, making the experience interactive and humorous.

Players can cut the character's hair using scissors, draw on their face using a marker, and wash away the markings. As the player interacts with the character, its facial expressions, dialogue and frustration level change in response.

The purpose of this project was to learn the fundamentals of Python programming and apply them to creating an interactive game. It was developed through a combination of tutorials, independent coding, experimentation and debugging.

Technologies Used

Python 3 – Main programming language.

Pygame – Used to create the game window, graphics, animations, input handling and game loop.

Python standard libraries:

math – Mathematical calculations and geometry.

random – Randomised hair generation and game behaviour.

sys – Application exit handling.

Dependencies: Pygame is required to run the game. It is listed in requirements.txt.

Features

Introductory screen: Introduces the game and explains the controls.

Scissors tool: Allows players to cut the character's hair by dragging across it.

Falling hair animation: Cut sections of hair fall away from the character.

Marker tool: Allows players to draw on the character's face.

Face interaction zones: Different areas, including the eyes and mouth, can trigger different reactions.

Wash tool: Removes marker drawings from the character's face.

Character reactions: Facial expressions and dialogue change depending on player interactions.

Frustration system: Tracks the character's reactions and anger throughout gameplay.

Game interface: Displays information such as remaining hair and the character's frustration.

Ending screen: Concludes the game and displays a summary of the player's actions.

Restart functionality: Allows players to restart the game.

How to Play

Launch the game and read the instructions on the introductory screen.

Select a tool using the keyboard:

Press 1 to select scissors.

Press 2 to select the marker.

Use the mouse to interact with the character:

Drag the scissors across the hair to cut it.

Drag the marker across the face to draw.

Press W to wash the marker off the character's face.

Watch how the character's expressions, dialogue and frustration respond to your actions.

The game ends when the hair remaining reaches the ending threshold.

Press R to restart or ESC to quit.

Installation and Setup

Requirements

Before running the game, make sure you have:

Python 3 installed.

Pygame installed.

A code editor or terminal to run the Python file.

1. Download the project

Clone the repository or download the project files from GitHub.

2. Open the project folder

Open your terminal and navigate to the folder containing the game files.

3. Create a virtual environment

python3 -m venv venv

4. Activate the virtual environment

For macOS and Linux:

source venv/bin/activate

For Windows:

venv\Scripts\activate

5. Install the dependencies

python3 -m pip install -r requirements.txt

Running the Game

Once the dependencies have been installed, run:

python3 hair_trigger.py

The game window should open, allowing you to start playing.

Project Status

Completed prototype.

The game includes its introductory screen, interactive tools, character reactions, frustration system and ending screen. The project was developed as a learning exercise to apply Python programming concepts through an interactive game.

Possible Future Improvements

Some areas that could be explored in future development include:

Adding sound effects and background music.

Introducing additional interactive tools.

Expanding the range of character expressions and dialogue.

Adding more levels or different gameplay scenarios.

Further improving the visual design and animations.

Acknowledgements and Sources

The development process involved learning from online Python and Pygame tutorials, experimenting with code, and independently adapting and writing features for the game.

Learning resources consulted:

YouTube tutorial 1

YouTube tutorial 2

YouTube tutorial 3 – Pygame tutorial series

YouTube tutorial 4

Friends also tested the game and provided feedback during development. Their feedback contributed to the inclusion of an introductory screen and an ending to give the gameplay a clearer structure.

AI assistance was used to help understand error messages and troubleshoot bugs. The game features and code were developed through tutorials, adaptation and independent coding.

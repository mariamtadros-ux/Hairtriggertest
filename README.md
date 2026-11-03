Hair Trigger

An interactive 2D game created using Python and Pygame, where players use different tools to interact with a character and influence their mood.

About the Project

Hair Trigger is an interactive game developed as part of a university coding project. The idea behind the game was to create a character that responds to the player's actions, making the experience interactive and humorous.

Players can cut the character's hair using scissors, draw on their face using a marker, and wash away the markings. As the player interacts with the character, its facial expressions, dialogue and frustration level change in response.

The purpose of this project was to learn the fundamentals of Python programming and apply them to creating an interactive game. As someone who began the project without previous Python or game development experience, I developed my understanding through tutorials, adapting existing examples, independent coding, experimentation and debugging.

Technologies Used

Python 3: Main programming language.

Pygame CE: Used to create the game window, graphics, animations, input handling and game loop.

Python standard libraries:

math – Mathematical calculations and geometry.

random – Randomised hair generation and game behaviour.

sys – Application exit handling.

Dependencies: Pygame CE is required to run the game and is listed in requirements.txt.

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

Ending screen: Concludes the game when the remaining hair reaches a set threshold.

Restart functionality: Allows players to restart the game.

How to Play

Launch the game and read the instructions on the introductory screen.

Controls

Press 1 to select scissors.

Press 2 to select the marker.

Drag the scissors across the hair to cut it.

Drag the marker across the face to draw.

Press W to wash the marker off the character's face.

Press R to restart the game.

Press ESC to quit.

Watch how the character's expressions, dialogue and frustration respond to your actions.

The game ends when the remaining hair reaches the ending threshold.

Installation and Setup

Requirements

Before running the game, make sure you have:

Python 3 installed.

Pygame CE installed.

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

6. Run the game

python3 hair_trigger.py

The game window should open, allowing you to start playing.

Project Status

Completed prototype.

The game includes an introductory screen, interactive tools, character reactions, a frustration system and an ending screen. The project was developed as a learning exercise to apply Python programming concepts through an interactive game.

Possible Future Improvements

Some areas that could be explored in future development include:

Adding sound effects and background music.

Introducing additional interactive tools.

Expanding the range of character expressions and dialogue.

Adding more levels or different gameplay scenarios.

Further improving the visual design and animations.

Acknowledgements and Sources

I developed Hair Trigger through a combination of independent coding, experimentation and learning from external Python and Pygame resources.

The following tutorials were consulted during the development process:

YouTube tutorial 1

YouTube tutorial 2

YouTube tutorial 3 – Pygame tutorial series

YouTube tutorial 4

I used these resources to develop my understanding of Python and Pygame techniques. I adapted relevant examples and applied the concepts to my own game. I also independently wrote and modified code to implement the game's specific features. Any directly adapted code should be acknowledged in the relevant code comments.

Friends tested the game and provided feedback during development. Their feedback contributed to the inclusion of an introductory screen and an ending, giving the gameplay a clearer structure.

I also used AI assistance to help interpret error messages and troubleshoot bugs. I did not use AI to generate the game's features; the development and implementation involved my own coding, tutorial-based learning and adaptation.

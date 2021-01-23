This project is a script written in Python to drive a RaspberryPI (connected to a robotic arm and an Arduino UNO chip) in order to observe, analyze and play tic-tac-toe game with a human.

- The board state is read via a camera and processed / analyzed using OpenCV.
- The algorithm used to find the best move is minimax.
- The move is fed into the Arduino chip via a serial communication cable, which is programmed to move the servo-motors of the arm to pick the O/X piece and place it in the desired location.

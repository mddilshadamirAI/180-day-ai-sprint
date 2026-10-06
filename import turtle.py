import turtle
import math
import random
import colorsys

# -----------------------------
# SCREEN
# -----------------------------
screen = turtle.Screen()
screen.setup(width=900, height=700)
screen.bgcolor("black")
screen.title("Mouse Following Snake 🐍")
screen.tracer(0)

# -----------------------------
# SNAKE SETTINGS
# -----------------------------
snake = []

SEGMENT_SIZE = 18
SPEED = 5
FOLLOW_DISTANCE = 18

# Snake head
head = turtle.Turtle()
head.shape("circle")
head.shapesize(1.0)
head.penup()
head.color("cyan")
snake.append(head)

# Create initial body
for i in range(8):
    segment = turtle.Turtle()
    segment.shape("circle")
    segment.shapesize(0.75)
    segment.penup()
    segment.color("cyan")
    segment.goto(-((i + 1) * FOLLOW_DISTANCE), 0)
    snake.append(segment)

# -----------------------------
# MOUSE POSITION
# -----------------------------
mouse_x = 0
mouse_y = 0

def mouse_move(x, y):
    global mouse_x, mouse_y
    mouse_x = x
    mouse_y = y

screen.cv.bind("<Motion>", lambda event: mouse_move(
    event.x - screen.window_width() / 2,
    screen.window_height() / 2 - event.y
))

# -----------------------------
# FOOD
# -----------------------------
food = turtle.Turtle()
food.shape("circle")
food.shapesize(0.8)
food.penup()
food.color("red")

def new_food():
    x = random.randint(-420, 420)
    y = random.randint(-320, 320)
    food.goto(x, y)

new_food()

# -----------------------------
# COLOR CHANGING
# -----------------------------
hue = 0

def change_colors():
    global hue

    hue += 0.003
    if hue >= 1:
        hue = 0

    for i, segment in enumerate(snake):
        h = (hue + i * 0.015) % 1
        r, g, b = colorsys.hsv_to_rgb(h, 1, 1)

        # Convert RGB 0-1 to 0-255
        color = (
            int(r * 255),
            int(g * 255),
            int(b * 255)
        )

        segment.color(color)

# -----------------------------
# MOVE SNAKE
# -----------------------------
def move_snake():

    # Calculate direction toward mouse
    dx = mouse_x - head.xcor()
    dy = mouse_y - head.ycor()

    distance = math.sqrt(dx * dx + dy * dy)

    if distance > 2:

        # Calculate angle
        angle = math.degrees(math.atan2(dy, dx))

        head.setheading(angle)

        # Move toward mouse
        head.forward(min(SPEED, distance))

    # Body follows previous segment
    for i in range(len(snake) - 1, 0, -1):

        previous = snake[i - 1]

        dx = previous.xcor() - snake[i].xcor()
        dy = previous.ycor() - snake[i].ycor()

        distance = math.sqrt(dx * dx + dy * dy)

        if distance > FOLLOW_DISTANCE:

            angle = math.degrees(math.atan2(dy, dx))

            snake[i].setheading(angle)

            snake[i].goto(
                previous.xcor() - math.cos(math.radians(angle)) * FOLLOW_DISTANCE,
                previous.ycor() - math.sin(math.radians(angle)) * FOLLOW_DISTANCE
            )

    # -----------------------------
    # EAT FOOD
    # -----------------------------
    food_distance = head.distance(food)

    if food_distance < 22:

        new_food()

        # Add new segment
        segment = turtle.Turtle()
        segment.shape("circle")
        segment.shapesize(0.75)
        segment.penup()

        last = snake[-1]

        segment.goto(last.xcor(), last.ycor())
        snake.append(segment)

    # Keep snake inside screen
    if head.xcor() > 440:
        head.setx(440)

    if head.xcor() < -440:
        head.setx(-440)

    if head.ycor() > 340:
        head.sety(340)

    if head.ycor() < -340:
        head.sety(-340)

    change_colors()

    screen.update()

    screen.ontimer(move_snake, 16)


# -----------------------------
# START GAME
# -----------------------------
move_snake()

screen.mainloop()
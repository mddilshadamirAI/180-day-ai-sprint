import turtle
import math
import random
import colorsys


# =========================================================
# NEON SNAKE 🐍
# Python Turtle Edition
# =========================================================

WIDTH = 1000
HEIGHT = 700

SPEED = 5
SEGMENT_DISTANCE = 17


# =========================================================
# SCREEN
# =========================================================

screen = turtle.Screen()

# IMPORTANT:
# colorsys gives RGB values between 0 and 1
screen.colormode(1.0)

screen.setup(WIDTH, HEIGHT)
screen.bgcolor("black")
screen.title("NEON SNAKE 🐍")
screen.tracer(0)


# =========================================================
# GAME VARIABLES
# =========================================================

snake = []

mouse_x = 0
mouse_y = 0

score = 0
hue = 0.0
food_hue = 0.0


# =========================================================
# SCORE DISPLAY
# =========================================================

score_writer = turtle.Turtle()
score_writer.hideturtle()
score_writer.penup()
score_writer.color("white")
score_writer.goto(-460, 305)

def update_score():

    score_writer.clear()

    score_writer.write(
        f"SCORE: {score}",
        font=("Arial", 20, "bold")
    )


update_score()


# =========================================================
# MOUSE TRACKING
# =========================================================

def mouse_move(event):

    global mouse_x, mouse_y

    mouse_x = event.x - WIDTH / 2
    mouse_y = HEIGHT / 2 - event.y


canvas = screen.getcanvas()

canvas.bind(
    "<Motion>",
    mouse_move
)


# =========================================================
# CREATE SNAKE SEGMENT
# =========================================================

def create_segment(x, y, size=0.8):

    segment = turtle.Turtle()

    segment.shape("circle")
    segment.shapesize(size)
    segment.penup()
    segment.goto(x, y)

    snake.append(segment)

    return segment


# =========================================================
# CREATE HEAD
# =========================================================

head = create_segment(
    0,
    0,
    1.1
)


# =========================================================
# CREATE INITIAL BODY
# =========================================================

for i in range(1, 11):

    create_segment(
        -i * SEGMENT_DISTANCE,
        0,
        0.8
    )


# =========================================================
# FOOD
# =========================================================

food = turtle.Turtle()

food.shape("circle")
food.shapesize(0.8)
food.penup()


# Extra larger transparent-looking glow
food_glow = turtle.Turtle()

food_glow.shape("circle")
food_glow.shapesize(1.4)
food_glow.penup()


# =========================================================
# FOOD POSITION
# =========================================================

def spawn_food():

    x = random.randint(-430, 430)
    y = random.randint(-280, 280)

    food.goto(x, y)
    food_glow.goto(x, y)


spawn_food()


# =========================================================
# RAINBOW SNAKE
# =========================================================

def update_colors():

    global hue

    hue += 0.004

    if hue >= 1.0:
        hue = 0.0

    for i, segment in enumerate(snake):

        current_hue = (
            hue + i * 0.018
        ) % 1.0

        r, g, b = colorsys.hsv_to_rgb(
            current_hue,
            1.0,
            1.0
        )

        # IMPORTANT:
        # Keep RGB between 0 and 1
        segment.color(
            (r, g, b)
        )


# =========================================================
# NEON FOOD EFFECT
# =========================================================

def update_food():

    global food_hue

    food_hue += 0.01

    if food_hue >= 1.0:
        food_hue = 0.0

    r, g, b = colorsys.hsv_to_rgb(
        food_hue,
        1.0,
        1.0
    )

    # RGB must stay between 0 and 1
    food.color(
        (r, g, b)
    )

    food_glow.color(
        (r, g, b)
    )

    # Pulsating glow
    pulse = (
        1.3
        + math.sin(food_hue * math.pi * 10) * 0.15
    )

    food_glow.shapesize(
        pulse
    )


# =========================================================
# EAT FOOD
# =========================================================

def eat_food():

    global score

    score += 10

    update_score()

    spawn_food()

    # Grow by 2 segments
    for _ in range(2):

        last = snake[-1]

        create_segment(
            last.xcor(),
            last.ycor(),
            0.8
        )


# =========================================================
# MOVE SNAKE
# =========================================================

def move_snake():

    # -----------------------------------------------------
    # FIND DIRECTION TO MOUSE
    # -----------------------------------------------------

    dx = (
        mouse_x
        - head.xcor()
    )

    dy = (
        mouse_y
        - head.ycor()
    )

    distance = math.sqrt(
        dx * dx + dy * dy
    )


    # -----------------------------------------------------
    # MOVE HEAD
    # -----------------------------------------------------

    if distance > 3:

        angle = math.degrees(
            math.atan2(
                dy,
                dx
            )
        )

        head.setheading(
            angle
        )

        movement = min(
            SPEED,
            distance
        )

        head.forward(
            movement
        )


    # -----------------------------------------------------
    # BODY FOLLOWS HEAD
    # -----------------------------------------------------

    for i in range(
        len(snake) - 1,
        0,
        -1
    ):

        current = snake[i]
        previous = snake[i - 1]

        dx = (
            previous.xcor()
            - current.xcor()
        )

        dy = (
            previous.ycor()
            - current.ycor()
        )

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        if distance > SEGMENT_DISTANCE:

            angle = math.atan2(
                dy,
                dx
            )

            new_x = (
                previous.xcor()
                - math.cos(angle)
                * SEGMENT_DISTANCE
            )

            new_y = (
                previous.ycor()
                - math.sin(angle)
                * SEGMENT_DISTANCE
            )

            current.goto(
                new_x,
                new_y
            )


    # -----------------------------------------------------
    # FOOD COLLISION
    # -----------------------------------------------------

    if head.distance(food) < 25:

        eat_food()


    # -----------------------------------------------------
    # SCREEN BOUNDARIES
    # -----------------------------------------------------

    if head.xcor() > 470:

        head.setx(470)

    if head.xcor() < -470:

        head.setx(-470)

    if head.ycor() > 320:

        head.sety(320)

    if head.ycor() < -320:

        head.sety(-320)


    # -----------------------------------------------------
    # ANIMATIONS
    # -----------------------------------------------------

    update_colors()

    update_food()

    screen.update()


    # -----------------------------------------------------
    # RUN AGAIN
    # -----------------------------------------------------

    screen.ontimer(
        move_snake,
        16
    )


# =========================================================
# START GAME
# =========================================================

move_snake()

screen.mainloop()
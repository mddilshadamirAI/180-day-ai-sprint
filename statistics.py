import argparse
import sys
import statistics

def greet(name: str):
    """Prints a friendly greeting."""
    print(f"Hello, {name}!")

def calculate_average(numbers: list[float]):
    """Calculates and prints the mean of a provided list of numbers."""
    if not numbers:
        print("No numbers provided to calculate.")
        return
    avg = statistics.mean(numbers)
    print(f"The average is: {avg}")

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        description="A utility script to greet users and calculate averages."
    )
    
    # Define arguments
    parser.add_argument("name", help="The name of the person to greet")
    parser.add_argument(
        "--numbers", 
        nargs="+", 
        type=float, 
        help="A list of numbers to calculate the mean (space-separated)"
    )

    args = parser.parse_args()

    # Execute logic
    greet(args.name)
    
    if args.numbers:
        calculate_average(args.numbers)

if __name__ == "__main__":
    main()

"""
BMI Calculator - Beginner Tier
--------------------------------
Command-line tool that:
  - Prompts the user for weight (kg) and height (m)
  - Validates the input (must be numeric and positive)
  - Calculates BMI = weight / height^2
  - Classifies the result into a standard health category
  - Lets the user run multiple calculations without restarting the program
"""


def get_positive_float(prompt: str) -> float:
    """
    Repeatedly asks the user for input until they provide a valid
    positive number. Handles both non-numeric input and negative/zero
    values with a clear error message.
    """
    while True:
        raw_value = input(prompt).strip()
        try:
            value = float(raw_value)
        except ValueError:
            print(
                f"  ❌ '{raw_value}' is not a valid number. Please enter something like 65 or 65.5.\n"
            )
            continue

        if value <= 0:
            print("  ❌ Value must be greater than 0. Please try again.\n")
            continue

        return value


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculates BMI using the standard formula: weight / height^2."""
    return weight_kg / (height_m**2)


def classify_bmi(bmi: float) -> str:
    """Maps a BMI value to its standard WHO health category."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def main():
    print("=" * 45)
    print("            BMI CALCULATOR")
    print("=" * 45)

    while True:
        print("\nEnter your details below:")
        weight = get_positive_float("  Weight (kg): ")
        height = get_positive_float("  Height (m):  ")

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)

        print("\n" + "-" * 45)
        print(f"  Your BMI is: {bmi:.2f}")
        print(f"  Category:    {category}")
        print("-" * 45)

        again = input("\nCalculate another BMI? (y/n): ").strip().lower()
        if again != "y":
            print("\nThanks for using the BMI Calculator. Goodbye!")
            break


if __name__ == "__main__":
    main()

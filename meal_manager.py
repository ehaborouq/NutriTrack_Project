import datetime

class MealManager:
    """
    Manages user meals, calorie calculations, and nutritional advice.
    """
    def __init__(self, daily_limit=2000):
        # Setting the core properties for the manager
        self.daily_limit = daily_limit
        self.meals_list = []

    def add_meal(self, name, calories, category):
        """
        Creates a meal dictionary and appends it to the list.
        Returns the newly created meal.
        """
        new_meal = {
            "name": name,
            "calories": int(calories),
            "category": category,
            "time": datetime.datetime.now().strftime("%H:%M")
        }
        self.meals_list.append(new_meal)
        return new_meal

    def calculate_remaining_calories(self):
        """
        Computes the remaining calories based on the daily limit.
        Ensures the result is never below zero.
        """
        total_consumed = sum(meal['calories'] for meal in self.meals_list)
        remaining = self.daily_limit - total_consumed
        return max(0, remaining)

    def get_nutrition_advice(self):
        """
        Provides smart feedback based on the user's total calorie intake.
        """
        if not self.meals_list:
            return "Start your day by logging a healthy meal!"

        total_consumed = sum(meal['calories'] for meal in self.meals_list)
        remaining = self.daily_limit - total_consumed

        if total_consumed > self.daily_limit:
            return f"Daily limit exceeded by {abs(remaining)} kcal! Try to walk it off."

        elif total_consumed == self.daily_limit:
            return "Goal reached perfectly! No more calories needed for today."

        elif total_consumed > (self.daily_limit * 0.85):
            return "You're almost there! Your next meal should be very light."

        elif total_consumed > (self.daily_limit * 0.5):
            return "On track! You've consumed more than half of your daily goal."

        else:
            return "You're doing great! Keep tracking your progress."
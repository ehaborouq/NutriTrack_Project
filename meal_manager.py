import datetime

class MealManager:
    """
    Core logic for managing meal logs, calculating metrics,
    and generating personality-based coaching feedback.
    """

    def __init__(self, daily_limit=2000):
        # Initialize the meal manager with a default or user-defined calorie goal
        self.daily_limit = daily_limit
        self.meals_list = []

    def add_meal(self, name, calories, category):
        """
        Creates a new meal entry and stores it in the session history.
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
        Calculates how many calories are left before reaching the daily goal.
        Returns 0 if the limit is exceeded.
        """
        total_consumed = sum(meal['calories'] for meal in self.meals_list)
        remaining = self.daily_limit - total_consumed
        return max(0, remaining)

    def get_nutrition_advice(self, personality="Motivator"):
        """
        Generates dynamic advice based on the user's consumption progress
        and the selected coach's personality.
        """
        total_consumed = sum(meal['calories'] for meal in self.meals_list)

        # Calculate progress ratio and over-limit amount
        ratio = total_consumed / self.daily_limit if self.daily_limit > 0 else 0
        exceeded_by = total_consumed - self.daily_limit

        # Coach Personality Dictionary: Centralized messages for easy updates
        coaches = {
            "Motivator": {
                "start": "Great start! Every healthy choice counts today. 🌟",
                "half": "You're halfway there! Keep that momentum going! 💪",
                "near": "Almost at the finish line! Keep your next meal light. ✨",
                "limit": "Goal reached! You're a champion today! 🏆",
                "exceeded": f"Over the limit by {exceeded_by} kcal, but don't give up! Let's move a bit more. 🚶‍♂️"
            },
            "Strict": {
                "start": "System active. Awaiting your first entry. Stay disciplined. ⚖️",
                "half": "50% reached. No room for unplanned snacks. 🚫",
                "near": "Warning: 85% capacity reached. Choose wisely. ⚠️",
                "limit": "Capacity full. Protocol: Stop eating. 🛑",
                "exceeded": f"Limit violated! {exceeded_by} kcal excess detected. Rectify now. 📉"
            },
            "Comedian": {
                "start": "The fridge is watching you... make it proud! 🥗",
                "half": "Halfway done! Your stomach is currently 50% happy. 🍔",
                "near": "Aborted mission! You're almost full, don't be a hero. 🦸‍♂️",
                "limit": "Game over! You've officially defeated hunger today. 🎮",
                "exceeded": f"Oops! {exceeded_by} extra calories! They're winning! Run for your life! 🏃‍♂️"
            }
        }

        # Fallback to 'Motivator' if selected personality is not found
        coach = coaches.get(personality, coaches["Motivator"])

        # Logical routing for advice triggers
        if not self.meals_list:
            return coach["start"]
        if total_consumed > self.daily_limit:
            return coach["exceeded"]
        if total_consumed == self.daily_limit:
            return coach["limit"]
        if ratio > 0.85:
            return coach["near"]
        if ratio > 0.5:
            return coach["half"]

        return coach["start"]
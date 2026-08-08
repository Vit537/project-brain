"""
Time and Date Service
Provides time, date, and calendar information (local, no internet needed)
"""
from datetime import datetime, timedelta
import calendar
from colorama import Fore, Style, init

init(autoreset=True)


class TimeService:
    """Handles all time and date queries"""
    
    @staticmethod
    def get_current_time(language='en'):
        """Get current time"""
        now = datetime.now()
        if language == 'es':
            time_str = now.strftime("%H:%M:%S")
            return f"La hora actual es {time_str}", f"Current time: {time_str}"
        else:
            time_str = now.strftime("%I:%M %p")
            return f"The current time is {time_str}", f"Current time: {time_str}"
    
    @staticmethod
    def get_current_date(language='en'):
        """Get current date"""
        now = datetime.now()
        if language == 'es':
            date_str = now.strftime("%d de %B de %Y")
            day_name = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][now.weekday()]
            return f"Hoy es {day_name}, {date_str}", f"Today is {day_name}, {date_str}"
        else:
            date_str = now.strftime("%B %d, %Y")
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][now.weekday()]
            return f"Today is {day_name}, {date_str}", f"Today is {day_name}, {date_str}"
    
    @staticmethod
    def get_day_of_week(language='en'):
        """Get day of week"""
        now = datetime.now()
        if language == 'es':
            days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            day = days[now.weekday()]
            return f"Hoy es {day}", f"Today is {day}"
        else:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day = days[now.weekday()]
            return f"Today is {day}", f"Today is {day}"
    
    @staticmethod
    def calculate_time_until(target_time, language='en'):
        """Calculate time until a specific time"""
        now = datetime.now()
        try:
            target = datetime.strptime(target_time, "%H:%M")
            target = target.replace(year=now.year, month=now.month, day=now.day)
            
            if target < now:
                target = target + timedelta(days=1)
            
            diff = target - now
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            
            if language == 'es':
                return f"Faltan {hours} horas y {minutes} minutos", f"{hours}h {minutes}m remaining"
            else:
                return f"There are {hours} hours and {minutes} minutes remaining", f"{hours}h {minutes}m remaining"
        except:
            if language == 'es':
                return "No entiendo ese formato de hora", "Invalid time format"
            else:
                return "I don't understand that time format", "Invalid time format"

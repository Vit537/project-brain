"""
System Information Service
Provides system stats (CPU, RAM, disk, battery) - local, no internet
"""
import psutil
from colorama import Fore, Style, init

init(autoreset=True)


class SystemService:
    """Handles system information queries"""
    
    @staticmethod
    def get_cpu_usage(language='en'):
        """Get CPU usage percentage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        if language == 'es':
            return f"El uso de CPU es {cpu_percent}%", f"CPU: {cpu_percent}%"
        else:
            return f"CPU usage is {cpu_percent}%", f"CPU: {cpu_percent}%"
    
    @staticmethod
    def get_memory_usage(language='en'):
        """Get RAM usage"""
        memory = psutil.virtual_memory()
        used_gb = memory.used / (1024**3)
        total_gb = memory.total / (1024**3)
        percent = memory.percent
        
        if language == 'es':
            return f"Memoria en uso: {used_gb:.1f} GB de {total_gb:.1f} GB, {percent}%", f"RAM: {percent}%"
        else:
            return f"Memory in use: {used_gb:.1f} GB of {total_gb:.1f} GB, {percent}%", f"RAM: {percent}%"
    
    @staticmethod
    def get_disk_usage(language='en'):
        """Get disk space usage"""
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024**3)
        total_gb = disk.total / (1024**3)
        percent = disk.percent
        
        if language == 'es':
            return f"Espacio en disco: {used_gb:.1f} GB de {total_gb:.1f} GB, {percent}% usado", f"Disk: {percent}%"
        else:
            return f"Disk space: {used_gb:.1f} GB of {total_gb:.1f} GB, {percent}% used", f"Disk: {percent}%"
    
    @staticmethod
    def get_battery_status(language='en'):
        """Get battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = battery.power_plugged
                status = "connected" if plugged else "unplugged"
                if language == 'es':
                    status = "conectada" if plugged else "desconectada"
                    return f"Batería: {percent}%, {status}", f"Battery: {percent}%"
                else:
                    return f"Battery: {percent}%, {status}", f"Battery: {percent}%"
            else:
                if language == 'es':
                    return "No se detectó batería", "No battery detected"
                else:
                    return "No battery detected", "No battery detected"
        except:
            if language == 'es':
                return "No puedo acceder a la información de batería", "Battery info unavailable"
            else:
                return "I can't access battery information", "Battery info unavailable"
    
    @staticmethod
    def get_system_summary(language='en'):
        """Get complete system summary"""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if language == 'es':
            return f"Sistema: CPU {cpu}%, RAM {memory.percent}%, Disco {disk.percent}%", \
                   f"CPU {cpu}% | RAM {memory.percent}% | Disk {disk.percent}%"
        else:
            return f"System status: CPU {cpu}%, RAM {memory.percent}%, Disk {disk.percent}%", \
                   f"CPU {cpu}% | RAM {memory.percent}% | Disk {disk.percent}%"

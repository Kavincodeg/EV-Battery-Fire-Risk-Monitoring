class BatteryState:
    def __init__(self, temperature, voltage, current, capacity):
        self.temperature = temperature
        self.voltage = voltage
        self.current = current
        self.capacity = capacity

    def soc(self):
        """
        Simulated State of Charge (SOC)
        """
        return min(max((self.voltage - 3.0) / (4.2 - 3.0) * 100, 0), 100)

    def power(self):
        """
        Instantaneous power consumption
        """
        return self.voltage * self.current

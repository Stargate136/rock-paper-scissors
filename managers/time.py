from datetime import datetime, timedelta


class TimeManager:
    """
    TimeManager class
    """

    @staticmethod
    def now():
        """Returns the current time"""
        return datetime.utcnow()

    @staticmethod
    def timestamp_after_delay(delay_seconds):
        """
        Returns the timestamp after a delay
        :param delay_seconds: number of seconds
        :return: timestamp"""
        current_time = datetime.utcnow()
        delayed_time = current_time + timedelta(seconds=delay_seconds)
        return delayed_time

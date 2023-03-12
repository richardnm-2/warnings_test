from abc import ABC
from pydantic import BaseModel
import warnings


class AlertWarning(UserWarning):
    def __init__(self, message, alert_type='warning', user_profile='admin'):
        self.alert = Alert(
            message=message, alert_type=alert_type, user_profile=user_profile)
        self.message = self.alert

        warnings.warn(self)

    def __str__(self):
        return repr(self.message)


class AlertA(AlertWarning):
    message = 'Alert A'

    def __init__(self, message=message, alert_type='warning'):
        super().__init__(message, alert_type)


class AlertB(AlertWarning):
    message = 'Alert B'

    def __init__(self, message=message, alert_type='warning'):
        super().__init__(message, alert_type)


class AlertC(AlertWarning):
    message = 'Alert C'

    def __init__(self, message=message, alert_type='warning'):
        super().__init__(message, alert_type)


class Alert(BaseModel):
    message: str
    alert_type: str
    user_profile: str

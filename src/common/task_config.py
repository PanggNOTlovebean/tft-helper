from qfluentwidgets import QConfig, ConfigItem, BoolValidator

class TaskConfig(QConfig):
    enabled = ConfigItem("tasks", "enabled", True, BoolValidator())

from cx_Freeze import setup, Executable

setup(
    name = "ReplayTime",
    version = "0.1",
    description = "ReplayTime",
    executables = [Executable("ReplayTime.py")],
)
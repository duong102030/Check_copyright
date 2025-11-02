from setuptools import setup

setup(
    name="check-copyright-nkd",
    version="1.0.0",
    py_modules=["check_copyright"],
    entry_points={
        "console_scripts": [
            "check_copyright = check_copyright:main",
        ],
    },
)

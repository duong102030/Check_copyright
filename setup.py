from setuptools import setup

setup(
    name="check-copyright-nkd",
    version="1.0.0",
    py_modules=["check_copyright"],
    entry_points={
        "console_scripts": [
            "check-copyright-nkd = check_copyright:main",
        ],
    },
)

from setuptools import setup, find_packages

setup(
    name="blinkui",
    version="0.1.0",
    description="Build mobile apps in pure Python",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "blink=cli.main:main",
        ],
    },
    python_requires=">=3.10",
)
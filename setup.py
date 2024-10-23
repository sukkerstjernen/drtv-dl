from setuptools import setup, find_packages

setup(
    name="drtv-dl",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "ffmpeg-python",
    ],
    entry_points={
        "console_scripts": [
            "drtv-dl=drtv_dl.cli:parse_args",
        ],
    },
)
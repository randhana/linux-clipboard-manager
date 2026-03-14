import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="linux-copycache",
    version="1.0.2",
    author="Pulathisi Kariyawasam",
    author_email="pulathisi.kariyawasam@gmail.com",
    description="A lightweight, fast, and reliable clipboard manager for Linux (Ubuntu) mimicking Win+V.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/randhana/linux-clipboard-manager",
    project_urls={
        "Bug Tracker": "https://github.com/randhana/linux-clipboard-manager/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.4.0",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "linux-clipboard=linux_clipboard_manager.clipboard_gui:main",
        ],
    },
)

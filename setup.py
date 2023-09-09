import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webxpressd",
    version="0.2.1",
    author="tantanGH",
    author_email="tantanGH@github",
    license='MIT',
    description="Preprocessing Service for WebXpression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tantanGH/webxpressd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'webxpressd=webxpressd.webxpressd:main'
        ]
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=["selenium", "beautifulsoup4"],
)

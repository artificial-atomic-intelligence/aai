import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aai",
    version="0.0.1",
    description="AtomicAI API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/artificial-atomic-intelligence/aai",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
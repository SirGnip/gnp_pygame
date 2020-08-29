import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gnp_pygame",
    version="1.0.0",
    description="Personal PyGame utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SirGnip/gnp_pygame",

    # Code is in "src/", an un-importable directory (at least not easily or accidentally)
    # Helps reduce confusion around whether code from repo or site-packages is being used.
    # https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
    # https://hynek.me/articles/testing-packaging/
    # https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ],

    python_requires='>=2.7',
    install_requires=[
        "pygame>=1.9",
        "pytest>=4.6",
    ],
)

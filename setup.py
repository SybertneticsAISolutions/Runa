from setuptools import setup, find_packages

setup(
    name="runa",
    version="0.1.0",
    description="Runa Programming Language - A natural language-like programming language",
    author="Sybertnetics",
    author_email="info@sybertnetics.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ply>=3.11",  # For lexer/parser
        "click>=8.0.0",  # For CLI
        "astor>=0.8.1",  # For Python AST manipulation
    ],
    entry_points={
        "console_scripts": [
            "runa=runa.cli:main",
        ],
    },
    python_requires=">=3.12",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13"
    ],
)
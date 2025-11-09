"""
Setup script for Pet Insurance SHAP Analysis package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pet-insurance-shap",
    version="1.0.0",
    author="AI Team",
    author_email="ai-team@your-company.com",
    description="SHAP-based explainability for pet insurance claim decisions using GPT models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/pet-insurance-shap",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "coverage>=7.2.0",
        ],
        "gpu": [
            "torch-cuda>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pet-claims-demo=examples.demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.json", "*.md"],
    },
)

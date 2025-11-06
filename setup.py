from setuptools import setup, find_packages

setup(
    name="openmetadata-polaris-connector",
    version="2.0.0",
    description="Apache Polaris connector for OpenMetadata",
    author="Mustapha Fonsau",
    author_email="mfonsau@talentys.eu",
    packages=find_packages(include=["polaris_connector", "polaris_connector.*"]),
    install_requires=[
        "openmetadata-ingestion>=1.4.0",
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ],
    entry_points={
        "openmetadata.ingestion.source.plugins": [
            "polaris = polaris_connector.polaris_source:PolarisSource",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
)
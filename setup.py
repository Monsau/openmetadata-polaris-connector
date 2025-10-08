from setuptools import setup, find_packages

setup(
    name="openmetadata-polaris-connector",
    version="1.0.0",
    description="Apache Polaris connector for OpenMetadata",
    author="Mustapha Fonsau",
    author_email="mfonsau@talentys.eu",
    packages=find_packages(where="connectors"),
    package_dir={"": "connectors"},
    install_requires=[
        "openmetadata-ingestion>=1.4.0",
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ],
    entry_points={
        "openmetadata_sources": [
            "polaris = connectors.polaris.polaris_connector:PolarisSource",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
from setuptools import setup, find_packages

setup(
    name="analyse_incidents_reseau",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.25.0",
        "pyyaml>=6.0",
        "regex>=2025.9.1",
        "openpyxl>=3.1.0",
        "xlsxwriter>=3.1.0",
        "reportlab>=4.0.0",
        "elasticsearch>=8.10.0",
        "python-dateutil>=2.9.0"
    ],
    entry_points={
        "console_scripts": [
            "run_weekly_report=run_weekly_report:main",
        ]
    },
    python_requires=">=3.9",
)

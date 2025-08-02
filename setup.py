# pip install -e .

from setuptools import setup, find_packages

setup(
    name='rupdpybrowser',
    version='0.1',
    description='To Control Chromium Browser Session',
    author='Rahul Upadhyay',
    author_email='rahulrupadhyay91@gmail.com',
    packages=find_packages(),
    install_requires=[
        'playwright>=1.43.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)

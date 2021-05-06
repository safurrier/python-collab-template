from setuptools import setup, find_packages
from os import path

absolute_path = path.abspath(path.dirname(__file__))


def get_file_data(filename):
    with open(path.join(absolute_path, filename), encoding='utf-8') as f:
        file_data = f.read()
    return file_data


setup(
    name='src',
    version='0.0.1',
    description='Example Python Collaboration Template',
    long_description=get_file_data('README.md'),
    long_description_content_type='text/markdown',
    author='Example Author',
    author_email='N/A',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    packages=find_packages(),
    install_requires=get_file_data('requirements.prod').split('\n'),
    python_requires='>=3.5'
)

from setuptools import setup

setup(
    name='restcli',
    version='1.0.0',
    description='Smart REST API Testing Tool - Zero Dependencies',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Logan Smith',
    author_email='contact@metaphy.io',
    url='https://github.com/DonkRonk17/RestCLI',
    py_modules=['restcli'],
    entry_points={
        'console_scripts': [
            'restcli=restcli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires='>=3.6',
)

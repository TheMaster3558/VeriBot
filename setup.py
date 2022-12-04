import re
from setuptools import setup


with open('veribot/__init__.py', 'r') as f:
    version = re.search(r'^__version__:\sFinal\[str]\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)


with open('README.rst', 'r') as f:
    readme = f.read()


packages = [
    'veribot'
]


requirements = [
    'aiosqlite',
    'discord.py>=2.0',
    'jishaku'
]


setup(
    name='veribot',
    author='The Master',
    license='MIT',
    url='https://github.com/TheMaster3558/veribot',
    project_urls={
        'GitHub': 'https://github.com/TheMaster3558/veribot'
    },
    version=version,
    packages=packages,
    description='VeriBot is a bot that can be used for verification.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    install_requires=requirements,
    python_requires='>=3.7.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
      ]
)

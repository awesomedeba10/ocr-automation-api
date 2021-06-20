from setuptools import setup

def _get_requirements():
    try:
        with open('requirements.txt') as f:
            requirements = f.read().splitlines()
        return requirements
    except FileNotFoundError as e:
        print(e)

setup(
    name='ocr-automation-api',
    version='1.0',
    packages=[],
    url='https://github.com/awesomedeba10/ocr-automation-api.git',
    license='BSD-2',
    install_requires=_get_requirements(),
    author='awesomedeba10',
    author_email='officialdeba10@gmail.com',
    description='API Support for OCR Form Automation'
)
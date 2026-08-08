from setuptools import find_packages,setup
from typing import List
HYPHEN_E_DOT='-e .'
def get_requirements(file_path:str)->list[str]:
    requirements = []
    with open(file_path, 'r') as file:
        for line in file:
            requirement = line.strip()
            if requirement:
                requirements.append(requirement)

    if HYPHEN_E_DOT in requirements:
        requirements.remove(HYPHEN_E_DOT)
    return requirements

setup(
    name='Network security',
    version='0.0.1',
    author='Muhammad Bilal Sheikh',
    author_email='smbilal1409@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)


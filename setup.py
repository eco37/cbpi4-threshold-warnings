from setuptools import setup

setup(name='cbpi4-threshold-warnings',
      version='0.0.1',
      description='CraftBeerPi Plugin to set thresholds that with add a warning when triggered',
      author='Max Sidenstjärna',
      author_email='',
      url='https://github.com/eco37/cpbi4-threshold-warnings',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-warnings': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-threshold-warnings'],
     )

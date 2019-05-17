from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='roconfiguration',
      version='1.0.3',
      description='Implementation of key-value pair based configuration for Python applications.',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent'
      ],
      url='https://github.com/RobertoPrevato/roconfiguration',
      author='RobertoPrevato',
      author_email='roberto.prevato@gmail.com',
      keywords='configuration core yaml ini json environment',
      license='MIT',
      packages=['roconfiguration'],
      install_requires=['PyYAML'],
      include_package_data=True,
      zip_safe=False)

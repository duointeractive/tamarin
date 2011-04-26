from setuptools import setup
import tamarin

DESCRIPTION = "A Django app for monitoring AWS usage in Django's admin."

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

version_str = '%d.%d' % (tamarin.VERSION[0], tamarin.VERSION[1])

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

setup(
    name='tamarin',
    version=version_str,
    packages=[
        'tamarin',
    ],
    author='Gregory Taylor',
    author_email='gtaylor@duointeractive.com',
    url='https://github.com/duointeractive/tamarin/',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    install_requires=['boto', 'django'],
)

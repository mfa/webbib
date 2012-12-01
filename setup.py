from setuptools import setup, find_packages

setup(
    name='webbib',
    version='0.1',
    url='http://github.com/mfa/webbib/',
    license='BSD',
    author='Andreas Madsack',
    author_email='Andreas.Madsack@ims.uni-stuttgart.de',
    description='Bibliography website for bibtex data using Flask and pybtex',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts': ['webbib-cli = webbib.main:cli_main'],
    },
    install_requires=[
        'Flask>=0.7',
        'babel',
        'Flask-Babel',
        'lxml',
        'simplejson',
        'pybtex'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

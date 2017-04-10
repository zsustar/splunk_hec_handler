from setuptools import setup

setup(
    name = 'splunk_http_handler',
    version = '1.0.0',
    license = 'MIT License',
    description = 'A Python logging handler that sends your logs to Splunk over HTTP event collector',
    long_description = open('README.md').read(),
    author = 'MEV, LLC',
    author_email = 'vlad.shevtsov@mev.com',
    url = 'https://github.com/vlad-shevtsov-mev/splunk_http_handler',
    packages = ['splunk_http_handler'],
    install_requires = ['requests >= 2.6.0, < 3.0.0', 'ast', 'mock'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Logging'
    ]
)

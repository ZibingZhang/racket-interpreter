import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='racketinterpreter',
    packages=['racketinterpreter'],
    version='0.1.0',
    author='Zibing Zhang',
    author_email='',
    description='An interpreter for Racket',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ZibingZhang/racket-interpreter',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Interpreters',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7',
)

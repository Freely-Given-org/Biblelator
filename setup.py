"""
A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""
VERSION = '0.0.1'
LAST_MODIFIED_DATE = '2020-04-11' # by RJH — when setup.py was modified below

INCLUDE_DATA_SOURCE_FILES = False
INCLUDE_DERIVED_DATA_PICKLE_FILES = True
# INCLUDE_DERIVED_DATA_JSON_FILES = False


from setuptools import setup # Always prefer setuptools over distutils
# from os import path

# this_folderpath = path.abspath(path.dirname(__file__))

# Get the long description from the README file
#with open(path.join(this_folderpath, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()


package_data_list = []
if INCLUDE_DATA_SOURCE_FILES:
    package_data_list += [
                'DataFiles/Biblelator.gif', 'DataFiles/Biblelator.jpg',
                'DataFiles/BiblelatorLogo.gif', 'DataFiles/BiblelatorLogoSmall.gif',
                ]
if INCLUDE_DERIVED_DATA_PICKLE_FILES:
    package_data_list += [
                # 'DataFiles/DerivedFiles/iso_639_3_Languages_Tables.pickle',
                # 'DataFiles/DerivedFiles/USFM2Markers_Tables.pickle',
                ]
# if INCLUDE_DERIVED_DATA_JSON_FILES:
#     package_data_list += [
#                 'DataFiles/DerivedFiles/iso_639_3_Languages_Tables.json',
#                 'DataFiles/DerivedFiles/USFM2Markers_Tables.json',
#                 ]


setup(
    name='Biblelator',
    version=VERSION,

    packages=['Biblelator',
            'Biblelator.Apps',
            'Biblelator.Dialogs',
            'Biblelator.Helpers',
            'Biblelator.Settings',
            'Biblelator.Windows',
            ],
    package_dir ={ 'Biblelator': 'Biblelator' },
    package_data={ 'Biblelator': package_data_list },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional

    # metadata to display on PyPI
    # This should be your name or the name of the organization which owns the project.
    author="Robert Hunt",
    author_email="Freely.Given.org+Biblelator@gmail.com",

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description="Biblelator — experimental USFM Bible Editor",
    license='GPLv3',

    # This is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    #
    # Often, this is the same as your README, so you can just read it in from
    # that file directly (as we have already done above)
    #
    # This field corresponds to the "Description" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    long_description="""
A USFM Bible editor using the BibleOrgSys library and
Python's tKinter windowing library for simple and easy installation.

NOTE: This packaging is still being tested following massive restructuring,
and is not necessarily fully functional until it is marked as v0.1.0 or higher.
We also have hopes to improve documentation before v0.2.0.

After that point, we also hope to release Docker and Snap versions.

This software has been developed in small chunks of spare time since 2013
(so it's not necessarily well-thought out, and definitely not polished).
However, it was used as my main Bible editor instead of Paratext
for a couple of years.

This package will not reach v1.0.0 until after the BibleOrgSys reaches it.

The API will not become fixed/stable until the v1.0.0 release.

No attempt at all has been made at memory or speed optimisations
and this is not planned until after the release of v1.0.0.

Biblelator is developed and tested on Linux (Ubuntu) but also runs on Windows (although not so well tested).

See https://ubsicap.github.io/usfm/ for more information about USFM.
""",
#    long_description=long_description,

    # Denotes that our long_description is in Markdown; valid values are
    # text/plain, text/x-rst, and text/markdown
    #
    # Optional if long_description is written in reStructuredText (rst) but
    # required for plain-text or Markdown; if unspecified, "applications should
    # attempt to render [the long_description] as text/x-rst; charset=UTF-8 and
    # fall back to text/plain if it is not valid rst" (see link below)
    #
    # This field corresponds to the "Description-Content-Type" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
    long_description_content_type='text/markdown',

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords="Bible editor USFM",

    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url="http://freely-given.org/Software/Biblelator/",

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    #project_urls={  # Optional
    #    'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #    'Funding': 'https://donate.pypi.org',
    #    'Say Thanks!': 'http://saythanks.io/to/example',
    #    'Source': 'https://github.com/pypa/sampleproject/',
    #},
    project_urls={
        #"Bug Tracker": "https://bugs.example.com/HelloWorld/",
        #"Documentation": "https://docs.example.com/HelloWorld/",
        "Source Code": "https://github.com/openscriptures/Biblelator/",
    },

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        # How mature is this project? Common values are
        #   1 - Planning
        #   2 - Pre-Alpha
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Pre-Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Religion',
        'Topic :: Religion',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Operating System :: OS Independent',
    ],

    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. If you
    # do not support Python 2, you can simplify this to '>=3.5' or similar, see
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.7',

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['BibleOrgSys'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    #extras_require={  # Optional
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)

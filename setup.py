from distutils.core import setup, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy

#setup(
#    ext_modules = cythonize("ImgLib/MyLib_Cy.pyx"),
#    include_dirs=[numpy.get_include()]
#)

setup(
	include_dirs = [numpy.get_include()],   
	cmdclass = {'build_ext': build_ext},
    ext_modules=[
        Extension("ImgLib.MyLib_Cy", 
        		 ["ImgLib/MyLib_Cy.pyx"],
        		 extra_compile_args=['-O3'],
        		 #language='c++',
                 include_dirs=[numpy.get_include()]
                ),
    ],
)

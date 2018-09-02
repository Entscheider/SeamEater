# Seameater
Seameater is a python program that implements some algorithm described on [this](http://www.faculty.idc.ac.il/arik/SCWeb/imret/) site and on the paper "Seam Carving for Content-Aware Image Resizing" by Shai Avidan and Ariel Shamir. E.g.

- Remove objects seamlessly in pictures by decreasing the picture size
- Remove objects in the gradient domain (needs a lot of memory)
- Enlarge/Downsize a picture by enlarging/downsizing the background
- Amplify the content of pictures

This application depends on [Numpy](https://www.numpy.org/), [Scipy](https://www.scipy.org/), [imageio](https://imageio.github.io/) and [PyQt4 or PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro). Because it is mainly written in pure Python, be warned: it is not as fast as you may wish. However, some code may be helpful for analysis.

## How to run
Clone this repository and install the dependencies if necessary.
Then go to the source directory and run `python3 main.py`.

It is possible to use a faster seam finding algorithm by compiling the Cython-Extension.
To do that, you have to install [cython](https://github.com/cython/cython), run `python3 setup.py build_ext  --inplace` and restart the application.

## Screenshots
* Enlarge image
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/screenshot_add.png)
* Remove Content
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/Screenshot_remove.png)
* Amplify content
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/screenshot_content_amplification.png)

## License
The code is licensed under GPLv3.

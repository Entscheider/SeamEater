# Seameater
Seameater is a python program implementing some algorithm, which are described on [this](http://www.faculty.idc.ac.il/arik/SCWeb/imret/) site and the paper about Seam Carving. E.g.

- Remove objects seamlessly in picture by decreasing the picture size
- Remove objects in the gradient domain (need a lot of memory)
- Enlarge/Downsize a picture by enlarging/downsizing the background
- Amplify the content of picture

The application depends on Numpy and PyQt4 or PyQt5. Because it is mainly written in pure Python, be warned: it is not as fast as you may wish. However, some code may be helpful for analysis.

## How to run
Clone the repository and install the dependencies if necessary.
Then go to the source directory and run `python3 main.py`.

It is possible to use a faster seam finding algorithm by compiling the Cython-Extension.
To do that, you have to run `python3 setup.py build_ext  --inplace` and restart the application.

## Screenshots
* Enlarge image
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/screenshot_add.png)
* Remove Content
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/Screenshot_remove.png)
* Amplify content
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/screenshot_content_amplification.png)

## License
The code is licensed under GPLv3.

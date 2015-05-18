# Seameater
Seameater is a python program implementing some algorithm, which are described on [this]( ftp://ftp1.idc.ac.il/Arik_shamir/SCweb/imret/index.html) site and the paper about Seam Carving. E.g.

- Remove objects seamlessly in picture by decreasing the picture size
- Remove objects in the gradient domain (need a lot of memory)
- Enlarge/Downsize a picture by enlarging/downsizing the background
- Amplify the content of picture

The application depends on Numpy and PyQt4 or PyQt5. Because it is written in pure Python, be warned: it is not as fast as you may wish. However, some code may be helpful for analysis.

## How to run
Clone the repository and install the dependencies if necessary.
Then go to the source directory and run `python2 main.py`.

## Screenshots
* Enlarge image
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/screenshot_add.png)
* Remove Content
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/Screenshot_remove.png)
* Amplify content
![](https://raw.githubusercontent.com/Entscheider/SeamEater/master/pic/screenshot/screenshot_content_amplification.png)

## License
The code is licenses under GPLv3.

# BrewSpot
Fourth project of Udacity's Full Stack Web Developer Nanodegree.

It consist on a python generated webpage application that allows visitors to find new beers and where to have them. Logged users can submit their own locals and the beers they offer so the visitors can meet them.
<br />
<br />
## How to run the BrewSpot app
--------------
The only requirement is to have **Python 2.7** installed. If you don't have python installed, download the most recent release for 2.7 version on https://www.python.org/downloads/. When you are ready, follow the instructions:
<br />
1. Open terminal
2. Move to the choosen directory. Example:  ```$ cd Desktop```<br />
3. Clone the project repository <br />
```$ git clone https://github.com/gvzqez/BrewSpot```
4. Move to the project vagrant directory <br />
 ```$ cd BrewSpot/vagrant```
5. Install and connect to the VM <br />
```$ vagrant up``` <br />
 ```$ vagrant ssh``` <br />
6. Once inside the VM, move to the app virtual image directory <br />
 ```$ cd /vagrant/src/BrewSpot``` <br />
 7. Create and populate the databse <br />
 ```$ python database_setup.py``` <br />
 ```$ python lotsofbeers.py``` <br />
 8. Execute the application <br />
  ```$ python main.py``` <br />




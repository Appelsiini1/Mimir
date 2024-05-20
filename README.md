 # Mímir
 ![Mímir logo](resource/logoV3.png)
 ## A dynamic programming assignment manager

 This tool is intended to be used for managing large volumes of programming assignments on programming courses. Assignments are imported into the program with a sleek UI. The user can then create assignment sets from the imported assignments. The sets are then exported into a LaTeX file, that can then be turned into a PDF using pdflatex.

 This tool was started as a part of my Master's thesis at LUT University (Finland).

 ## Requirements

 In order to run directly from source, install all dependecies with the install script in the root folder by running
 
 ```
 ./install.sh
 ```
**OR** by installing them individually from `requirements.txt` with
 ```
 pip install -r requirements.txt
 ```

 Start the program by running `main.py`.

 To convert the TeX files the program creates to PDF's, you need to install `pdflatex`. Note that you need to install extra LaTeX packages, like `lastpage`. These should come with the LaTeX Extra. Mímir uses pdflatex via command-line to run it on Windows and normal shell on Linux. In addition, you need to install `pygmentize` for the PDF creation and highlighting to work.
 
 You can install them using these commands on Ubuntu:

 _**NOTE: The install script will also install these, so only use these if not using the install script.**_

 ```
sudo apt install texlive
sudo apt install texlive-latex-extra
sudo apt install python3-pygments
```

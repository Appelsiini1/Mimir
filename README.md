# Mimir
 ![Mímir logo](resource/logoV3.png)
 ## A dynamic programming assignment manager

 This tool is intended to be used for managing large volumes of progrgramming assignments on programming courses. Assignments are imported into the program with a sleek UI. The user can then create assignment sets from the imported assignments. The sets are then exported into a LaTeX file, that can then be turned into a PDF using pdflatex.

 This tool is made as a part of my Master's thesis. 
 **The tool is still under development.**

 ## Requirements

 In order to run directly from source, install dependecies from `requirements.txt` with
 ```
 pip install -r requirements.txt
 ```

 Start the program by running `main.py`.

 To convert the TeX files the program creates to PDF's, you need to install `pdflatex`. Mímir uses WSL
 to run it on Windows and normal shell on Linux. In addition, you need to install `pygmentize` to use highlighting.
 
 You can install them using these commands on Ubuntu:
 ```
sudo apt install texlive
sudo apt install python3-pygments
```
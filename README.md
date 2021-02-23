# ParseCheque

## Installation

1. Install tesseract
```bash
sudo apt update sudo apt install tesseract-ocr
```
2. Install languages
```bash
sudo apt-get install tesseract-ocr-heb tesseract-ocr-eng
wget https://github.com/tesseract-ocr/tessdata/raw/master/script/Hebrew.traineddata
```
and move Hebrew in tesseract-ocr folder
3. Install dependencies 
```bash
pip install -r req.txt
```
## Usage

```bash
python3 main.py "40.jpg" "40.json"
```

## License
[MIT](https://choosealicense.com/licenses/mit/)

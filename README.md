# Forklift Injury Prevention Device

This project acts as an advanced driver assistance system (ADAS) for forklifts. It detects operators, monitors phone usage and provides a small web interface to display warnings in real time.

## Environment Setup

1. **Install Python 3.11**
2. *(Linux only)* install OpenCV dependencies:
   ```bash
   sudo apt-get install python3-opencv
   ```
3. **Create and activate a virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
4. **Install Python requirements**
   ```bash
   pip install -r requirements.txt
   ```
5. **Prepare the model files**
   - Place the YOLOv11 NCNN model under `traning/runs/train/yolov11n_320_V3/weights/`.
   - Alternatively run `python traning/model_ncnn_conversion.py` to convert the model.

To start the system run:
```bash
python main.py
```
This launches the detector and a web interface available at `http://<HOST>:5000`.

## Directory Structure

```
.
├── main.py                     - Application entry point
├── core/
│   └── detector.py             - YOLOv11 NCNN detection wrapper
├── utils/
│   ├── camera_stream.py        - Threaded camera capture class
│   ├── defines.py              - Central configuration values
│   ├── log.py                  - Simple logging helpers
│   └── web_stream.py           - Flask video streaming utilities
├── web/
│   ├── templates/              - HTML templates for the UI
│   └── static/                 - CSS and JavaScript files
├── comm/
│   └── serial_comm.py          - UART communication with the ESP32 board
├── data_preprocessing/
│   ├── dataset_annotate_face.py - Auto label faces in a dataset
│   ├── dataset_balancing.py    - Remove invalid YOLO labels
│   ├── dataset_change_class.py - Remap class IDs in labels
│   ├── dataset_cleaning.py     - Clean dataset and split into sets
│   ├── dataset_count.py        - Count images and labels in a dataset
│   ├── dataset_segregate.py    - Split dataset by class combinations
│   ├── dataset_split.py        - Create train/val/test splits
│   └── dataset_transfer.py     - Copy dataset to a new location
├── traning/
│   ├── create_dataset.py       - Dataset creation helpers
│   ├── model_ncnn_conversion.py - Convert trained model to NCNN format
│   ├── model_training_yolov11n.ipynb - Training notebook
│   └── yolo11n.pt              - Sample weights
├── test_scripts/
│   ├── camera_test.py          - Verify camera connectivity
│   ├── ncnn_model_test.py      - Test detector on an image
│   └── windows_model_test.py   - Webcam test script for Windows
├── test_images/
│   └── sample1.jpg             - Example image for tests
└── forlift_injury_prevention_device_firmware_esp32/
    └── platformio.ini          - ESP32 firmware project
```

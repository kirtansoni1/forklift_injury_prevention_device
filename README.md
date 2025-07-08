# forklift_injury_prevention_device
This device works like ADAS, but for Forklifts

# Steps to setup
1) install python3.11
2) sudo apt install python3-opencv
3) update pip
4) create venv
5) install requirements file
6) run get model script, which will automatically fetch the latest AI model of YOLO11n and create proper dir format
7) Run the entry point

# Directories explanation
yolov11_rpi5_project/
├── main.py                         # Entry point
├── core/
│   └── detector.py                 # YOLOv11 NCNN human detection module
├── utils/
│   ├── camera_stream.py           # Multithreaded camera handling
│   ├── defines.py                 # All constants and magic numbers
|   └── log.py                     # Centralized log file generator
├── web/
│   ├── templates/                 # Flask HTML templates
│   └── static/                    # CSS, JS and images
├── comm/
│   └── serial_comm.py             # Serial communication abstraction (RPI5 ⇆ ESP32-S3)
├── test_script/                   # To quickly test the hardware connection or if any error in hardware 
│   └── camera_test.py             # To test the camera connection and operation
├── models/                        # Store yolov11n.ncnn.param/bin here
├── README.md                      # Project overview & instructions
└── .gitignore                     # Environment & cache exclusions
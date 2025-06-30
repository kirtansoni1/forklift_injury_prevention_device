import cv2
from utils.camera_stream import CameraStream
from core.detector import YOLOv11Detector
from comm.serial_comm import SerialComm
from utils.log import log_info, log_warning, log_error


def main():
    camera = CameraStream().start()
    detector = YOLOv11Detector()
    comm = SerialComm()
    log_info("System initialized. Starting detection loop.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue

            detections = detector.detect_humans(frame)

            for (x1, y1, x2, y2, conf) in detections:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            if detections:
                log_info(f"{len(detections)} human(s) detected.")
                comm.send("human_detected")

            msg = comm.receive()
            if msg:
                log_info(f"Received from ESP32-S3: {msg}")

            cv2.imshow("Human Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        log_error(f"Exception occurred: {e}")
    finally:
        camera.stop()
        comm.close()
        cv2.destroyAllWindows()
        log_info("System shutdown completed.")


if __name__ == "__main__":
    main()

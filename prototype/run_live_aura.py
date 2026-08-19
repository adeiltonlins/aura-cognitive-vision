from __future__ import annotations

import cv2

from openai_perception import OpenAIPerception
from perception_worker import PerceptionWorker


def main() -> None:
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise SystemExit("Não foi possível abrir a câmera.")

    perception = OpenAIPerception()
    worker = PerceptionWorker(perception.analyze)
    worker.start()

    print("AURA LIVE iniciado. Pressione Q para sair.")
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                continue

            worker.submit(frame)
            cv2.imshow("AURA Cognitive Vision", frame)

            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        worker.stop()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

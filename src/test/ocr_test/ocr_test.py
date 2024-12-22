import cv2

from common.ocr import RelatetiveBoxPosition, ocr

position = RelatetiveBoxPosition(0.454, 0.183, 0.547, 0.231)

AUGMENT_NAME_POSITION_TUPLE = (
    (0.2230, 0.5028, 0.3594, 0.5354),
    (0.4344, 0.5028, 0.5723, 0.5326),
    (0.6457, 0.5028, 0.7836, 0.5354),
)


frame = cv2.imread('./img_1.png')
ocr_line_model = ocr
cropped_frame = RelatetiveBoxPosition(*AUGMENT_NAME_POSITION_TUPLE[0]).get_cropped_frame(frame)
# cropped_frame = frame
ocr_result = ocr_line_model(cropped_frame)
ocr_result = ocr_result[0][0][1]
ocr_result = ocr_result.replace('I川', 'III')
ocr_result = ocr_result.replace('ⅡI', 'II')
print(ocr_result)

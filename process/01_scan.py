import compas_rrc as rrc
import os
from undo.production_data import ProductionData
import json
import sys
import cv2
import time

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
file_name = DATA + "/"+"20240912_scan.json"

PRODUCTION_LOG_CONFIG = dict(
    ENABLED=True,                       # Generate a log of received feedback
    OVERWRITE=True,                     # When True, it will create a new log file every time, otherwise, it will append to existing
    CONSOLE_OUTPUT=True,                # When True, it will print received feedback on the console
)

if __name__ == '__main__':

    #open json nd read production data
    if os.path.exists(file_name):
        print('Using production data file: {}'.format(file_name))
        with open(file_name, 'r') as fp:
            production_data = ProductionData.from_data(json.load(fp))
    else:
        print('Cannot find production data file: {}'.format(file_name))
        sys.exit(-1)

    # Create Ros Client
    ros = rrc.RosClient()
    ros.run()

    # Create ABB Client
    abb = rrc.AbbClient(ros, '/rob2')
    print('Connected.')

    cameraNumber = 0
    width, height = 3840, 2160

    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    cap = cv2.VideoCapture()
    cap.open(cameraNumber + 1 + cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

    cap.set(cv2.CAP_PROP_FPS, 30)
    path = os.path.abspath(os.path.join(HERE, '..', 'images/'))
    print(path)
    cnt = 1

    for tim in range(18):

        for i in range(len(production_data.actions)+1):

            ret, frame = cap.read()

            if i != len(production_data.actions):
                action = production_data.actions[i]

                if (action.id-12) % 5 == 1 and action.id > 7:
                    cv2.imwrite(path + '/im_{}.png'.format(cnt), frame)
                    cnt += 1
                abb.send_and_wait(rrc.WaitTime(0.25))

                prefixed_action_class_name = '{}{}'.format("rrc.", action.name)
                instruction_type = eval(prefixed_action_class_name)

                if instruction_type is None:
                    raise Exception('Cannot find implementation for instruction: {}'.format(action.name))
                instruction = instruction_type(**action.parameters)
                abb.send_and_wait(instruction)
                print(instruction)

    # End of Code
    print('Finished')

    # Close client
    ros.close()
    ros.terminate()
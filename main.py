import cv2
import mediapipe as mp
import numpy as np
import PySimpleGUI as sg


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_pose.POSE_CONNECTIONS

print('press q for exit application')

def calculo_angulo(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angulo = np.abs(radians * 180.0 / np.pi)

    if angulo > 180.0:
            angulo = 360 - angulo

    return angulo
def rescale_frame(frame, percent=50):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

def get_mediapipe_path():
    import mediapipe
    mediapipe_path = mediapipe.__path__[0]
    return mediapipe_path



    # captura do video
angulo_min = []
angulo_min_quadril = []
# Abre a janela de seleção de arquivo
sg.theme('DarkBlue')
layout = [[sg.Text('Digite o caminho do arquivo de vídeo:')],
          [sg.Input(key='-FILE-', enable_events=True), sg.FileBrowse()],
          [sg.Button('Iniciar'), sg.Button('Webcam') , sg.Button('Sair')]]

window = sg.Window('Análise de vídeo', layout, size=(450, 150))


#laytou pra escolher entre video agachando ou webcam
while True:
    event, values = window.read()
    if event == 'Iniciar':
        file_path = values['-FILE-']
        # Inicia a captura de vídeo
        cap = cv2.VideoCapture(file_path)
        break
        cv2.imshow('gravacao teste ', image)

    elif event == 'Webcam':
        cap =cv2.VideoCapture(0)
        break

    elif event =='Sair':
        break

    elif event == sg.WIN_CLOSED:
        break








contador = 0
contadorerrado = 0
min_ang = 0
max_ang = 0
min_ang_quadril = 0
max_ang_quadril = 0
stage = None

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if frame is not None:
            frame_ = rescale_frame(frame, percent=75)
        image = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
            # faz a detecçao ( listras )
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # pega as codernadas de cada musculo
        try:
            landmarks = results.pose_landmarks.landmark


            ombro = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            cotovelo = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            pulso = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            quadril = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            joelho = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            tornozelo = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                #calculando os angulos
            angulo = calculo_angulo(ombro, cotovelo, pulso)

            angulo_joelho = calculo_angulo(quadril, joelho , cotovelo)
            angulo_joelho = round(angulo_joelho, 2)

            angulo_quadril = calculo_angulo(ombro, quadril, joelho)
            angulo_quadril= round(angulo_quadril, 2)

            quadril_angulo = 180 - angulo_quadril
            joelho_angulo = 180 - angulo_joelho

            cv2.putText(image, str(angulo_joelho),
                        tuple(np.multiply(joelho, [1500, 800]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )

            cv2.putText(image, str(angulo_quadril),
                        tuple(np.multiply(quadril, [1500, 800]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )



            if angulo_quadril <= 90:
                stage = "up2"
            if angulo_quadril > 120 and stage == 'up2':
                stage = "down2"
                contador += 1
                print(contador)



        except:
            pass

           #funçao da caixa retangular
        cv2.rectangle(image, (20,-60), (220,100), (0,0,0), -1)


            #contador de repetiçoes
        cv2.putText(image, "reps : " + str(contador),
                        (30,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)

            # Hip angle:
        cv2.putText(image, " angulo quadril : " + str(angulo_quadril),
                        (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(image, " angulo joelho : " + str(angulo_joelho),
                        (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        #cv2.putText(image, " errado : " + str(contadorerrado),
                   # (30, 100),
                   #         cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=1),
                                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=1)
                                     )
        #cxfreeze nome_do_arquivo.py --target-dir dist
    # pra instalar app
                #abrir a janela da gravaçao
        cv2.imshow('gravacao teste ', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            print
            cap.release(),
            cap.destroyAllWindows()
        if event == sg.WIN_CLOSED:
            break






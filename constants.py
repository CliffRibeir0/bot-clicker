import os

class Config:
    # pasta com as unidades de medida de referência para comparar com o screenshot_unit
    UNITS_REFERENCE_FOLDER   = r"C:\Python - Projetos\ArquivosColetaAutomatica\unidades_referencia"
    TESSERACT_FOLDER         = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    SCREENSHOTS_FOLDER       = r"C:\Python - Projetos\ArquivosColetaAutomatica\printsOCR"
    #AINDA_MUDAR              = r"C:\Python - Projetos\ArquivosColetaAutomatica\printsOCR\coluna.png"
    IMAGE_COLUNA              = os.path.join(SCREENSHOTS_FOLDER, "coluna.png")

    #  ponto do check do primeiro parâmetro inferior
    NAME_CLICK_POS = (184, 571)

    #  primeira tela: altura entre o segundo check inferior e o primeiro check inferior
    NAME_CLICK_Y_STEP_1 = -53

    #  após a rolar tela: altura entre os checks dos parâmetros, menor do que a altura de NAME_CLICK_Y_STEP_1
    NAME_CLICK_Y_STEP_2  = int((NAME_CLICK_Y_STEP_1 * 0.7407)) #Estava -40

    #  posição do botão "Show Selected"
    SHOW_SELECTED_POS = (473, 621)

    #  posição do botão "Cancel All"
    CANCEL_ALL_POS = (390, 619)

    #  posição do check do parâmetro superior da tela
    CHECK_POS = (182, 198)

    #  ponto em que o scroll começa quando se perde o parâmetro para baixo (deixar em cima da primeira palavra do nome do segundo parâmetro inferior)
    #SCROLL_POS         = (250, 510)

    #  número de parâmetros que cabem na tela
    NUM_INITIAL_PARAMS = 8


    #  posição em que o scroll começa (deixar em cima da primeira palavra do nome do parâmetro superior)
    SCROLL_START = (221, 198)

    #  posição em que o scroll termina
    SCROLL_END         = (SCROLL_START[0], SCROLL_START[1]+(- NAME_CLICK_Y_STEP_1)) # Estava (250, 245) 

    #  posição em que solta o botão do mouse após o scroll terminar
    SCROLL_MID         = (SCROLL_START[0]+50, SCROLL_START[0]+(- NAME_CLICK_Y_STEP_1))  #(300, 245)

    #  posição em que o scroll começa quando perde a posição relativa do parâmetro selecionado (deixar em cima da primeira palavra do nome do parâmetro inferior)
    SCROLL_START_FIND = (224, 570)

    #  posição em que o scroll termina quando perde a posição relativa do parâmetro selecionado (deixar em cima da primeira palavra do nome do segundo parâmetro inferior)
    SCROLL_END_FIND    = (SCROLL_START_FIND[0], (SCROLL_START_FIND[1] - NAME_CLICK_Y_STEP_1))  #(250,510)

    #  região da coluna para pegar todos os checkboxes
    COL_REGION = (160, 177, 40, 413)

    #  região da unidade quando o parâmetro está isolado
    UNIT_REGION = (1073, 174, 132, 47)

     # região do nome do parâmetro com a coluna Range
    NAME_REGION_WITH_RANGE_COLUMN = (200, 175, 614, 47)

    # região do nome do parâmetro sem a coluna Range
    NAME_REGION_WITHOUT_RANGE_COLUMN = (199, 176, 736, 45)

    # região do value do parâmetro com a coluna Range
    VALUE_REGION_WITH_RANGE_COLUMN = (821, 176, 110, 44)

    # região do value do parâmetro sem a coluna Range
    VALUE_REGION_WITHOUT_RANGE_COLUMN = (948, 176, 118, 44)

    # ponto de ancoragem na tela do scanner para ativar a tela
    ANCHOR_CLICK_POS   = (CHECK_POS[0], SHOW_SELECTED_POS[1])#(250, 620)  

    #  Posição de onde é encontrado o nome Range quando há a coluna Range no scanner
    RANGE_COLUMN       = (COL_REGION[0], (COL_REGION[1] - UNIT_REGION[3]), ((UNIT_REGION[0] + UNIT_REGION[2]) - COL_REGION[0]), UNIT_REGION[3])#(936, 140, 134, 32)  

    #  ID de request
    CAN_REQUEST_IDS = [0x7e0]

    #  ID de response
    CAN_RESPONSE_ID = [0x7e8]

    TIMEOUT_SCROLL     = 5.0  #  tempo máximo em que fica procurando a posição relativa do parâmetro selecionado
    SCROLL_DELAY       = 0.5  #  delay do scroll
    Y_LIMIT            = COL_REGION[1] #170  #  coordenada y acima dos parâmetros da tela, detectará quando a lista de parâmetros acabar

    linear_0 = [0x00,0x00,0x00,0x00]  #  lista de valores para testar parâmetros lineares
    linear_1 = [0x7F,0xFF,0xFF,0xFF]  #  lista de valores para testar parâmetros lineares
    linear_2 = [0x80,0x00,0x00,0x00]  #  lista de valores para testar parâmetros lineares
    linear_3 = [0xFF,0xFF,0xFF,0xFF]  #  lista de valores para testar parâmetros lineares
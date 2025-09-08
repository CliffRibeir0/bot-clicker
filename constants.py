import os

class Config:
    # UNITS_REFERENCE_FOLDER   = r"C:\Python - Projetos\ArquivosColetaAutomatica\unidades_referencia"
    # TESSERACT_FOLDER         = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # SCREENSHOTS_FOLDER            = r"C:\Python - Projetos\ArquivosColetaAutomatica\printsOCR"

    UNITS_REFERENCE_FOLDER   = r"C:\Python - Projetos\ArquivosColetaAutomatica\unidades_referencia"
    TESSERACT_FOLDER         = r"C:\Program Files\Tesseract-OCR"
    TESSERACT_FOLDER         = os.path.join(TESSERACT_FOLDER, "tesseract.exe")
    SCREENSHOTS_FOLDER       = r"C:\Python - Projetos\ArquivosColetaAutomatica\prints OCR"
    #AINDA_MUDAR              = r"C:\Python - Projetos\ArquivosColetaAutomatica\printsOCR\coluna.png"
    IMAGE_COLUNA              = os.path.join(SCREENSHOTS_FOLDER, "coluna.png")


    NAME_CLICK_POS       = (180, 570)  # ponto-base para clicar no nome do primeiro parâmetro inferior
    NAME_CLICK_Y_STEP_1  = -54  #  altura entre o check de um parâmetro e outro
    NAME_CLICK_Y_STEP_2  = -40  #  altura entre o check de um parâmetro e outro

    SHOW_SELECTED_POS  = (475, 620)  #  posição do botão "Show Selected"
    CANCEL_ALL_POS     = (390, 620)  #  posição do botão "Cancel All"
    CHECK_POS          = (180, 200)  #  posição do check do parâmetro superior da tela
    SCROLL_POS         = (250, 510)  #

    NUM_INITIAL_PARAMS = 8  #  número de parâmetros que cabem na tela

    SCROLL_START       = (250, 200)  #  posição em que o scroll começa
    SCROLL_END         = (250, 245)  #  posição em que o scroll termina
    SCROLL_MID         = (300, 245)
    SCROLL_START_FIND  = (250, 575)  #  posição em que o scroll começa quando perde a posição relativa do parâmetro selecionado
    SCROLL_END_FIND    = (250, 510)  #  posição em que o scroll termina quando perde a posição relativa do parâmetro selecionado

    COL_REGION         = (159, 173, 40, 415)  #  região da unidade do parâmetro, quando ele está isolado
    UNIT_REGION        = (1080,180,120,35)  #  região da unidade quando o parâmetro está isolado

    NAME_REGION_WITH_RANGE_COLUMN  = (195, 175, 623, 45)  # região do nome do parâmetro com a coluna Range
    NAME_REGION_WITHOUT_RANGE_COLUMN  = (195, 175, 740, 45)  # região do nome do parâmetro sem a coluna Range
    VALUE_REGION_WITH_RANGE_COLUMN = (820, 180, 110, 35)  # região do value do parâmetro com a coluna Range
    VALUE_REGION_WITHOUT_RANGE_COLUMN = (945, 180, 110, 35)  # região do value do parâmetro sem a coluna Range

    CHECK_POS          = (180, 200)

    ANCHOR_CLICK_POS   = (250, 620)  # ponto de ancoragem na tela do scanner para ativar a tela
    RANGE_COLUMN       = (936, 140, 134, 32)  #  Posição de onde é encontrado o nome Range quando há a coluna Range no scanner

    CAN_REQUEST_IDS    = [0x7E0, 0x7DF]  #  ID de request
    CAN_RESPONSE_ID    = [0x7E8]  #  ID de response

    TIMEOUT_SCROLL     = 5.0  #  tempo máximo em que fica procurando a posição relativa do parâmetro selecionado
    SCROLL_DELAY       = 0.5  #  delay do scroll
    Y_LIMIT            = 170  #  coordenada y acima dos parâmetros da tela, detectará quando a lista de parâmetros acabar

    linear_0 = [0x00,0x00,0x00,0x00]  #  lista de valores para testar parâmetros lineares
    linear_1 = [0x7F,0xFF,0xFF,0xFF]  #  lista de valores para testar parâmetros lineares
    linear_2 = [0x80,0x00,0x00,0x00]  #  lista de valores para testar parâmetros lineares
    linear_3 = [0xFF,0xFF,0xFF,0xFF]  #  lista de valores para testar parâmetros lineares
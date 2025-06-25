class GameStyles():
    menu_button_size= (250, 65)
    input_size = (300, 40)
    game_button_size = (160, 160)

    color_O = "blue"
    color_X = "red"
    color_neutral = "black"

    background_style = "background-color: white;"

    menu_title_style = """
            font-size: 25px;
            font-weight: bold;
        """
    
    menu_button_style = """
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                margin-top: 10px;
                border: 3px solid #de8400;
                background-color: #ff9800;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                font-size: 15px;
                font-weight: bold;
                margin-top: 10px;
                border: 3px solid #cd7a00;
                background-color: #f49100;
                color: white;
                border-radius: 5px;
            }
        """
    
    game_label_style = """
            font-size: 50px;
            margin-bottom: 0px;
        """
    
    game_button_style = """
            QPushButton {
                font-size: 50px;
                font-weight: bold;
                border: 2px solid #333;
                background: white;
                color: {color};
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #f6f6f6;
                border-radius: 5px;
                color: {color};
            }
            """
    
    input_style = """
        QLineEdit {
            font-size: 14px;
            padding: 8px;
            border: 2px solid #ff9800;
            border-radius: 6px;
            background: #fff;
            selection-background-color: #ff9800;
            selection-color: white;
        }
        QLineEdit:focus {
            border: 2px solid #de8400;
        }
    """
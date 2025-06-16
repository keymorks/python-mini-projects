class GameStyles():
    background_style = "background-color: white;"

    menu_title_style = """
            font-size: 25px;
            font-weight: bold;
        """
    
    menu_button_style = """
            font-size: 15px;
            font-weight: bold;
            margin-top: 10px;
            border: 3px solid #de8400;
            background-color: #ff9800;
            color: white;
            border-radius: 5px;
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
                background: #e0e0e0;
                border-radius: 5px;
                color: {color};
            }
            """
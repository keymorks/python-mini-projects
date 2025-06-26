class Styles:
    window_style = "background-color: #ffffff;"

    white_button_style = """
        QPushButton {
            background-color: #ffffff;
            color: black;
            border-radius: 10px;
            border: 2px solid #dedede;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:pressed {
            background-color: #f6f6f6;
        }
        """
    
    orange_button_style = """
        QPushButton {
            background-color: #ff8e00;
            color: white;
            border-radius: 10px;
            border: 2px solid #f18600;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:pressed {
            background-color: #f18600;
        }
        """
    
    scroll_area_style = """
        QLabel {
            font-size: 20px; 
            padding-top: 7px;
            background-color: white;
            qproperty-alignment: 'AlignLeft | AlignVCenter';
        }
        QScrollArea { 
            border: none; 
            background-color: white;
            height: 80px;
        }
        QScrollBar:horizontal {
            border: none;
            background: #f0f0f0;
            height: 12px;
            margin: 5px 0px 0px 0px;  /* Отступ снизу */
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #c0c0c0;
            min-width: 30px;
            border-radius: 6px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
        }
        """
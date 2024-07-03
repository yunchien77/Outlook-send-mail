import configparser as cfp

class EmailSender:
    def __init__(self, config_file):
        self.config = cfp.ConfigParser()
        self.config.read(config_file)
        self.sender_email = self.config['EMAIL']['sender_email']
        self.password = self.config['EMAIL']['password']
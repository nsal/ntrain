from webserver import application
import logging

if __name__ == '__main__':
    logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
    application.run()

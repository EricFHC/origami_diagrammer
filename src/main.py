from app.application import Application
import logging

logging.raiseExceptions = False

if __name__ == '__main__':
    app = Application()
    app.load()
    app.mainloop()
import logging, time

class WidgetHandler(logging.StreamHandler):
    def __init__(self, widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widget
        widget.setReadOnly(True)

    def emit(self, record):
        import pdb
        name = "<b>{}</b>".format(record.name)
        s_time = time.gmtime(record.created)
        time_txt = time.strftime("%a, %d %b %Y %H:%M:%S", s_time)

        # Format the level name
        levelname = record.levelname
        if record.levelname=="CRITICAL":
            format = 'color=red style="font-weight:bold" size=5'
        elif record.levelname == "ERROR":
            format = 'color=red style="font-weight:bold"'
        elif record.levelname == "WARNING":
            format = 'style="font-weight:bold"'
        elif record.levelname == "INFO":
            format = ""
            levelname = ""
        elif record.levelname == "DEBUG":
            format = "color=grey"
        else:
            format = "color=blue"
        type = "<font {}>{:10s}</font>".format(format, levelname)

        # Format the message

        if record.levelname == "CRITICAL":
            msg = '<font color=red size=5>{}</font>'.format(record.msg)
        elif record.levelname == "ERROR":
            msg = '<font style="font-weight:bold">{}</font>'.format(record.msg)
        elif record.levelname == "DEBUG":
            msg = '<font color=grey size=3>{}</font>'.format(record.msg)
        else:
            msg = record.msg


        message = "<b>{name}</b> -- <small>({time})</small>  {type}:  {msg}<br>".format(
            name=name, time=time_txt, type=type, msg=msg)
        self.widget.insertHtml(message)

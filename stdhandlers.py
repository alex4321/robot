def text(application,  args):
    text = " ".join(args)
    print("Robot : " + text)
    return False, application.text_to_speech.convert(text)


def set_speech(application, args):
    assert len(args) == 2
    variable, value = args
    assert variable in ["speaker", "emotion", "speed", "lang"]
    setattr(application.text_to_speech, variable, value)
    return False, None

handlers = {
    "text": text,
    "set-speech": set_speech
}
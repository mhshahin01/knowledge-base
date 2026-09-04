def repeat_topic(topic: str, times: int) -> None:
    repeated_topic = (topic + " ") * times
    print(repeated_topic.strip())


repeat_topic("Python", 3)


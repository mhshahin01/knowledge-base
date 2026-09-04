def read_token_count(response):
    try:
        return int(response["tokens"])
    except KeyError:
        return 0
    except (TypeError, ValueError):
        return 0


print(read_token_count({"tokens": "42"}))
print(read_token_count({}))
print(read_token_count({"tokens": "unknown"}))


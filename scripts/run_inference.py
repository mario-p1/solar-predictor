from heliocast.handlers.inference import lambda_handler

if __name__ == "__main__":
    res = lambda_handler({}, {})
    print(res)

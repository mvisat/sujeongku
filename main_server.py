from server import listener

if __name__ == '__main__':
    try:
        listener.listener().serve_forever()
    except KeyboardInterrupt:
        print("Terminated by user")

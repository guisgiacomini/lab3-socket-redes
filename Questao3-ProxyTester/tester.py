import os
import socket
import configparser  # parses INI format (.conf files have [sections] and key=value)
from multiprocessing.dummy import Pool as ThreadPool  # thread-based pool

parser = configparser.ConfigParser()
pool = ThreadPool(10)  # 10 threads running in parallel


def test_socket(cfg_data):
    """Tests if a single server is reachable on port 80"""
    print("Testing: {}, {}".format(
        cfg_data["ip_address"], cfg_data["configfile"]))

    s = socket.socket()  # create a TCP socket

    try:
        s.connect((cfg_data["ip_address"], 80))  # try connecting to port 80
    except Exception as e:
        print("Offline: %s:%d. %s" %  # print error if connection fails
              (cfg_data["ip_address"], 80, e))
    finally:
        s.close()  # always close the socket


def main():
    # Step 1: find all .conf files in configs/ folder
    configs = []
    for (dirpath, subdirs, files) in os.walk("configs"):
        for f in files:
            configs.append(os.path.abspath(os.path.join(dirpath, f)))

    # Step 2: extract the IP address from each config file
    cfg_data = []
    for config in configs:
        parser.read(config)
        # Endpoint format is "IP:port", split to get just the IP
        cfg_data.append(
            {"ip_address": parser["Peer"]["Endpoint"].split(":")[0], "configfile": config})

    # Step 3: test all servers in parallel, then wait for completion
    pool.map(test_socket, cfg_data)
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()

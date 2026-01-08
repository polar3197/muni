from config import GTFSConfig
from gtfs.fetcher import GTFSFetcher

def main():
    config = GTFSConfig()
    fetcher = GTFSFetcher(config)
    v_list = fetcher.fetch_live_vehicles()
    i = 0
    for v in v_list:
        #print(f"route_id: {v['route_id']}\n location: ({v['lat']}, {v['lon']})")
        print(v)
        i += 1
        if i > 10:
            break
    return

if __name__ == "__main__":
    main()
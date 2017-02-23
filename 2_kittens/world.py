class Item(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        for key, val in kwargs.iteritems():
            if key in self.props:
                setattr(self, key, val)
            else:
                raise Exception('Sure? {} {} {}'.format(self.__class__.__name__, key, val))

    def __repr__(self):
        return '<{cls}: {kwargs}>'.format(
            cls=self.__class__.__name__,
            kwargs=self.kwargs,
        )


class Video(Item):
    props = ['id', 'size']
    id = None
    size = None


class Endpoint(Item):
    props = ['id', 'dc_latency', 'caches_count', 'caches_latencies']
    id = None
    dc_latency = None
    caches_count = None
    caches_latencies = None


class Cache(Item):
    props = ['id', 'size', 'stored_videos', 'endpoints']
    id = None
    size = None
    stored_videos = None
    endpoints = None


class Request(Item):
    props = ['id', 'video_id', 'endpoint_id', 'count']
    id = None
    video_id = None
    endpoint_id = None
    count = None


class World(object):
    videos = []
    endpoints = []
    requests = []
    caches = []

    cache_size_mb = videos_count = endpoints_count = caches_count = reqs_count = None


# ============ ALI START =============


    def solve(self):
        pass

# ============ ALI END =============



    @staticmethod
    def from_file(file_obj):
        obj = World()
        line_iter = iter(file_obj)

        counts_line = next(line_iter).strip()

        obj.videos_count, obj.endpoints_count, obj.reqs_count, obj.caches_count, obj.cache_size_mb = map(int, counts_line.split(' '))

        videos_line = next(line_iter).strip()
        obj.videos = (
            Video(id=index, size=int(size_mb))
            for index, size_mb in enumerate(videos_line.split(' '))
        )

        obj.caches = tuple(
            Cache(id=index, size=obj.cache_size_mb, stored_videos={}, endpoints={})
            for index in range(obj.caches_count)
        )

        for endpoint_id in range(obj.endpoints_count):
            endpoint_desc_line = next(line_iter).strip()
            dc_latency, caches_count = map(int, endpoint_desc_line.split(' '))
            endpoint = Endpoint(id=endpoint_id, dc_latency=int(dc_latency), caches_count=int(caches_count), caches_latencies={})
            obj.endpoints.append(endpoint)

            for cache in range(caches_count):
                cache_desc_line = next(line_iter).strip()
                cache_id, latency = map(int, cache_desc_line.split(' '))
                endpoint.caches_latencies[cache_id] = latency
                obj.caches[cache_id].endpoints[endpoint_id] = latency

        for req_id in range(obj.reqs_count):
            endpoint_desc_line = next(line_iter).strip()
            video_id, endpoint_id, count = map(int, endpoint_desc_line.split(' '))
            obj.requests.append(Request(
                id=req_id,
                video_id=video_id,
                endpoint_id=endpoint_id,
                count=count
            ))

        return obj

with open('me_at_the_zoo.in') as file_obj:
    w = World.from_file(file_obj)
    print list(w.videos)

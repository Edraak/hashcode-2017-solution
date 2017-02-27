from __future__ import division

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
    props = ['id', 'size', 'possible_caches']
    id = None
    size = None
    possible_caches = None


class Endpoint(Item):
    props = ['id', 'dc_latency', 'caches_count', 'caches_latencies']
    id = None
    dc_latency = None
    caches_count = None
    caches_latencies = None


class Cache(Item):
    props = ['id', 'size', 'stored_videos', 'endpoints', 'possible_videos']
    id = None
    size = None
    stored_videos = None
    endpoints = None
    possible_videos = None

    def rescore(self, video_id, ep_id, count, video_cache):

        if video_id in self.possible_videos:
            #  score =  (endpoint.dc_latency                       - cache_lat)                          * request.count          * (self.cache_size_mb / video.size)
            old_score = (w.endpoints[ep_id].dc_latency - w.endpoints[ep_id].caches_latencies[self.id]) * count * (w.cache_size_mb / w.videos[video_id].size)
            new_score = (w.endpoints[ep_id].caches_latencies[video_cache.id] - w.endpoints[ep_id].caches_latencies[self.id]) * count * (w.cache_size_mb / w.videos[video_id].size)
            self.possible_videos[video_id][0] -= old_score-new_score


class World(object):
    videos = []
    endpoints = []
    requests = []
    caches = []

    cache_size_mb = videos_count = endpoints_count = caches_count = reqs_count = None


# ============ ALI START =============


    def solve(self):
        pass

    def process_requests(self, line_iter):
        for req_id in range(self.reqs_count):
            endpoint_desc_line = next(line_iter).strip()
            video_id, endpoint_id, count = map(int, endpoint_desc_line.split(' '))
            endpoint = self.endpoints[endpoint_id]
            for cache_id, cache_lat in endpoint.caches_latencies.iteritems():
                video = self.videos[video_id]
                score = (endpoint.dc_latency - cache_lat) * count * (self.cache_size_mb / video.size)
                # print request.video_id, score
                _possible_videos = self.caches[cache_id].possible_videos
                if video.id in self.caches[cache_id].possible_videos:
                    # Increase score
                    _possible_videos[video_id][0] += score
                    _possible_videos[video_id][1][endpoint.id] = count
                else:
                    _possible_videos[video_id] = [score, {endpoint.id: count}]
                    # video.possible_caches[cache_id] = cache_id

    def process_caches(self):
        for cache in self.caches:
            print "processing cache " + str(cache.id)
            _possible_videos = list(cache.possible_videos.items())
            _possible_videos.sort(key=lambda t: t[1][0], reverse=True)
            for video_id, scoreandendpoints in _possible_videos:
                if cache.size - self.videos[video_id].size >= 0:
                    cache.size -= self.videos[video_id].size
                    cache.stored_videos[video_id] = self.videos[video_id]
                    for ep_id, count in scoreandendpoints[1].iteritems():
                        for cache_id, cache_lat in self.endpoints[ep_id].caches_latencies.iteritems():
                            if cache_id != cache.id:
                                self.caches[cache_id].rescore(video_id, ep_id, count, cache)

    def output_result(self, filename):
        with open(filename, 'w') as file_obj:
            file_obj.write(str(len(self.caches)) + "\n")
            for cache in w.caches:
                file_obj.write(str(cache.id) + " ")
                for vid, v in cache.stored_videos.iteritems():
                    file_obj.write(str(vid) + " ")
                file_obj.write("\n")


# ============ ALI END =============



    @staticmethod
    def from_file(file_obj):
        obj = World()
        line_iter = iter(file_obj)

        counts_line = next(line_iter).strip()

        obj.videos_count, obj.endpoints_count, obj.reqs_count, obj.caches_count, obj.cache_size_mb = map(int, counts_line.split(' '))

        videos_line = next(line_iter).strip()
        obj.videos = tuple(
            Video(id=index, size=int(size_mb), possible_caches={})
            for index, size_mb in enumerate(videos_line.split(' '))
        )

        obj.caches = tuple(
            Cache(id=index, size=obj.cache_size_mb, stored_videos={}, endpoints={}, possible_videos={})
            for index in range(obj.caches_count)
        )

        for endpoint_id in range(obj.endpoints_count):
            endpoint_desc_line = next(line_iter).strip()
            dc_latency, caches_count = map(int, endpoint_desc_line.split(' '))
            endpoint = Endpoint(id=endpoint_id, dc_latency=dc_latency, caches_count=caches_count, caches_latencies={})
            obj.endpoints.append(endpoint)

            for cache in range(caches_count):
                cache_desc_line = next(line_iter).strip()
                cache_id, latency = map(int, cache_desc_line.split(' '))
                endpoint.caches_latencies[cache_id] = latency
                obj.caches[cache_id].endpoints[endpoint_id] = latency

        obj.process_requests(line_iter)

        return obj


from sys import argv
filename = argv[1]
with open(filename) as file_obj:
    print 'Start', filename
    w = World.from_file(file_obj)
    # w.process_requests()
    w.process_caches()
    w.output_result(filename.replace('.in', '.out'))
    print 'Done', filename
